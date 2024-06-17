"""
Module includes the `SequenceInterval` base class as well as 
`Top` and `Bottom` classes.
"""

import aligned_textgrid
from praatio.utilities.constants import Interval
import praatio
from praatio.data_classes.interval_tier import IntervalTier
from aligned_textgrid.mixins.mixins import InTierMixins, PrecedenceMixins
from aligned_textgrid.mixins.within import WithinMixins
from typing import Type, Any
import numpy as np
import warnings
import sys
from collections.abc import Sequence

if sys.version_info >= (3,11):
    from typing import Self
else:
    from typing_extensions import Self

class HierarchyMixins:

    # Ultimately, both of these class variables should be be
    # set to subclasses of SequenceInterval, but that can't be
    # done in the class definition since those subclasses
    # can't exist until after both SequenceVariable
    # and those subclasses have been created.
    superset_class = None
    subset_class = None
        
    @classmethod
    def set_superset_class(
            cls, 
            superset_class: type = None
        ):
        """_Set the superset class_

        Args:
            superset_class (Type[SequenceInterval], optional): 
                Must be a subclass of Sequence Interval, but not the *same* class as the
                current instance. Defaults to None.

        """
        if superset_class is None:
            cls.superset_class = None
        elif "Top" in cls.__name__ :
            cls.superset_class = None
        elif issubclass(superset_class, HierarchyPart) and not superset_class is cls:
            cls.superset_class = superset_class
            # avoid recursion here!
            if not cls.superset_class.subset_class is cls:
                cls.superset_class.set_subset_class(cls)
        elif superset_class is cls:
            raise Exception(f"Sequence {cls.__name__} can't have {superset_class.__name__} as its superset class.")
        elif not issubclass(superset_class, HierarchyPart):
            raise Exception(f"Sequence {cls.__name__} superset_class must be subclass of SequenceInterval. {superset_class.__name__} was given.")
        else:
            raise Exception(f"Unknown error setting {superset_class.__name__} as superset class of {cls.__name__}")
        
    @classmethod
    def set_subset_class(cls, subset_class = None):
        """summary

        Args:
            subset_class (Type[SequenceInterval], optional): 
                Must be a subclass of SequenceInterval, but not the *same* as the current instance.
                Defaults to None.
        """

        if subset_class is None:
            cls.subset_class = None
        elif "Bottom" in cls.__name__:
            cls.subset_class = None
        elif issubclass(subset_class, HierarchyPart) and not subset_class is cls:
            cls.subset_class = subset_class
            # avoid recursion here!
            if not cls.subset_class.superset_class is cls:
                cls.subset_class.set_superset_class(cls)
        elif not issubclass(subset_class, HierarchyPart):
            raise Exception(f"Sequence {cls.__name__} subset_class must be subclass of SequenceInterval. {subset_class.__name__} was given.")
        elif subset_class is cls:
            raise Exception(f"Sequence {cls.__name__} can't have {subset_class.__name__} as its subset class.")
        else:
            raise Exception(f"Unknown error setting {subset_class.__name__} as subset class of {cls.__name__}")            

