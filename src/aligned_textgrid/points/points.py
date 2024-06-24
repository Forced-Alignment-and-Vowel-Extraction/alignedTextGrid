from praatio.utilities.constants import Point
from aligned_textgrid.mixins.mixins import PrecedenceMixins, InTierMixins, SequenceBaseClass
from aligned_textgrid.mixins.within import WithinMixins
from aligned_textgrid.sequences.tiers import SequenceTier
from aligned_textgrid.sequences.sequences import SequenceInterval
import warnings
import numpy as np
from typing import TYPE_CHECKING

import sys
if sys.version_info >= (3,11):
    from typing import Self
else:
    from typing_extensions import Self

if TYPE_CHECKING:
    from aligned_textgrid import SequencePointTier

class  SequencePoint(SequenceBaseClass, PrecedenceMixins, InTierMixins, WithinMixins):
    """Sequence Points
    
    Args:
        point (list|tuple|Point|Self):
            A list or tuple of a time and label value.
    
    Examples:
        ```{python}
        from aligned_textgrid import SequencePoint, SequenceInterval

        first_point = SequencePoint((0, "first"))
        print(first_point)
        ```

        ```{python}
        second_point = SequencePoint((1, "second"))
        interval = SequenceInterval((0.5, 2, "word"))

        print(
            first_point.distance_from(second_point)
        )

        print(
            first_point.distance_from(interval)
        )
        ```

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
            point: list|tuple|Point|Self = (None, None)
        ):
        self._seq_type = SequencePoint
        if isinstance(point, SequencePoint):
            point = Point(point.time, point.label)

        if len(point) > 2:
            raise ValueError((
                "The tuple to create a SequencePoint should be "
                "no more than 2 values long. "
                f"{len(point)} were provided."
            ))

        point = Point(*point)


        self.time = point.time
        self.label = point.label

        self.intier:'SequencePointTier|None' = None
        self.tiername:str|None = None
        self.pointspool = None

        self.fol:SequencePoint|None = None
        self.prev:SequencePoint|None = None

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
    
    def __add__(self, x):
        warnings.warn("+ is not implemented for SequencePoint")
        return self
    
    def append(self, x):
        warnings.warn("append() is not implemented for SequencePoint")
    
    ## Properties
    @property
    def entry_class(self):
        return self.__class__

    @property
    def time(self):
        return self._time
    
    @time.setter
    def time(self, time):
        self._time = time

    @property
    def start(self):
        return self.time

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
    def _shift(self, increment):
        self.time += increment

    def distance_from(
            self, 
            entry: Self|SequenceInterval
        ) -> np.array:
        """Distance from an entry

        Args:
            entry (Self | SequenceInterval):
                A point or an interval to get the distance of the current 
                point from

        Returns:
            (np.array):
                a single value in the case of a point, a numpy array in
                the case of an interval.
        """
        if isinstance(entry, SequencePoint):
            return np.array(self.time - entry.time)
        
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

    
SequencePoint._set_seq_type(SequencePoint)