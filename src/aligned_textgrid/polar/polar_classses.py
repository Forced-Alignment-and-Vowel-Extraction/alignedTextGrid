from aligned_textgrid.sequences.sequences import *
from aligned_textgrid.points.points import *
from aligned_textgrid.sequences.word_and_phone import *
import warnings
import numpy as np

class PrStr(SequencePoint):
    def __init__(self, Point):
        super().__init__(Point)

    @property
    def certainty(self):
        if "?" in self.label:
            return "uncertain"
        return "certain"

    @property
    def status(self):
        if "*" in self.label:
            return "prominence"
        if "]" in self.label:
            return "edge"
        warnings.warn("Invalid label")
        return self.label
    
class ToBI(SequencePoint):
    def __init__(self, Point=None):
        super().__init__(Point)

class TurningPoints(SequencePoint):
    def __init__(self, Point):
        super().__init__(Point)

    @property
    def certainty(self):
        if "?" in self.label:
            return "uncertain"
        return "certain"
    
    @property
    def override(self):
        override_value = self.label.split(",")[-1]
        if override_value == "0":
            return None
        return override_value

class Ranges(SequenceInterval):
    def __init__(self, Interval):
        super().__init__(Interval)
    
    @property
    def range(self):
        range_chr = self.label.split("-")
        range_num = [float(x) for x in range_chr] 
        return np.array(range_num)
    
    @property
    def low(self):
        return self.range[0]
    
    @property
    def high(self):
        return self.range[1]

    @property
    def bands(self):
        return np.linspace(self.low, self.high, num = 6)

class Levels(SequencePoint):
    def __init__(self, Point):
        super().__init__(Point)
        self.ranges_tier = None
    
    def set_ranges_tier(self, tier: Ranges):
        self.reference_tier = tier

class Misc(SequencePoint):
    def __init(self, Point):
        super().__init__(Point)
    