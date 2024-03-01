"""
Module includes the `SequenceInterval` base class as well as 
`Top` and `Bottom` classes.
"""

from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from aligned_textgrid.mixins.mixins import InTierMixins, PrecedenceMixins
from aligned_textgrid.mixins.within import WithinMixins
from typing import Type, Any
import numpy as np
import warnings

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

        self.subset_list = []
        if all([isinstance(subint, self.subset_class) for subint in subset_list]):
            for element in subset_list:
                self.append_subset_list(element)
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

        if isinstance(subset_instance, self.subset_class) and not subset_instance in self.subset_list:
            if subset_instance.super_instance:
                subset_instance.remove_superset()
            self.subset_list.append(subset_instance)
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
        if subset_instance not in self.subset_list:
            #warnings.warn("Provided subset_instance was not in the subset list")
            return
        
        self.subset_list.remove(subset_instance)
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

        self._sort_subsetlist()
        for idx, p in enumerate(self.subset_list):
            if idx == 0:
                p.set_initial()
            else:
                p.set_prev(self.subset_list[idx-1])
            if idx == len(self.subset_list)-1:
                p.set_final()
            else:
                p.set_fol(self.subset_list[idx+1])

    def _sort_subsetlist(self):
        """summary
            Private method. Sorts the subset_list
        """
        if len(self.subset_list) > 0:
            item_starts = self.sub_starts
            item_order = np.argsort(item_starts)
            self.subset_list = [self.subset_list[idx] for idx in item_order]
        
        self.contains = self.subset_list

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

class SequenceInterval(InstanceMixins, InTierMixins, PrecedenceMixins, HierarchyPart):
    """
    A class to describe an interval with precedence relationships and hierarchical relationships

    Args:
        Interval: A Praat textgrid Interval

    Attributes:
        start (float):
            Start time of the interval
        end (float):
            End time of the interval
        label (Any):
            Label of the interval
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
        subset_list (List[SequenceInterval]): 
            A list of subset instances. Cannot be the same subclass of the current instance.
        sub_starts (numpy.ndarray):
            A numpy array of start times for the subset list
        sub_ends (numpy.ndarray):
            A numpy array of end times for the subset list
        sub_labels (List[Any]):
            A list of labels from the subset list
    """    

    # utilities
    def __init__(
        self, 
        Interval: Interval = Interval(None, None, None)
    ):
        super().__init__()
        if not Interval:
            Interval = Interval(None, None, None)
        self.start = Interval.start
        self.end = Interval.end
        self.label = Interval.label
        
        self.fol = None
        self.prev = None

        ## prevent infinite recursion
        if self.label != "#":
            self.set_final()
        if self.label != "#":
            self.set_initial()

        self.subset_list = []
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
        if subset_instance in self.subset_list:
            pop_idx = self.index(subset_instance)
            self.subset_list.pop(pop_idx)
            self._set_subset_precedence()
        else:
            raise Exception("Subset instance not in subset list")
    
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
        if len(self.subset_list) > 0:
            start_arr = np.array([
                seg.start for seg in self.subset_list
            ])
            return start_arr
        else:
            return np.array([])
        
    @property
    def sub_ends(self):
        if len(self.subset_list) > 0:
            end_arr = np.array([
                seg.end for seg in self.subset_list
            ])
            return end_arr
        else:
            return np.array([])
    
    @property
    def sub_labels(self):
        if len(self.subset_list) > 0:
            lab_list = [seg.label for seg in self.subset_list]
            return lab_list
        else:
            return []
        
    def _shift(self, increment):
        self.start += increment
        self.end += increment
      
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

            new_list = fuser.subset_list + fusee.subset_list
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

            new_list = fusee.subset_list + fuser.subset_list
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
