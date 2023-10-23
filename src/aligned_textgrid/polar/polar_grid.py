from aligned_textgrid.sequences.word_and_phone import *
from aligned_textgrid.aligned_textgrid import *
from aligned_textgrid.sequences.tiers import *
from aligned_textgrid.points.ptiers import *

class PolarGrid(AlignedTextGrid):
    def __init__(self,
                 textgrid: Textgrid = None,
                 textgrid_path: str =  None,
                 entry_classes = None):
        super().__init__(
            textgrid=textgrid, 
            textgrid_path=textgrid_path, 
            entry_classes=entry_classes
            )
        # self.words = None
        # self.phones = None
        # self.tobi = None
        # self.prstr = None
        # self.turningpoints = None
        # self.levels = None
        # self.ranges = None
        self._set_named_accessors()
        
    #def _get_tier_by_class(self, entry_class):

        
    def _set_named_accessors(self):
        for tg in self.tier_groups:
            for tier in tg:
                setattr(self, tier.entry_class.__name__, tier)