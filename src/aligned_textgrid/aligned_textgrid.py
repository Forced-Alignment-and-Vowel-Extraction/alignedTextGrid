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
from aligned_textgrid.custom_classes import custom_classes
from typing import Type, Sequence, Literal
from copy import copy
import numpy as np
import warnings


class AlignedTextGrid(WithinMixins):
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
        entry_classes (list[Sequence[Type[SequenceInterval]]]): 
            The entry classes for each tier within a tier group.
        tier_groups (list[TierGroup]):
            a list of `TierGroup`
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
        self.entry_classes = entry_classes
        if textgrid:
            self.tg_tiers, self.entry_classes = self._nestify_tiers(textgrid, entry_classes)
        elif textgrid_path:
            tg = openTextgrid(
                fnFullPath=textgrid_path, 
                includeEmptyIntervals=True
            )
            self.tg_tiers, self.entry_classes = self._nestify_tiers(tg, entry_classes)

        self.tier_groups = self._relate_tiers()
        self.contains = self.tier_groups
        self.entry_classes = [[tier.entry_class for tier in tg] for tg in self.tier_groups]

    
    def __contains__(self, item):
        return item in self.tier_groups
    
    def __getitem__(
            self, 
            idx: int | list
            ):
        if type(idx) is int:
            return self.tier_groups[idx]
        if len(idx) != len(self):
            raise Exception("Attempt to index with incompatible list")
        if type(idx) is list:
            out_list = []
            for x, tier in zip(idx, self.tier_groups):
                out_list.append(tier[x])
            return(out_list)
        
    def __iter__(self):
        self._idx = 0
        return self

    def __len__(self):
        return len(self.tier_groups)

    def __next__(self):
        if self._idx < len(self.tier_groups):
            out = self.tier_groups[self._idx]
            self._idx += 1
            return(out)
        raise StopIteration
    
    def __repr__(self):
        n_groups = len(self.tier_groups)
        group_names = [x.name for x in self.tier_groups]
        n_tiers = [len(x) for x in self.tier_groups]
        entry_classes = [[x.__name__ for x in y] for y in self.entry_classes]
        return f"AlignedTextGrid with {n_groups} groups named {repr(group_names)} "\
               f"each with {repr(n_tiers)} tiers. {repr(entry_classes)}"
    
    def __getattr__(
            self, 
            name: str
        ):
        tier_group_names = [x.name for x in self.tier_groups]
        match_list = [x  for x in tier_group_names if x == name]

        if len(match_list) == 1:
            match_idx = tier_group_names.index(name)
            self.__setattr__(name, self.tier_groups[match_idx])
            return self.tier_groups[match_idx]
        
        if len(match_list) > 1:
            raise AttributeError(f"This AlignedTextGrid has multiple TierGroups called {name}")
        
        if len(match_list) < 1:
            raise AttributeError(f"This AlignedTextGrid has no attribute {name}")    
    def index(
            self,
            group: TierGroup|PointsGroup
        )->int:
        return self.tier_groups.index(group)
    
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
    
    @property
    def tier_names(self):
        return [x.tier_names for x in self.tier_groups]

    @property
    def xmin(self):
        return np.array([tgroup.xmin for tgroup in self.tier_groups]).min()

    @property
    def xmax(self):
        return np.array([tgroup.xmax for tgroup in self.tier_groups]).max()
    
    def interleave_class(
            self, 
            name:str,
            above:SequenceInterval|str = None,
            below:SequenceInterval|str = None,
            timing_from: Literal["above", "below"] = "below",
            copy_labels: bool = True
        ):
        """Interleave a new entry class.

        Args:
            name (str): 
                Name of the new class
            above (SequenceInterval|str, optional): 
                Which entry class to interleave above.
            below (SequenceInterval|str, optional): 
                Which entry class to interleave below.
            timing_from (Literal['above', 'below'], optional): 
                Which tier to draw timing from. Defaults to "below".
            copy_labels (bool):
                Whether or not to copy labels from the tier providing
                timing information. Defaults to True.

        
        You can set either `above` or `below`, but not both.
        """

        if above and below:
            raise ValueError("Only one of above or below may be specified")
        if not (above or below):
            raise ValueError("Either above or below must be specified")
        if not name:
            raise ValueError("name must be specified")
        
        new_class = custom_classes([name])[0]

        if type(above) is str:
            above = self.get_class_by_name(above)

        if type(below) is str:
            below = self.get_class_by_name(below)

        if above:
            up_class = copy(above.superset_class)
            down_class = above
            specified_class = above

        if below:
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

