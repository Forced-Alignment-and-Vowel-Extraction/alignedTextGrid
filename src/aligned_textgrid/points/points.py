from praatio.utilities.constants import Point
from aligned_textgrid.mixins.mixins import PrecedenceMixins, InTierMixins
from aligned_textgrid.mixins.within import WithinMixins
from aligned_textgrid.sequences.tiers import SequenceTier
from aligned_textgrid.sequences.sequences import SequenceInterval
from typing_extensions import Self
import warnings
import numpy as np

from typing import Union

class  SequencePoint(PrecedenceMixins, InTierMixins, WithinMixins):
    """Sequence Points
    
    Args:
        point (Point): a `praatio.point` object
    
    Attributes:
        ...:
            All attributes and methods included in PrecedenceMixins and InTierMixins
        time (float):
            Time value associated with the point.
        label (str):
            Label associated with the point
        intier (SequencePointTier):
            If the SequencePoint is within a tier, this accesses the tier.
        fol (SequencePoint):
            If defined, the following SequencePoint within the same tier
        prev (SequencePoint):
            If defined, the previous SequencePoint within the same tier.
        fol_distance (float):
            If `fol` is defined, the difference between the current point and `fol`
            (should be >= 0)
        prev_distance (float):
            if `prev` is defined, the difference between the current point and `prev`
            (should be <= 0).
    """

    def __init__(
            self,
            point = Point(0, "")
        ):

        if isinstance(point, SequencePoint):
            point = (point.time, point.label)

        point = Point(*point)

        self.time = point.time
        self.label = point.label

        self.intier = None
        self.tiername = None
        self.pointspool = None

        self.fol = None
        self.prev = None

        if self.label != "#":
            self.set_final()
        if self.label != "#":
            self.set_initial()


    def __repr__(self) -> str:
        out_string = f"Class {type(self).__name__}, label: {self.label};"
        if self.intier:
            out_string += f" tier_index: {self.tier_index}"
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
    def distance_from(
            self, 
            entry: Self|SequenceInterval
        ) -> Union[float, np.array]:
        """Distance from an entry

        Args:
            entry (Self | SequenceInterval):
                A point or an interval to get the distance of the current 
                point from

        Returns:
            (float | np.array):
                a single value in the case of a point, a numpy array in
                the case of an interval.
        """
        if isinstance(entry, SequencePoint):
            return self.time - entry.time
        
        if isinstance(entry, SequenceInterval):
            entry_times = np.array([entry.start, entry.end])
            return self.time - entry_times

    def get_interval_index_at_time(
            self, 
            tier: SequenceTier = None
        ) -> int:
        """Get the index of an interval at the point's time

        Args:
            tier (SequenceTier): A SequenceTier.

        Returns:
            (int): 
              The index of the SequenceInterval within which the point falls
        """
        if tier and isinstance(tier, SequenceTier):
            int_idx = tier.get_interval_at_time(self.time)
            return int_idx
    
    def get_interval_at_point(
            self, 
            tier: SequenceTier=None
        ) -> SequenceInterval:
        """Get the `SequenceInterval` the current point falls within

        Args:
            tier (SequenceTier):
                The sequence tier within which to look for a matching SequenceInterval

        Returns:
            (SequenceInterval): 
                The SequenceInterval within which the current point falls
        """
        if tier and isinstance(tier, SequenceTier):
            return tier[self.get_interval_index_at_time(tier)]

    
    