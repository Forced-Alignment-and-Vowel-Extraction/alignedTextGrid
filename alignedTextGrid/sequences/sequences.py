from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
import numpy as np

class SequenceInterval:
    def __init__(self, Interval = Interval(None, None, None), focus = True):
        self.start = Interval.start
        self.end = Interval.end
        self.label = Interval.label
        if focus:
            self.fol = self.__class__(focus=False)
            self.prev = self.__class__(focus=False)

    def set_fol(self, next_int):
        if isinstance(next_int, self.__class__):
            self.fol = next_int
        elif isinstance(next_int, Interval):
            self.fol = self.__class__(next_int, focus = False)
        else:
            raise Exception(f"Following segment must be an instance of {self.__class__.__name__} or Interval")

    def set_prev(self, prev_int):
        if isinstance(prev_int, self.__class__):
            self.prev = prev_int
        elif isinstance(prev_int, Interval):
            self.prev = self.__class__(prev_int, focus = False)
        else:
            raise Exception(f"Previous segment must be an instance of {self.__class__.__name__} or Interval")
    
    def set_final(self):
        self.set_fol(Interval(None, None, "#"))  

    def set_initial(self):
        self.set_prev(Interval(None, None, "#"))

    def set_feature(self, feature, value):
        setattr(self, feature, value)

    def return_interval(self):
        return Interval(self.start, self.end, self.label)
