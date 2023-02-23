from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from alignedTextGrid.sequences.sequences import SequenceInterval, Top, Bottom
import numpy as np

class Phone(SequenceInterval):
    def __init__(self, Interval = Interval(None, None, None), focus = True):
         super().__init__(Interval, focus)
         self.set_word = super().set_super_instance
         self.set_superset_class(Word)
         self.set_subset_class(Bottom)

    @property
    def inword(self):
        return self.super_instance

class Word(SequenceInterval):
    def __init__(
            self, 
            Interval = Interval(None, None, None), 
            focus = True
        ):
        super().__init__(Interval, focus)
        self.set_phones = super().set_subset_list
        self.set_superset_class(Top)
        self.set_subset_class(Phone)
    
    @property
    def phone_list(self):
        return self.subset_list
    
    @property
    def phones(self):
        return [p.label for p in self.phone_list]