class InstanceMixins(HierarchyMixins, WithinMixins):

    def set_super_instance(self, super_instance = None):
        """Sets the specific superset relationship

        Args:
            super_instance (SegmentInterval, optional): 
                Sets the superset relationship between this object and `super_instance` object.
                Current object is appended to `super_instance`'s subset list.
        """

        if super_instance is None:
            warnings.warn("No superset instance provided")   
        elif isinstance(super_instance, self.superset_class) and not super_instance is self.super_instance:
            self.super_instance = super_instance
            self.super_instance.append_subset_list(self)
        else:
            raise Exception(f"The superset_class was defined as {self.superset_class.__name__}, but provided super_instance was {type(super_instance).__name__}")
                        

    ## Subset Methods
        
    def set_subset_list(self, subset_list = None):
        """Appends all objects to the `subset_list`

        Args:
            subset_list (List[SequenceInterval], optional): 
                A list of SequenceInterval subclass objects. Cannot be the
                same subclass of the current object. Current object is
                set as the `super_instance` of all objects in the list.
        """

        self._subset_list = IntervalList()
        if subset_list is None:
            return
        if all([isinstance(subint, self.subset_class) for subint in subset_list]):
            for element in subset_list:
                self.append_subset_list(element)
            self._set_within()
            self._set_subset_precedence()

        else:
            subset_class_set = set([type(x).__name__ for x in subset_list])
            raise Exception(f"The subset_class was defined as {self.subset_class.__name__}, but provided subset_list contained {subset_class_set}")

    def append_subset_list(self, subset_instance = None):
        """Append a single item to subset list

        Args:
            subset_instance (SequenceInterval): 
                The SequenceInterval subclass instance to append to the
                `subset_list`. Current object is set as `super_instance`
                to `subset_instance`. Precedence relationships within
                `subset_list` are reset.
        """

        if isinstance(subset_instance, self.subset_class) and not subset_instance in self._subset_list:
            if subset_instance.super_instance:
                subset_instance.remove_superset()
            self._subset_list.append(subset_instance)
            self._set_subset_precedence()
            # avoid recursion
            if not self is subset_instance.super_instance:
                subset_instance.set_super_instance(self)
        elif isinstance(subset_instance, self.subset_class):
            pass
        else:
            raise Exception(f"The subset_class was defined as {self.subset_class.__name__}, but provided subset_instance was {type(subset_instance).__name__}")
        
    def remove_from_subset_list(self, subset_instance = None):
        """Remove a sequence interval from the subset list

        Args:
            subset_instance (SequenceInterval): The sequence interval to remove.
        """
        if subset_instance not in self._subset_list:
            #warnings.warn("Provided subset_instance was not in the subset list")
            return
        
        self._subset_list.remove(subset_instance)
        subset_instance.super_instance = None
        subset_instance.within = None
        self._set_subset_precedence()
    
    def remove_superset(self):
        """Remove the superset instance from the current subset class
        """
        
        if self.super_instance is None:
            warnings.warn("Provided SequenceInterval has no superset instance")
            return
        
        self.super_instance.remove_from_subset_list(self)


    def _set_subset_precedence(self):
        """summary
            Private method. Sorts subset list and re-sets precedence 
            relationshops.
        """
        for idx, p in enumerate(self._subset_list):
            if idx == 0:
                p.set_initial()
            else:
                p.set_prev(self._subset_list[idx-1])
            if idx == len(self._subset_list)-1:
                p.set_final()
            else:
                p.set_fol(self._subset_list[idx+1])

    def _set_within(self):
        """summary
            Private method. Sets within
        """
        self.contains = self._subset_list

    ## Subset Validation
    def validate(self) -> bool:
        """Validate the subset list
        Validation checks to see if

        1. The first item in `subset_list` starts at the same time as `self`.
        If not, does it start before or after `self.start`
        2. The last item in `subset_list` ends at the same time as `self`.
        If not, does it end before or after `self.end`.
        3. Do all of the subset intervals fit "snugly" inside of the superset,
        that is, with no gaps or overlaps.

        This doesn't raise any exceptions, but does issue a warning for any
        checks that don't pass.

        Returns:
            (bool):
                - `True` if all checks pass, or if the `subset_list` is empty.
                - `False` if any checks fail.
        """
        validation_concerns = []
        if len(self.subset_list) == 0:
            return True
        else:
            if not np.allclose(self.start, self.sub_starts[0]):
                if self.start < self.sub_starts[0]:
                    validation_concerns.append(
                        "First subset interval starts after current interval"
                    )
                else:
                    validation_concerns.append(
                        "First subset interval starts before current interval"
                    )
            if not np.allclose(self.end, self.sub_ends[-1]):
                if self.end > self.sub_ends[-1]:
                    validation_concerns.append(
                        "Last subset interval ends before current interval"
                    )
                else:
                    validation_concerns.append(
                        "Last subset interval ends after current interval"
                    )
            if not np.allclose(self.sub_starts[1:], self.sub_ends[:-1]):
                validation_concerns.append(
                    "Not all subintervals fit snugly"
                )
            ## prepping messages
            if len(validation_concerns) == 0:
                return True
            else:
                validation_warn = "\n".join(validation_concerns)
                warnings.warn(validation_warn)
                return False         
                
class HierarchyPart(HierarchyMixins):
    def __init__(self):
        pass

