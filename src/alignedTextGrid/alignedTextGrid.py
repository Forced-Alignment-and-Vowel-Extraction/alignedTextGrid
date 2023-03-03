"""
Module containing AlignedTextGrid class
"""

from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from praatio.data_classes.textgrid import Textgrid
from alignedTextGrid.sequences.sequences import SequenceInterval, Top, Bottom
from alignedTextGrid.sequences.tiers import SequenceTier, RelatedTiers
from typing import Type, Sequence
import numpy as np
import warnings


class AlignedTextGrid:
    """
    """
    def __init__(
        self,
        textgrid: Textgrid = None,
        textgrid_path: str =  None,
        entry_classes: 
            Sequence[Sequence[Type[SequenceInterval]]] |
            Sequence[Type[SequenceInterval]]
              = ((None),)
    ):
        self.entry_classes = entry_classes
        if textgrid:
            self.tg_tiers = self._nestify_tiers(textgrid)
        #self.tier_groups


    def _nestify_tiers(
        self,
        textgrid: Textgrid
    ):
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
        for tier_group, classes in zip(self.tg_tiers, self.entry_classes):
            tier_list = []
            for tier, entry_class in zip(tier_group, classes):
                tier_list.append(SequenceTier(tier, entry_class))
            
