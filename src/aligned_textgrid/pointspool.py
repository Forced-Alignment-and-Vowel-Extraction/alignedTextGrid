from aligned_textgrid.points.ptiers import SequencePointTier
import numpy as np

class PointsPool:
    def __init__(self, tiers):
        self.entry_list = []
        if type(tiers) is list:
           self.entry_list = [entry for tier in tiers 
                         for entry in tier.sequence_list]
        if type(tiers) is SequencePointTier:
            self.entry_list = tiers.sequence_list
        
        self.__sort_pointspool()
        self.__set_pointspool()

    def __sort_pointspool(self):
        entry_order = np.argsort([x.time for x in self.entry_list])
        self.entry_list = [self.entry_list[idx] for idx in entry_order]
    
    def __set_pointspool(self):
        for entry in self.entry_list:
            entry.pointspool = self