from praatio.utilities.constants import Interval, Point
from praatio.data_classes.interval_tier import IntervalTier
from praatio.data_classes.point_tier import PointTier
from praatio.data_classes.textgrid import Textgrid
from aligned_textgrid.sequences.sequences import SequenceInterval, Top, Bottom
from aligned_textgrid.sequences.tiers import SequenceTier
from aligned_textgrid.points.points import SequencePoint
from aligned_textgrid.mixins.tiermixins import TierMixins, TierGroupMixins
import numpy as np
from typing import Type
import warnings

class SequencePointTier(TierMixins):
    def __init__(self, 
                 tier = PointTier("", [Point(0,"")]), 
                 entry_class = SequencePoint):
        super().__init__()
        if isinstance(tier, PointTier):
            self.entry_list = tier.entries
            self.name = tier.name
        else: 
            self.entry_list = tier
            self.name = entry_class.__name__

        self.entry_class = entry_class
        
        entry_order = np.argsort([x.time for x in self.entry_list])
        self.entry_list = [self.entry_list[idx] for idx in entry_order]
        self.sequence_list = []

        for entry in self.entry_list:
            this_point = self.entry_class(entry)
            self.sequence_list += [this_point]
        self.__set_precedence()

    def __set_precedence(self):
        for idx,seq in enumerate(self.sequence_list):
            self.__set_intier(seq)
            if idx == 0:
                seq.set_initial()
            else:
                seq.set_prev(self.sequence_list[idx-1])
            if idx == len(self.sequence_list)-1:
                seq.set_final()
            else:
                seq.set_fol(self.sequence_list[idx+1])

    def __set_intier(
            self,
            entry
        ):
        """
        Sets the intier attribute of the entry
        """
        entry.intier = self
        entry.tiername = self.name                 

    def __repr__(self):
        return f"Sequence Point tier of {self.entry_class.__name__};"

    @property
    def times(self):
        return np.array(
            [x.time for x in self.sequence_list]
        )
    
    @property
    def labels(self):
        return [x.label for x in self.sequence_list]
    
    @property
    def xmin(self):
        if len(self.sequence_list) > 0:
            return self.sequence_list[0].time
        else:
            return None
    
    @property
    def xmax(self):
        if len(self.sequence_list) > 0:
            return self.sequence_list[-1].time
        else:
            return None
    
    def get_nearest_point(self, time):
        out_idx = np.abs(self.times-time).argmin()
        return out_idx

    def return_tier(self):
        all_points = [entry.return_point() for entry in self.sequence_list]
        point_tier = PointTier(name = self.name, entries=all_points)
        return(point_tier)
    
    def save_as_tg(self, save_path):
        point_tier = self.return_tier()
        out_tg = Textgrid()
        out_tg.addTier(tier = point_tier)
        out_tg.save(save_path, "long_textgrid")

class PointsGroup(TierGroupMixins):
    def __init__(
            self,
            tiers: list[SequencePointTier] = [SequencePointTier()]
    ):
        super().__init__()
        self.tier_list = tiers
    
    def __repr__(self):
        n_tiers = len(self.tier_list)
        classes = [x.__name__ for x in self.entry_classes]
        return f"PointsGroup with {n_tiers} tiers. {repr(classes)}"
    
