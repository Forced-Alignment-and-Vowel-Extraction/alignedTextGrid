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
        self.level = None

    def set_level(self, tier):
        instance = tier.get_nearest_point(self.time)
        #instance = tier[idx]
        
        if self.level is instance:
            return
        
        if np.allclose(self.time, instance.time):
            self.level = instance

            instance.set_turning_point(self.intier)

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
        self.range_interval = None
        self.turning_point = None

    def set_ranges_tier(self, tier: Ranges):
        self.ranges_tier = tier
    
    def set_range_interval(self):
        if self.ranges_tier:
            self.range_interval = self.get_interval_at_point(self.ranges_tier)
    
    def set_turning_point(self, tier):
        instance = tier.get_nearest_point(self.time)
        #instance = tier[idx]

        if self.turning_point is instance:
            return

        if np.allclose(self.time, instance.time):
            self.turning_point = instance

            instance.set_level(self.intier)

    @property
    def certainty(self):
        if "?" in self.label:
            return "uncertain"
        return "certain"

    @property
    def level(self):
        return int(self.label.replace("?", ""))
    
    @property
    def band(self):
        return self.range_interval.bands[self.level-1:self.level+1]


class Misc(SequencePoint):
    def __init(self, Point):
        super().__init__(Point)
    