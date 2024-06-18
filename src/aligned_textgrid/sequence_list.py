import numpy as np
import warnings
import sys
from collections.abc import Sequence
if sys.version_info >= (3,11):
    from typing import Self
else:
    from typing_extensions import Self

class SequenceList(Sequence):
    """A list of SequenceIntervals or SequencePoints that
    remains sorted

    Args:
        *args (SequenceInterval, SequencePoint):
            SequenceIntervals or SequencePoints

    Attributes:
        starts (np.array):
            An array of start times
        ends (np.array):
            An array of end times
        labels (list[str]):
            A list of labels
    """

    def __init__(self, *args):
        self._values = []
        self.entry_class = None
        for arg in args:
            self.append(arg)

    def __getitem__(self, idx):
        return self._values[idx]
    
    def __len__(self):
        return len(self._values)
    
    def __contains__(self, other):
        if other in self._values:
            return True
        self_tuples = [tuple(x.return_interval()) for x in self]
        other_tuple = tuple(other.return_interval())
        if other_tuple in self._values:
            return True
        
        return False
    
    def __add__(self, other:Sequence):

        other = [x for x in other if x not in self]

        if len(other) < 1:
            return self

        unique_other_classes = set([x.__class__ for x in other])

        if len(unique_other_classes) > 1:
            raise ValueError("All values in added list must have the same class.")
    
        if len(unique_other_classes) < 1:
            return self
        
        incoming_class = next(iter(unique_other_classes))
        if self.entry_class and not incoming_class.__name__ == self.entry_class.__name__:
            raise ValueError("All values in added list must have the same class as original list.")
        
        if not self.entry_class:
            self.entry_class = next(iter(unique_other_classes))

        new_list = self._values + [x for x in other]
        new_intervals = [self.entry_class(x) if not x.entry_class is self.entry_class else x for x in new_list]
        output =  SequenceList(*new_intervals)
        output._check_no_overlaps()
        return output

    def __repr__(self):
        return self._values.__repr__()
            
    def _sort(self):
        if len(self._values) > 0:
            if hasattr(self[0], "start"):
                item_starts = np.array([x.start for x in self._values])
            if hasattr(self[0], "time"):
                item_starts = np.array([x.time for x in self._values])
            item_order = np.argsort(item_starts)
            self._values = [self._values[idx] for idx in item_order]
    
    def _entry_class_checker(self, value):
        if self.entry_class is None:
            self.entry_class = value.entry_class
        
        if not issubclass(self.entry_class, value.entry_class):
            raise ValueError("All values must have the same class.")
    
    def _shift(self, increment):
        for value in self:
            value._shift(increment)

    def _check_no_overlaps(
          self
    )->bool:
        starts = self.starts
        ends = self.ends

        a = np.array([e > starts for e in ends])
        b = np.array([s < ends for s in starts])

        n_overlaps = (a&b).sum()

        overlaps = n_overlaps > len(self)

        if overlaps:
            warnings.warn("Some intervals provided overlap in time")

        return not n_overlaps > len(self)            

    @property
    def starts(self)->np.array:
        if len(self) < 1:
            return np.array([])
        
        if hasattr(self[0], "start"):
            return np.array([x.start for x in self])
        
        if hasattr(self[0], "time"):
            return np.array([x.time for x in self])

    @property
    def ends(self) -> np.array:
        if len(self) < 1:    
            return np.array([])

        if hasattr(self[0], "end"):
            return np.array([x.end for x in self])
        
        if hasattr(self[0], "time"):
            return np.array([x.time for x in self])
    
    @property
    def labels(self) -> list[str]:
        if len(self) > 0:
            return [x.label for x in self]

        return []
    
    def append(self, value, shift:bool = False):
        """Append a SequenceInterval to the list.

        After appending, the SequenceIntervals are re-sorted

        Args:
            value (SequenceInterval): 
                A SequenceInterval to append
        """
        if value in self:
            return
        
        self._entry_class_checker(value)
        value = self.entry_class(value)
        
        increment = 0
        if len(self.ends) > 0:
            increment = self.ends[-1]
        if shift:
            value._shift(increment)

        self._values.append(value)
        self._sort()

    def concat(self, intervals:list|Self):
        intervals = SequenceList(*intervals)

        increment = 0
        if len(self.ends) > 0:
            increment = self.ends[-1]
        
        intervals._shift(increment)          
        
        new_values = self + intervals
        self._values = new_values

       
    def remove(self, x):
        """Remove a SequenceInterval from the list

        Args:
            x (SequenceInterval):
                The SequenceInterval to remove.
        """
        self._values.remove(x)

    def pop(self, x):
        """Pop a SequneceInterval

        Args:
            x (SequenceInterval):
                SequenceInterval to pop
        """
        if x in self:
            pop_idx = self.index(x)
            self._values.pop(pop_idx)
