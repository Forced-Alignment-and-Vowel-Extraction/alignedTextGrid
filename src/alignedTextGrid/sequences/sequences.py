"""
Module includes the `SequenceInterval` base class as well as 
`Top` and `Bottom` classes.
"""

from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from typing import Type
import numpy as np
import inspect
import warnings
class SequenceInterval:
    """
    A class to describe an interval with precedence relationships and hierarchical relationships

    Parameters:
        Interval: A Praat textgrid Interval

    Attributes:
        start (float):
            Start time of the interval
        end (float):
            End time of the interval
        label (Any):
            Label of the interval
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
        [] :
            Indexes into the `subset_list`
    """    

    # Ultimately, both of these class variables should be be
    # set to subclasses of SequenceInterval, but that can't be
    # done in the class definition since those subclasses
    # can't exist until after both SequenceVariable
    # and those subclasses have been created.
    superset_class = None
    subset_class = None

    # utilities
    def __init__(
        self, 
        Interval: Interval = Interval(None, None, None)
    ):
        if not Interval:
            Interval = Interval(None, None, None)
        self.start = Interval.start
        self.end = Interval.end
        self.label = Interval.label
        self.subset_list = []
        self.super_instance= None

    def __contains__(self, item):
        return item in self.subset_list

    def __getitem__(self, idx):
        return self.subset_list[idx]

    def __iter__(self):
        self.current = 0
        return self
    
    def __len__(self):
        return len(self.subset_list)
    
    def __len__(self):
        return len(self.subset_list)
    
    def __next__(self):
        if self.current < len(self.subset_list):
            this_seg = self.subset_list[self.current]
            self.current+=1
            return this_seg
        else:
            raise StopIteration
    
    def __repr__(self) -> str:
        out_string = f"Class {self.__class__.__name__}, label: {self.label}"
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
    
    # Hierarchy methods
    ## Superset Methods

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
        if superset_class:
            if not cls is Top:
                if issubclass(superset_class, SequenceInterval):
                    if not superset_class is cls:
                        cls.superset_class = superset_class
                        if not superset_class.subset_class is cls:
                            superset_class.set_subset_class(cls)
                    else:
                        raise Exception(f"Sequence {cls.__name__} can't have {superset_class.__name__} as its superset class.")
                else:
                    raise Exception(f"Sequence {cls.__name__} superset_class must be subclass of SequenceInterval. {superset_class.__name__} was given.")
            else:
                cls.superset_class = None

    def set_super_instance(self, super_instance = None):
        """_Sets the specific superset relationship_

        Args:
            super_instance (SegmentInterval, optional): 
                Sets the superset relationship between this object and `super_instance` object.
                Current object is appended to `super_instance`'s subset list.
        """

        ## I know this isn't best practice
        ## but for some reason just having 
        ## `if super_instance` breaks with 
        ## __len__ defined that uses self.subset_list ...
        if not super_instance is None:
            if isinstance(super_instance, self.superset_class):
                if not super_instance is self.super_instance:
                    self.super_instance = super_instance
                    self.super_instance.append_subset_list(self)
            else:
                raise Exception(f"The superset_class was defined as {self.superset_class.__name__}, but provided super_instance was {super_instance.__class__.__name__}")
        else:
            warnings.warn("No superset instance provided")                

    ## Subset Methods
    @classmethod
    def set_subset_class(cls, subset_class = None):
        """_summary_

        Args:
            subset_class (Type[SequenceInterval], optional): 
                Must be a subclass of SequenceInterval, but not the *same* as the current instance.
                Defaults to None.
        """
        if subset_class:
            if not cls is Bottom:
                if issubclass(subset_class, SequenceInterval):
                    if not subset_class is cls:
                        cls.subset_class = subset_class
                        if not subset_class.superset_class == cls:
                            subset_class.set_superset_class(cls)
                    else:
                        raise Exception(f"Sequence {cls.__name__} can't have {subset_class.__name__} as its subset class.")
                else:
                    raise Exception(f"Sequence {cls.__name__} subset_class must be subclass of SequenceInterval. {subset_class.__name__} was given.")
            else:
                cls.subset_class = None
    
    def set_subset_list(self, subset_list = None):
        """_Appends all objects to the `subset_list`_

        Args:
            subset_list (List[SequenceInterval], optional): 
                A list of SequenceInterval subclass objects. Cannot be the
                same subclass of the current object. Current object is
                set as the `super_instance` of all objects in the list.
        """
        if subset_list:
            self.subset_list = []
            if all([isinstance(subint, self.subset_class) for subint in subset_list]):
                for element in subset_list:
                    self.append_subset_list(element)
                self._set_subset_precedence()
            else:
                subset_class_set = set([x.__class__.__name__ for x in subset_list])
                raise Exception(f"The subset_class was defined as {self.subset_class.__name__}, but provided subset_list contained {subset_class_set}")
        else:
            warnings.warn("No subset list provided")

    def append_subset_list(self, subset_instance = None):
        """_Append a single item to subset list_

        Args:
            subset_instance (SequenceInterval): 
                The SequenceInterval subclass instance to append to the
                `subset_list`. Current object is set as `super_instance`
                to `subset_instance`. Precedence relationships within
                `subset_list` are reset.
        """
        ## I know this isn't best practice
        ## but for some reason just having 
        ## `if super_instance` breaks with 
        ## __len__ defined... 
        if not subset_instance is None:
            if isinstance(subset_instance, self.subset_class):
                if not subset_instance in self.subset_list:
                    self.subset_list.append(subset_instance)
                    if not self is subset_instance.super_instance:
                        subset_instance.set_super_instance(self)
                    self._set_subset_precedence()
            else:
                raise Exception(f"The subset_class was defined as {self.subset_class.__name__}, but provided subset_instance was {subset_instance.__class__.__name__}")
            
    def _set_subset_precedence(self):
        """_summary_
            Private method. Sorts subset list and re-sets precedence 
            relationshops.
        """
        self._sort_subsetlist()
        if len(self.subset_list) > 0:
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
        """_summary_
            Private method. Sorts the subset_list
        """
        if len(self.subset_list) > 0:
            item_starts = self.sub_starts
            item_order = np.argsort(item_starts)
            self.subset_list = [self.subset_list[idx] for idx in item_order]

    ### Subset Properties
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
    
    ## Subset Validation
    def validate(self) -> bool:
        """_Validate the subset list_
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
                if self.start < self.sub_starts:
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

    # Precedence Methods
    def set_fol(
            self, next_int):
        """_Sets the following instance_

        Args:
            next_int (SequenceInterval): 
                Sets the `next_int` as the `fol` interval.
                Must be of the same class as the current object.
                That is, `next_int.__class__ is self.__class__`
        """
        if next_int.__class__ is self.__class__:
            self.fol = next_int
        else:
            raise Exception(f"Following segment must be an instance of {self.__class__.__name__}")

    def set_prev(self, prev_int):
        """_Sets the previous intance_

        Args:
            prev_int (SequenceInterval):
                Sets the `prev_int` as the `prev` interval
                Must be of the same class as the current object.
                That is, `prev_int.__class__ is self.__class__`                
        """
        if prev_int.__class__ is self.__class__:
            self.prev = prev_int
        else:
            raise Exception(f"Previous segment must be an instance of {self.__class__.__name__}")
    
    def set_final(self):
        """_Sets the current object as having no `fol` interval_
        
        While `self.fol` is defined for these intervals, the actual
        instance does not appear in `self.super_instance.subset_list`
        """
        self.set_fol(self.__class__(Interval(None, None, "#")))  

    def set_initial(self):
        """_Sets the current object as having no `prev` interval_

        While `self.prev` is defined for these intervals, the actual 
        instance does not appear in `self.super_instance.subset_list`
        """
        self.set_prev(self.__class__(Interval(None, None, "#")))

    ## Extensions and Saving
    def set_feature(self, feature, value):
        """_Sets arbitrary object attribute_

        This will be most useful for creating custom subclasses.

        Args:
            feature (str): New attribute name
            value (Any): New attribute value
        """
        setattr(self, feature, value)

    def return_interval(self) -> Interval:
        """_Return current object as `Interval`_
        
        Will be useful for saving back to textgrid

        Returns:
            (praatio.utilities.constants.Interval): A `praatio` `Interval` object
        """
        return Interval(self.start, self.end, self.label)

class Top(SequenceInterval):
    """_A top level interval class_
    
    This is a special subclass intended to be the `superset_class` 
    for classes at the top of the hierarchy.

    """
    def __init__(self, Interval=Interval(None, None, None)):
        super().__init__(Interval)

class Bottom(SequenceInterval):
    """_A bottom level interval class_

    This is a special subclass intended to be the `subset_class` 
    for classes at the bottom of the hierarchy.

    """
    def __init__(self, Interval=Interval(None, None, None)):
        super().__init__(Interval)

# This is how the default behavior of `SequenceInterval` 
# with respect to subset and superset classes is controlled
SequenceInterval.set_superset_class(Top)
SequenceInterval.set_subset_class(Bottom)