class IntervalList(Sequence):
    """A list of SequenceIntervals that
    remains sorted

    Args:
        *args (SequenceInterval):
            SequenceIntervals

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
    
    def __add__(self, other:Sequence):
        unique_other_classes = set([x.__class__ for x in other])

        if len(unique_other_classes) > 1:
            raise ValueError("All values in added list must have the same class.")
    
        if len(unique_other_classes) < 1:
            return
        
        incoming_class = next(iter(unique_other_classes))

        if not incoming_class is self.entry_class:
            raise ValueError("All values in added list must have the same class as original list.")
        
        return IntervalList(*(self._values + [x for x in other]))

    def __repr__(self):
        return self._values.__repr__()
            
    def _sort(self):
        if len(self._values) > 0:
            item_starts = np.array([x.start for x in self._values])
            item_order = np.argsort(item_starts)
            self._values = [self._values[idx] for idx in item_order]    


    @property
    def starts(self)->np.array:
        if len(self) > 0:
            return np.array([x.start for x in self])

        return np.array([])
    
    @property
    def ends(self) -> np.array:
        if len(self) > 0:
            return np.array([x.end for x in self])
        
        return np.array([])
    
    @property
    def labels(self) -> list[str]:
        if len(self) > 0:
            return [x.label for x in self]

        return []
    
    def append(self, value):
        """Append a SequenceInterval to the list.

        After appending, the SequenceIntervals are re-sorted

        Args:
            value (SequenceInterval): 
                A SequenceInterval to append
        """
        if self.entry_class is None:
            self.entry_class = value.__class__
        
        if not self.entry_class is value.__class__:
            raise ValueError("All values must have the same class.")

        self._values.append(value)
        self._sort()

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

class SequenceInterval(InstanceMixins, InTierMixins, PrecedenceMixins, HierarchyPart):
    """
    A class to describe an interval with precedence relationships and hierarchical relationships

    Args:
        interval (list|tuple|Interval|Self): 
            A Praat textgrid Interval. This could one of: 
            i) A list or tuple of start, end and label values (e.g. `[0, 1, "foo"]`); 
            ii) A `praatio.utilities.constants.Interval`
            iii) Another `SequenceInterval`. 
            In this last case, only the `start`, `end` and `label` values from the original
            `SequenceInterval` are preserved in the new one. 

    Examples:
        A new `SequenceInterval` can be created from scratch by passing it a tuple
        of a start time, end time, and a label
        ```{python}
        from aligned_textgrid import SequenceInterval

        sample_interval = SequenceInterval((0, 1, "sample"))
        print(sample_interval)
        ```

        You can pass a `SequenceInterval` to another
        `SequenceInterval` or subclass (like [](`~aligned_textgrid.sequences.word_and_phone.Word`))
        as well

        ```{python}
        from aligned_textgrid import Word

        sample_word = Word(sample_interval)
        print(sample_word)
        ```

    Attributes:
        start (float):
            Start time of the interval
        end (float):
            End time of the interval
        label (Any):
            Label of the interval
        duration (float):
            The duration of the interval
        intier (SequenceTier):
            The sequence tier the current interval is within.
        tier_index (int):
            The index of sequence within its tier.
        fol (SequenceInterval):
            Instance of the following interval. Is the same subclass as the current instance.
        prev (SequenceInterval): 
            Instance of the previous interval. Is the same subclass as current instance.
        super_instance (SequenceInterval): 
            The instance of the superset. Cannot be the same subclass as the current instance.
        subset_list (list[SequenceInterval]): 
            A list of subset instances. Cannot be the same subclass of the current instance.
        sub_starts (numpy.ndarray):
            A numpy array of start times for the subset list
        sub_ends (numpy.ndarray):
            A numpy array of end times for the subset list
        sub_labels (list[Any]):
            A list of labels from the subset list
    """    

    # utilities
    def __init__(
        self, 
        interval: list|tuple|Interval|Self= (None, None, None),
        *,
        Interval = None
    ):
        if Interval:
            interval = Interval

        if isinstance(interval, SequenceInterval):
            interval = (
                interval.start,
                interval.end,
                interval.label
            )
        rep_none = 3 - len(interval)
        interval += tuple([None]) * rep_none

        if len(interval) > 3:
            raise ValueError((
                "The tuple or list to create a SequenceInterval should be no "
                "more than 3 values long. "
                f"{len(interval)} were provided."
            ))

        interval = praatio.utilities.constants.Interval(*interval)

        self.start = interval.start
        self.end = interval.end
        self.label = interval.label
        
        self.fol = None
        self.prev = None

        ## prevent infinite recursion
        if self.label != "#":
            self.set_final()
        if self.label != "#":
            self.set_initial()

        self._subset_list = IntervalList()
        self.super_instance= None

        self.intier = None

    def __contains__(self, item):
        return item in self.subset_list

    def __getitem__(self, idx):
        return self.subset_list[idx]

    def __iter__(self):
        self.current = 0
        return self
    
    def __len__(self):
        return len(self.subset_list)
    
    def __next__(self):
        if self.current < len(self.subset_list):
            this_seg = self.subset_list[self.current]
            self.current+=1
            return this_seg
        else:
            raise StopIteration
        
    def index(
            self,
            subset_instance
    ) -> int:
        """Returns subset instance index

        Args:
            subset_instance (SequenceInterval): 
                A subset instance to get the index of.

        Returns:
            int: The index of `subset_instance`
        """
        return self.subset_list.index(subset_instance)

    def pop(
            self,
            subset_instance
    ):
        """Pop a sequence interval from the subset list

        Args:
            subset_instance (SequenceInterval): A sequence interval to pop
        """
        self.subset_list.pop(subset_instance)
        self._set_subset_precedence()
    
    def __repr__(self) -> str:
        out_string = f"Class {type(self).__name__}, label: {self.label}"
        if self.superset_class:
            out_string += f", .superset_class: {self.superset_class.__name__}"
            if self.super_instance:
                out_string += f", .super_instance: {self.super_instance.label}"
            else:
                out_string += f", .super_instance, None"            
        else:
            out_string += ", .superset_class: None"     
        if self.subset_class:
            out_string += f", .subset_class: {self.subset_class.__name__}"
            if self.subset_list:
                out_string += f", .subset_list: {repr(self.sub_labels)}"
        else:
            out_string += ", .subset_class: None"
        return out_string
    
    # properties
    @property
    def subset_list(self):
        return self._subset_list
    
    @subset_list.setter
    def subset_list(self, intervals: list[Self]|IntervalList[Self]):
        intervals = IntervalList(*intervals)
        self.set_subset_list(intervals)

    @property
    def start(self):
        return self._start
    
    @start.setter
    def start(self, time):
        self._start = time

    @property
    def end(self):
        return self._end
    
    @end.setter
    def end(self, time):
        self._end = time

    @property
    def sub_starts(self):
        return self.subset_list.starts
        
    @property
    def sub_ends(self):
        return self.subset_list.ends
    
    @property
    def sub_labels(self):
        return self.subset_list.labels
    
    def _shift(self, increment):
        self.start += increment
        self.end += increment
        
    @property
    def duration(self) -> float:
        return self.end - self.start
    
    @property
    def entry_class(self):
        return self.__class__
      
    ## Fusion
    def fuse_rightwards(
            self, 
            label_fun = lambda x, y: " ".join([x, y])
        ):
        """Fuse the current segment with the following segment

        Args:
            label_fun (function): Function for joining interval labels.
        """
        fuser = self
        fusee = self.fol

        if not fusee.label == "#":

            fuser.end = fusee.end
            fuser.fol = fusee.fol
            fuser.label = label_fun(fuser.label, fusee.label)

            new_list = fuser._subset_list + fusee.subset_list
            fuser.set_subset_list(new_list)
            
            if fuser.superset_class is Top and fuser.intier:
                fuser.intier.pop(fusee)
            else:
                if fuser.intier:
                    fuser.intier.pop(fusee)
                if fuser.super_instance:
                    fuser.super_instance.pop(fusee)                    
        else:
            raise Exception("Cannot fuse rightwards at right edge")
        
    def fuse_leftwards(
            self, 
            label_fun = lambda x, y: " ".join([x, y])
        ):
        """Fuse the current segment with the previous segment

        Args:
            label_fun (function): Function for joining interval labels.
        """
        fusee = self.prev
        fuser = self


        if not fusee.label == "#":

            fuser.start = fusee.start
            fuser.prev = fusee.prev
            fuser.label = label_fun(fusee.label, fuser.label)

            new_list = fusee.subset_list + fuser._subset_list
            fuser.set_subset_list(new_list)
            
            if fuser.superset_class is Top and fuser.intier:
                fuser.intier.pop(fusee)
            else:
                if fuser.intier:
                    fuser.intier.pop(fusee)
                if fuser.super_instance:
                    fuser.super_instance.pop(fusee)                    
        else:
            raise Exception("Cannot fuse leftwards at right edge")
    
    def fuse_rightward(self):
        self.fuse_rightwards()

    def fuse_leftward(self):
        self.fuse_leftwards()        

    ## Extensions and Saving
    def set_feature(
            self, 
            feature: str, 
            value: Any):
        """Sets arbitrary object attribute

        This will be most useful for creating custom subclasses.

        Args:
            feature (str): New attribute name
            value (Any): New attribute value
        """
        setattr(self, feature, value)

class Top(HierarchyPart):
    """A top level interval class
    
    This is a special subclass intended to be the `superset_class` 
    for classes at the top of the hierarchy.

    """
    def __init__(self):
        super().__init__()

class Bottom(HierarchyPart):
    """A bottom level interval class

    This is a special subclass intended to be the `subset_class` 
    for classes at the bottom of the hierarchy.

    """
    def __init__(self):
        super().__init__()

# This is how the default behavior of `SequenceInterval` 
# with respect to subset and superset classes is controlled
Top.set_superset_class()
Bottom.set_subset_class()
SequenceInterval.set_superset_class(Top)
SequenceInterval.set_subset_class(Bottom)
