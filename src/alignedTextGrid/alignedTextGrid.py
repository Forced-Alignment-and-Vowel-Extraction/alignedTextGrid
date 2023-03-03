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
    """
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
        tier_groups = []
        for tier_group, classes in zip(self.tg_tiers, self.entry_classes):
            tier_list = []
            for tier, entry_class in zip(tier_group, classes):
                tier_list.append(SequenceTier(tier, entry_class))
            tier_groups.append(RelatedTiers(tier_list))
        return tier_groups
    
    def return_textgrid(self):
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
        out_tg = self.return_textgrid()
        out_tg.save(
            fn = save_path,
            format = format,
            includeBlankSpaces = True
        )