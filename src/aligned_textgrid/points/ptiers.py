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
