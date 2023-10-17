from praatio.utilities.constants import Point
from aligned_textgrid.mixins.mixins import PrecedenceMixins, TierMixins
from aligned_textgrid.sequences.tiers import SequenceTier
import warnings

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

    def set_intier(self, tier):
        self.intier = tier
    
    def set_tiername(self, tier):
        self.tiername = tier.name

    # def get_interval_index_at_time(self, tier = None):
    #     if tier and isinstance(tier, SequenceTier)
    #         int_idx = tier.get_interal_at_time(self.time)
    #         return int_idx
    #
    # def get_interval_at_point(self, tier=None):

    def set_pointspool(self):
        pass

    def nearest(self):
        pass
        # 
    