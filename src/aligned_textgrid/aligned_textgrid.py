"""
Module containing AlignedTextGrid class
"""

from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from praatio.data_classes.textgrid import Textgrid
from praatio.textgrid import openTextgrid
from aligned_textgrid.sequences.sequences import SequenceInterval, Top, Bottom
from aligned_textgrid.points.points import SequencePoint
from aligned_textgrid.sequences.tiers import SequenceTier, TierGroup
from aligned_textgrid.points.tiers import SequencePointTier, PointsGroup
from aligned_textgrid.mixins.within import WithinMixins
from aligned_textgrid.custom_classes import custom_classes, clone_class, get_class_hierarchy
from typing import Type, Sequence, Literal
from copy import copy
import numpy as np
from collections.abc import Sequence
import warnings


class AlignedTextGrid(Sequence, WithinMixins):
    """An aligned Textgrid

    Args:
        textgrid (Textgrid, optional): A `praatio` TextGrid
        textgrid_path (str, optional): A path to a TextGrid file to be 
            read in with `praatio.textgrid.openTextgrid`
        entry_classes (Sequence[Sequence[Type[SequenceInterval]]] | Sequence[Type[SequenceInterval]], optional): 
            If a single list of `SequenceInterval` subclasses is given, they will be
            repeated as many times as necessary to assign a class to every tier. 
            So if there are three speakers, each with a word and phone tier, 
            `[Word, Phone]` will process them each into a tier group.

            If your TextGrids are more complex, provide a nested list with the 
            class for each tier within each tier group. Say, if only the first speaker
            had both a word and phone tier, and the remaining two had only a word tier,
            `[[Word, Phone], [Word], [Word]]`
    
    Attributes:
        entry_classes (list[Sequence[Type[SequenceInterval]]] | list[]): 
            The entry classes for each tier within a tier group.
        tier_groups (list[TierGroup] | list[]):
            A list of `TierGroup` or an empty list.
        tier_names (list[str]):
            A list of names for tiers in tier_groups.
        xmax (float):
            Maximum time
        xmin (float):
            Minimum time
        [] :
            indexable            
    """

    def __init__(
        self,
        textgrid: Textgrid = None,
        textgrid_path: str =  None,
        entry_classes: 
            Sequence[Sequence[Type[SequenceInterval]]] |
            Sequence[Type[SequenceInterval]]
              = [SequenceInterval]
    ):
        self.entry_classes = self._reclone_classes(entry_classes)
        if textgrid:
            self.tg_tiers, self.entry_classes = self._nestify_tiers(textgrid, self.entry_classes)
        elif textgrid_path:
            tg = openTextgrid(
                fnFullPath=textgrid_path, 
                includeEmptyIntervals=True,
                duplicateNamesMode='rename'
            )
            self.tg_tiers, self.entry_classes = self._nestify_tiers(tg, self.entry_classes)
        else:
            warnings.warn('Initializing an empty AlignedTextGrid')
            self._init_empty()
            return

        self.tier_groups = self._relate_tiers()
        self.contains = self.tier_groups
        for tgr in self.tier_groups:
            tgr.within = self
        self.entry_classes = [[tier.entry_class for tier in tg] for tg in self.tier_groups]
        self._set_group_names()
        
    def __getitem__(
            self, 
            idx: int | list
            ):
        if type(idx) is int:
            return self.tier_groups[idx]
        if len(idx) != len(self):
            raise IndexError("Index list and list of tier groups are of different sizes.")
        if type(idx) is list:
            if len(idx) == 0:
                raise IndexError("List of indexes is empty.")
            out_list = []
            for x, tier in zip(idx, self.tier_groups):
                out_list.append(tier[x])
            return(out_list)
        
    def __len__(self):
        return len(self.tier_groups)

    def __repr__(self):
        n_groups = len(self.tier_groups)
        group_names = [x.name for x in self.tier_groups]
        n_tiers = [len(x) for x in self.tier_groups]
        entry_classes = [[x.__name__ for x in y] for y in self.entry_classes]
        return f"AlignedTextGrid with {n_groups} groups named {repr(group_names)} "\
               f"each with {repr(n_tiers)} tiers. {repr(entry_classes)}"
    
    def __setstate__(self, d):
        self.__dict__ = d

    def _extend_classes(
            self, 
            tg: Textgrid, 
            entry_classes
        ):
        """summary

        Args:
            tg (_type_): _description_
            entry_classes (_type_): _description_
        """

        ntiers = len(tg.tiers)
        if not type(entry_classes[0]) in [list, tuple]:
            class_supers = [c.superset_class for c in entry_classes]
            try:
                top_idxes = [i for i,c in enumerate(class_supers) if issubclass(c, Top)]
            except ValueError:
                top_idxes = []

        if type(entry_classes[0]) in [list, tuple]:
            return entry_classes
        
        if len(entry_classes) == 1:
            extension = len(tg.tiers) // len(entry_classes)
            entry_classes = [entry_classes] * extension
            return entry_classes
        if len(top_idxes) <= 1:
            extension = len(tg.tiers) // len(entry_classes)
            entry_classes = [entry_classes] * extension
            return entry_classes
        
        return entry_classes

    def _reclone_classes(
            self, 
            entry_classes:list[SequenceInterval|SequencePoint]|list[list[SequenceInterval|SequencePoint]]
            ) -> list[SequenceInterval|SequencePoint]|list[list[SequenceInterval|SequencePoint]]:
        
        flat_classes = entry_classes
        if type(entry_classes[0]) is list:
            flat_classes = [c for tg in entry_classes for c in tg]
        
        unique_classes = list(set(flat_classes))

        points = [c for c in unique_classes if issubclass(c, SequencePoint)]
        tops = [
            c 
            for c in unique_classes 
            if issubclass(c, SequenceInterval)
            if issubclass(c.superset_class, Top)
        ]

        points_clone = [clone_class(p) for p  in points]
        tops_clone = [clone_class(t) for t in tops]
        full_seq_clone = []
        for tclone in tops_clone:
            full_seq_clone += get_class_hierarchy(tclone, [])

        full_clone = points_clone + full_seq_clone

        if type(entry_classes[0]) is list:
            new_entry_classes = [
                self._swap_classes(tg_classes, full_clone)
                for tg_classes in entry_classes
            ]
        else:
            new_entry_classes = self._swap_classes(entry_classes, full_clone)

        return new_entry_classes

    def _swap_classes(
            self, 
            orig_classes: list[SequenceInterval]|list[SequencePoint], 
            new_classes: list[SequenceInterval,SequencePoint]
        )->list[SequenceInterval]|list[SequencePoint]:
        new_classes_names = [c.__name__ for c in new_classes]
        orig_classes_names = [c.__name__ for c in orig_classes]

        new_idx = [new_classes_names.index(on) for on in orig_classes_names]

        out_classes = [new_classes[i] for i in new_idx]
        return out_classes


    def _init_empty(self):
        self.tier_groups = []
        self.contains = self.tier_groups
        self.entry_classes = []
        self.tg_tiers = None
    
    def _nestify_tiers(
        self,
        textgrid: Textgrid,
        entry_classes: list
    ):
        """_private method to nestify tiers_

        Takes a flat list of tiers and nests them according to 
        the nesting, or implied nesting, of `self.entry_classes`

        Args:
            textgrid (Textgrid): _description_
            entry_classes (list[SequenceInterval]): _description_

        Returns:
            (list[IntervalTier]): _description_
        """ 

        tier_list = []

        entry_classes = self._extend_classes(textgrid, entry_classes)
        if type(entry_classes[0]) in [list, tuple]:
            tier_idx = 0
            for idx, class_tup in enumerate(entry_classes):
                tier_list.append([])
                for jdx, classes in enumerate(class_tup):
                    tier_list[idx].append(textgrid.tiers[tier_idx])
                    tier_idx += 1
            return tier_list, entry_classes
        
        super_classes = [c.superset_class for c in entry_classes]
        top_idxes = [i for i,c in enumerate(super_classes) if issubclass(c, Top)]
        point_idxes = [i for i,c in enumerate(entry_classes) if issubclass(c, SequencePoint)]

        if len(top_idxes) <= 1:
            return [textgrid.tiers], [entry_classes]
        
        ## Nestifying hierarchywise
        entry_list = []
        for top_idx in top_idxes:
            this_tierlist = []
            this_entrylist = []

            this_tierlist.append(textgrid.tiers[top_idx])
            this_entrylist.append(entry_classes[top_idx])

            done = False
            while not done:
                curr = this_entrylist[-1]
                if issubclass(curr.subset_class, Bottom):
                    done = True
                    break

                try:
                    next_idx = entry_classes.index(curr.subset_class)
                except ValueError:
                    done = True
                    break

                this_tierlist.append(textgrid.tiers[next_idx])
                this_entrylist.append(entry_classes[next_idx])

            tier_list.append(this_tierlist)
            entry_list.append(this_entrylist)
        
        return tier_list, entry_list

    def _relate_tiers(self):
        """_Private method_

        creates RelatedTier objects for each set of
        nested IntervalTier and entry class

        Returns:
            (list[TierGroup]): _description_
        """

        tier_groups = []

        for tier_group, classes in zip(self.tg_tiers, self.entry_classes):
            sequence_tier_list = []
            point_tier_list = []
            for tier, entry_class in zip(tier_group, classes):
                if issubclass(entry_class, SequencePoint):
                    point_tier_list.append(SequencePointTier(tier, entry_class))
                if issubclass(entry_class, SequenceInterval):
                    sequence_tier_list.append(SequenceTier(tier, entry_class))
            if len(sequence_tier_list) > 0:
                tier_groups.append(TierGroup(sequence_tier_list))
            if len(point_tier_list) > 0:
                tier_groups.append(PointsGroup(point_tier_list))   
        return tier_groups
    
    def _set_group_names(self):
        tier_group_names = [x.name for x in self.tier_groups]
        duplicate_names = [
            name 
            for name in tier_group_names 
            if tier_group_names.count(name) > 1
        ]

        if len(duplicate_names) > 0:
            unique_dup = set(duplicate_names)
            warnings.warn(
                (
                    f"Some TierGroups had duplicate names, {unique_dup}. "
                    "Named accessors for TierGroups unavailable."
                )
            )
            return
        
        for idx, name in enumerate(tier_group_names):
            setattr(self, name, self.tier_groups[idx])

    @property
    def tier_names(self):
        if len(self) == 0:
            raise ValueError('No tier names in an empty TextGrid.')
        return [x.tier_names for x in self.tier_groups]

    @property
    def xmin(self):
        if len(self) == 0:
            raise ValueError('No minimum time for empty TextGrid.')
        return np.array([tgroup.xmin for tgroup in self.tier_groups]).min()

    @property
    def xmax(self):
        if len(self) == 0:
            raise ValueError('No maximum time for empty TextGrid.')
        return np.array([tgroup.xmax for tgroup in self.tier_groups]).max()
    
    def interleave_class(
            self, 
            name:str,
            above:Type[SequenceInterval]|str = None,
            below:Type[SequenceInterval]|str = None,
            timing_from: Literal["above", "below"] = "below",
            copy_labels: bool = True
        ):
        """Interleave a new entry class.

        You can set either `above` or `below`, but not both.

        Args:
            name (str): 
                Name of the new class
            above (Type[SequenceInterval]|str, optional): 
                Which entry class to interleave above.
            below (Type[SequenceInterval]|str, optional): 
                Which entry class to interleave below.
            timing_from (Literal['above', 'below'], optional): 
                Which tier to draw timing from. Defaults to "below".
            copy_labels (bool):
                Whether or not to copy labels from the tier providing
                timing information. Defaults to True.

        Examples:
            ```{python}
            from aligned_textgrid import AlignedTextGrid, Word, Phone

            atg = AlignedTextGrid(
                textgrid_path = "../usage/resources/josef-fruehwald_speaker.TextGrid",
                entry_classes = [Word, Phone]
            )
            print(atg)
            ```

            ```{python}
            atg.interleave_class(
                name = "Syllable",
                above = "Phone",
                timing_from = "below",
                copy_labels = True
            )
            print(atg)
            ```
        

        """

        if above and below:
            raise ValueError("Only one of above or below may be specified")
        if not (above or below):
            raise ValueError("Either above or below must be specified")
        if not name:
            raise ValueError("name must be specified")
        
        new_class = custom_classes([name])[0]

        if type(above) is type:
            above = above.__name__
        
        if type(below) is type:
            below = below.__name__

        if above:
            above = self.get_class_by_name(above)
            up_class = copy(above.superset_class)
            down_class = above
            specified_class = above

        if below:
            below = self.get_class_by_name(below)
            up_class = below
            down_class = copy(below.subset_class)
            specified_class = below

        if timing_from == "below":
            copy_class = down_class
        elif timing_from == "above":
            copy_class = up_class
        else:
            raise ValueError(
                f"{timing_from} is not a valid entry for timing_from. "\
                "Must be either 'above' or 'below'."
            )

        new_class.set_superset_class(up_class)
        new_class.set_subset_class(down_class)
        
        new_tiergoups = []
        new_entry_classes = []

        for tg in self.tier_groups:
            if not specified_class in tg.entry_classes:
                new_tiergoups.append(tg)
                new_entry_classes.append(tg.entry_classes)
            else:
                copy_tier = [tier for tier in tg if tier.entry_class is copy_class][0]
                new_tier = SequenceTier(
                    [seq.return_interval() for seq in copy_tier],
                    entry_class = new_class
                )
                if not copy_labels:
                    for seq in new_tier:
                        seq.label = ""
                
                orig_entry_classes = tg.entry_classes
                tier_list = tg.tier_list
                if not down_class in orig_entry_classes:
                    orig_entry_classes.append(down_class)
                
                insert_index = orig_entry_classes.index(down_class)
                tier_list.insert(insert_index, new_tier)
                
                for tier in tier_list:
                    tier.superset_class = tier.entry_class.superset_class
                    tier.subset_class = tier.entry_class.subset_class

                new_tg = TierGroup(tier_list)
                new_tg.name = tg.name
                new_tiergoups.append(new_tg)
                new_entry_classes.append(new_tg.entry_classes)

        self.tier_groups = new_tiergoups
        self.entry_classes = new_entry_classes
        for tgr in self.tier_groups:
            tgr.within = self
        self.contains = self.tier_groups

    def pop_class(
            self, 
            name: Type[SequenceInterval]|str
        ):
        """Pop a class from an AlignedTextGrid

        Remove a class of tiers from an AlignedTextGrid

        Args:
            name (Type[SequenceInterval] | str):
                The tier class to remove.

        Examples:
            ```{python}
            from aligned_textgrid import AlignedTextGrid, custom_classes

            atg = AlignedTextGrid(
                textgrid_path = "../usage/resources/spritely.TextGrid",
                entry_classes = custom_classes([
                    "PrWord",
                    "Foot",
                    "Syl",
                    "OnsetRime",
                    "SylPart",
                    "Phone"
                ])
            )
            print(atg)
            ```

            ```{python}
            atg.pop_class("SylPart")
            print(atg)
            ```
        """

        if type(name) is type:
            name = name.__name__

        new_tier_groups = []
        for tg in self.tier_groups:
            entry_classes = [t.entry_class.__name__ for t in tg]

            if not name in entry_classes:
                new_tier_groups.append(tg)
                continue
            
            if name in entry_classes and len(entry_classes) == 1:
                warnings.warn(
                    (
                        f"TierGroup {tg.name} contained only {name} tier "
                        "so it was removed."
                    )
                )
                continue

            pop_tier, = [t for t in tg if t.entry_class.__name__ == name]
            keep_tiers = [t for t in tg if t.entry_class.__name__ != name]

            pop_tier_super = pop_tier.entry_class.superset_class
            pop_tier_sub = pop_tier.entry_class.subset_class
            
            if not isinstance(pop_tier_super, Top):
                pop_tier_super.set_subset_class(pop_tier_sub)

            if not isinstance(pop_tier_sub, Bottom):
                pop_tier_sub.set_superset_class(pop_tier_super)

            for tier in keep_tiers:
                tier.superset_class = tier.entry_class.superset_class
                tier.subset_class = tier.entry_class.subset_class
            new_tg = TierGroup(keep_tiers)
            for seq in new_tg[-1]:
                seq.subset_list = []
                seq.contains = []
            new_tg.name = tg.name
            new_tier_groups.append(new_tg)
        
        self.tier_groups = new_tier_groups
        new_entry_classes = [tg.entry_classes for tg in self.tier_groups]
        self.entry_classes = new_entry_classes
        for tgr in self.tier_groups:
            tgr.within = self
        self.contains = self.tier_groups            
            
    def get_class_by_name(
            self, 
            class_name: str
    )->SequenceInterval|list[SequenceInterval]|None:
        """Get an entry class by name

        Args:
            class_name (str): The requested entry class

        Returns:
            (SequenceInterval|list[SequenceInterval]|None): 
                The requested entry class(es), if any
        """

        flat_class = [
            c for tg in self.entry_classes for c in tg
        ]
        unique_classes = set(flat_class)
        target_classes = [
            x 
            for x in unique_classes 
            if x.__name__ == class_name
        ]

        if len(target_classes) == 1:
            return target_classes[0]
        
        if len(target_classes) > 1:
            warnings.warn(f"Multiple entry classes matched {class_name}.")
            return target_classes

        if len(target_classes) < 1:
            warnings.warn(f"No entry classes named {class_name}.")
            return

    def get_intervals_at_time(
            self, 
            time: float
        ) -> list[list[int]]:
        """Get interval indices at time
        
        Returns a nested list of intervals at `time` for each tier.
        
        Args:
            time (float): time

        Returns:
            (list[list[int]]): a nested list of interval indices.
        """
        return [tgroup.get_intervals_at_time(time) for tgroup in self.tier_groups]

    def return_textgrid(self) -> Textgrid:
        """Convert this `AlignedTextGrid` to a `praatio` `Textgrid`
        
        Returns the current object as a `praatio.data_classes.textgrid.Textgrid`.
        Useful for saving.

        Returns:
            (praatio.data_classes.textgrid.Textgrid):
                A `praatio` `Textgrid`
        """
        out_tg = Textgrid()
        for group in self.tier_groups:
            for tier in group:
                out_tg.addTier(tier = tier.return_tier())
        return out_tg

    def save_textgrid(
            self, 
            save_path: str,
            format : Literal[
                "short_textgrid", 
                "long_textgrid", 
                "json", 
                "textgrid_json"
                ] 
            = "long_textgrid"
        ):
        """Saves the current AlignedTextGrid

        Uses the `praatio.data_classes.textgrid.Textgrid.save()` method.

        Args:
            save_path (str): path for saving the textgrid
            format (Literal["short_textgrid", "long_textgrid", "json", "textgrid_json"], optional): 
                Save format.
        """
        out_tg = self.return_textgrid()
        out_tg.save(
            fn = save_path,
            format = format,
            includeBlankSpaces = True
        )

