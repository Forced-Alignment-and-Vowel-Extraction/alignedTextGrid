from praatio.utilities.constants import Interval, Point
from praatio.data_classes.interval_tier import IntervalTier
from praatio.data_classes.point_tier import PointTier
from praatio.data_classes.textgrid import Textgrid
from aligned_textgrid.sequences.sequences import SequenceInterval, Top, Bottom
from aligned_textgrid.points.points import SequencePoint
import numpy as np
from typing import Type
import warnings

class SequencePointTier:
    def __init__(self, tier, entry_class = SequencePoint):
        if isinstance(tier, PointTier):
            self.entry_list = tier.entries
            self.name = tier.name
        else: 
            self.entry_list = tier
            self.name = entry_class.__name__

        self.entry_class = entry_class

        self.reference_tier = None

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
            entry: SequencePoint
        ):
        """
        Sets the intier attribute of the entry
        """
        entry.intier = self

    ## magic methods
    def __contains__(self,item):
        return item in self.sequence_list
    
    def __getitem__(self, idx):
        return self.sequence_list[idx]
    
    def __len__(self):
        return len(self.sequence_list)
    
    def __iter__(self):
        self._idx = 0
        return self
    
    def __next__(self):
        if self._idx < len(self.sequence_list):
            out = self.sequence_list[self._idx]
            self._idx += 1
            return(out)
        raise StopIteration

    def __repr__(self):
        return f"Sequence Point tier of {self.entry_class.__name__};"
    
    ## properties

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
    
    def return_tier(self):
        all_points = [entry.return_point() for entry in self.sequence_list]
        point_tier = PointTier(name = self.name, entries=all_points)
        return(point_tier)
    
    def save_as_tg(self, save_path):
        point_tier = self.return_tier()
        out_tg = Textgrid()
        out_tg.addTier(tier = point_tier)
        out_tg.save(save_path, "long_textgrid")        