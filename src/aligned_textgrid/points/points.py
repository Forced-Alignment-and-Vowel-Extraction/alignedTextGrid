from praatio.utilities.constants import Point
from aligned_textgrid.mixins.mixins import PrecedenceMixins, TierMixins
from aligned_textgrid.sequences.tiers import SequenceTier
from aligned_textgrid.sequences.sequences import SequenceInterval
import warnings
import numpy as np

class  SequencePoint(PrecedenceMixins, TierMixins):
    def __init__(
            self,
            Point
        ):
        super().__init__()
        if not Point:
            Point = Point(0, 0)
        
        self.time = Point.time
        self.label = Point.label

        self.intier = None
        self.tiername = None
        self.pointspool = None
        self.fol = None
        self.prev = None
        self.reference_tier = None

    def __repr__(self) -> str:
        out_string = f"Class {type(self).__name__}, label: {self.label}"
        return out_string
    
    def __contains__(self, item):
        warnings.warn("`in` is not a valid operator for a SequncePoint")
        return None
    
    def __getitem__(self, idex):
        warnings.warn("Indexing is not valid for a SequencePoint")
        return None    
    
    ## Properties
    @property
    def fol_distance(self):
        if self.fol and self.fol.time:
            return self.fol.time - self.time
        
        if self.fol and not self.fol.time:
            warnings.warn("Final point")
            return None

        if not self.fol:
            warnings.warn("Folowing point undefined")
            return None
        
    @property
    def prev_distance(self):
        if self.prev and self.prev.time:
            return self.prev.time - self.time
        
        if self.prev and not self.prev.time:
            warnings.warn("initial point")
            return None

        if not self.prev:
            warnings.warn("previous point undefined")
            return None        

    ## methods
    def distance_from(self, entry):
        if isinstance(entry, SequencePoint):
            return self.time - entry.time
        
        if isinstance(entry, SequenceInterval):
            entry_times = np.array([entry.start, entry.end])
            return self.time - entry_times

    # def get_interval_index_at_time(self, tier = None):
    #     if tier and isinstance(tier, SequenceTier)
    #         int_idx = tier.get_interal_at_time(self.time)
    #         return int_idx
    #
    # def get_interval_at_point(self, tier=None):
    