from praatio.utilities.constants import Interval, Point
from praatio.data_classes.interval_tier import IntervalTier
from praatio.data_classes.point_tier import PointTier
from typing import Type, Any
import numpy as np
import warnings


class PrecedenceMixins:
    """Methods and attributes for SequenceIntervals and SequencePoints

    Attributes:
        first (SequenceInterval): The first interval in the subset list
        last (SequenceInterval): The last interval in the subset list
    """

    @property
    def first(self):
        if hasattr(self, "subset_list") and len(self.subset_list) > 0:
            return self.subset_list[0]
        if hasattr(self, "subset_list"):
            raise IndexError(f"{type(self).__name__} with label "\
                             f"'{self.label}' subset list is empty.")
        raise AttributeError(f"{type(self).__name__} is not indexable.")
                
    @property
    def last(self):
        if hasattr(self, "subset_list") and len(self.subset_list) > 0:
            return self.subset_list[-1]
        if hasattr(self, "subset_list"):
            raise IndexError(f"{type(self).__name__} with label "\
                             f"'{self.label}' subset list is empty.")
        raise AttributeError(f"{type(self).__name__} is not indexable.")        

    def set_fol(
            self, next_int):
        """_Sets the following instance_

        Args:
            next_int (SequenceInterval|SequencePoint): 
                Sets the `next_int` as the `fol` entry.
                Must be of the same class as the current object.
                That is, `type(next_int) is type(self)`
        """
        if next_int is self:
            raise Exception(f"A segment can't follow itself.")
        if self.label == "#":
            return
        if self.fol is next_int:
            return
        elif type(next_int) is type(self):
            self.fol = next_int
            self.fol.set_prev(self)
        else:
            raise Exception(f"Following segment must be an instance of {type(self).__name__}")

    def set_prev(self, prev_int):
        """_Sets the previous intance_

        Args:
            prev_int (SequenceInterval|SequencePoint):
                Sets the `prev_int` as the `prev` entry.
                Must be of the same class as the current object.
                That is, `type(prev_int) is type(self)`                
        """
        if prev_int is self:
            raise Exception("A segment can't precede itself.")
        if self.label == "#":
            return
        if self.prev is prev_int:
            return
        elif type(prev_int) is type(self):
            self.prev = prev_int
            self.prev.set_fol(self)
        else:
            raise Exception(f"Previous segment must be an instance of {type(self).__name__}")
    
    def set_final(self):
        """_Sets the current object as having no `fol` entry_
        
        While `self.fol` is defined for these entries, the actual
        instance does not appear in `self.super_instance.subset_list`
        """
        
        if hasattr(self, "start"):
            self.set_fol(type(self)(Interval(None, None, "#")))
        elif hasattr(self, "time"):
            self.set_fol(type(self)(Point(None, "#")))

    def set_initial(self):
        """_Sets the current object as having no `prev` entry_

        While `self.prev` is defined for these entries, the actual 
        instance does not appear in `self.super_instance.subset_list`
        """
        if hasattr(self, "start"):
            self.set_prev(type(self)(Interval(None, None, "#")))
        elif hasattr(self, "time"):
            self.set_prev(type(self)(Point(None, "#")))

class InTierMixins:
    """InTier methods and attributes

    Attributes:
        tier_index (int):
          Index of the current entry within its tier
    """

    ## Tier operations
    @property
    def tier_index(self):
        if not self.intier is None:
            return self.intier.index(self)
        else:
            return None
    
    def get_tierwise(
            self,
            idx:int = 0
        ):
        """_Get entry by relative tier index_

        Returns a SequenceInterval or SequencePoint from an index position relative to
        the current sequence.

        - `idx=0` - Returns the current entry
        - `idx=1` - Returns the following entry on the tier. If the current entry is 
            in the final position within its subset list, this will not be the same as
            `.fol`
        - `idx=-1` - Returns the previous entry on the tier. If the current entry is 
            in the initial position within its subset list, this will not be the same as
            `.prev` 

        This will raise an ordinary IndexError if the relative index exceeds the length
        of the tier.

        Args:
            idx (int, optional): 
                The relative tier index at which to retrieve a sequence.
                Defaults to 0.

        Returns:
            (SequenceInterval|SequencePoint): The entry at the relative index
        """
        if not self.intier is None:
            return self.intier[self.tier_index + idx]
        else:
            return None

    def return_interval(self) -> Interval:
        """_Return current object as `Interval`_
        
        Will be useful for saving back to textgrid

        Returns:
            (praatio.utilities.constants.Interval): A `praatio` `Interval` object
        """
        return Interval(self.start, self.end, self.label)
    
    def return_point(self) -> Point:
        """_Return current object as `Point`_

        Returns:
           (praatio.utilities.constants.Point): A `praatio` `Point` 
           object
        """
        return Point(self.time, self.label)