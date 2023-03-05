"""
Module containing AlignedTextGrid class
"""

from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from praatio.data_classes.textgrid import Textgrid
from praatio.textgrid import openTextgrid
from alignedTextGrid.sequences.sequences import SequenceInterval, Top, Bottom
from alignedTextGrid.sequences.tiers import SequenceTier, RelatedTiers
from typing import Type, Sequence, Literal
import numpy as np
import warnings


class AlignedTextGrid:
    """_An aligned Textgrid_

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
        tier_groups (list[RelatedTiers]):
            a list of `RelatedTiers`
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
            self.tg_tiers = self._nestify_tiers(textgrid)
        elif textgrid_path:
            tg = openTextgrid(
                fnFullPath=textgrid_path, 
                includeEmptyIntervals=True
            )
            self.tg_tiers = self._nestify_tiers(tg)

        self.tier_groups = self._relate_tiers()
    
    def __contains__(self, item):
        return item in self.tier_groups
    
    def __getitem__(self, idx):
        return self.tier_groups[idx]
        
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
        n_tiers = [len(x) for x in self.tier_groups]
        entry_classes = [[x.__name__ for x in y] for y in self.entry_classes]
        return f"AlignedTextGrid with {n_groups} groups, each with {repr(n_tiers)} tiers. {repr(entry_classes)}"

    def _nestify_tiers(
        self,
        textgrid: Textgrid
    ):
        """_private method to nestify tiers_

        Takes a flat list of tiers and nests them according to 
        the nesting, or implied nesting, of `self.entry_classes`

        Args:
            textgrid (Textgrid): _description_

        Returns:
            (list[IntervalTier]): _description_
        """
        tier_idx = 0
        tier_list = []
       
        if not type(self.entry_classes[0]) in [tuple, list]:
            extension = len(textgrid.tiers) // len(self.entry_classes)
            self.entry_classes = [self.entry_classes] * extension
        elif len(self.entry_classes) == 1:
            extension = len(textgrid.tiers) // len(self.entry_classes[0])
            self.entry_classes = [self.entry_classes[0]] * extension

        for idx, class_tup in enumerate(self.entry_classes):
            tier_list.append([])
            for jdx, classes in enumerate(class_tup):
                tier_list[idx].append(textgrid.tiers[tier_idx])
                tier_idx += 1
        return tier_list

    def _relate_tiers(self):
        """_Private method_

        creates RelatedTier objects for each set of
        nested IntervalTier and entry class

        Returns:
            (list[RelatedTiers]): _description_
        """
        tier_groups = []
        for tier_group, classes in zip(self.tg_tiers, self.entry_classes):
            tier_list = []
            for tier, entry_class in zip(tier_group, classes):
                tier_list.append(SequenceTier(tier, entry_class))
            tier_groups.append(RelatedTiers(tier_list))
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

    def return_textgrid(self) -> Textgrid:
        """_Convert this `AlignedTextGrid` to a `praatio` `Textgrid`_
        
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
        """_Saves the current AlignedTextGrid_

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