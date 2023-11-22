"""
Special point and interval classes for PoLaR annotation
"""
from aligned_textgrid.sequences.sequences import SequenceInterval
from aligned_textgrid.sequences.tiers import SequenceTier
from aligned_textgrid.points.points import SequencePoint
import warnings
import numpy as np

class PrStr(SequencePoint):
    """PrStr tier points

    Attributes:
        ...:
           All methods and attributes from SequencePoint
        certainty (str):
            If a '?' was appended to a point label, `'uncertain'`, otherwise
            `'certain'`
        status (str):
            `'edge'` or `'prominence'`
    """

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
    """A ToBI point class

    Attributes:
       ...:
          All methods and attributes from SequencePoint
    """
    def __init__(self, Point=None):
        super().__init__(Point)

class TurningPoints(SequencePoint):
    """A turning point class

    Attributes:
        ...:
            All methods and attributes from SequencePoint
        level (Levels):
            The `Levels` point associated with this turning point
        certainty (str):
            If a '?' was appended to a point label, `'uncertain'`, otherwise
            `'certain'`
        override (str):
            An override value, if provided
    """
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
    """A ranges interval

    Attributes:
        ...:
            All methods and attributes from SequenceInterval
        range (np.array):
            The f0 range
        low (float):
            The low value of the f0 range
        high (float):
            The high value of the f0 range
        bands (np.array):
            The break points in the f0 range (6 break points defining 5 bands)
    """
    def __init__(self, Interval):
        super().__init__(Interval)
    
    @property
    def range(self):
        range_chr = self.label.split("-")
        try:
            range_num = [float(x) for x in range_chr] 
        except ValueError:
            range_num = [np.nan, np.nan]
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
    """A levels point class

    Attributes:
        ...:
            All methods and attributes from SequencePoint
        certainty (str):
            If a '?' was appended to a point label, `'uncertain'`, otherwise
            `'certain'`
        level (int):
            The level value given to this point
        band (np.array):
            The f0 band for this point, given its level
        ranges_interval (Ranges):
            The Ranges interval this point falls within
        ranges_tier (SequenceTier):
            The Ranges tier associated with these Levels
        turning_point (TurningPoints):
            The TurningPoints point associated with this Levels point

    """
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
    """Misc points
    """
    def __init(self, Point):
        super().__init__(Point)
    