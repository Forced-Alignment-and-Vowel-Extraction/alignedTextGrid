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
        superset_class (Type[SequenceInterval]): The superset class. Defaults to `Top`
        subset_class (Type[SequenceInterval]): The subset class. Defaults to `Bottom`

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

    # utilities
    def __init__(
        self, 
        Interval: Interval = Interval(None, None, None), 
        superset_class: type = None,
        subset_class: type = None
    ):
        if not Interval:
            Interval = Interval(None, None, None)
        self.start = Interval.start
        self.end = Interval.end
        self.label = Interval.label
        
        if superset_class:
            self.set_superset_class(superset_class)
        else:
            self.set_superset_class(Top)
        if subset_class:
            self.set_subset_class(subset_class)
        else:
            self.set_subset_class(Bottom)

        self.subset_list = []
        self.super_instance= None

    def __iter__(self):
        self.current = 0
        return self
    
    def __next__(self):
        if self.current < len(self.subset_list):
            this_seg = self.subset_list[self.current]
            self.current+=1
            return this_seg
        else:
            raise StopIteration

    def __getitem__(self, idx):
        return self.subset_list[idx]

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
                sub_labels = [x.label for x in self.subset_list]
                out_string += f", .subset_list: {repr(sub_labels)}"
        else:
            out_string += ", .subset_class: None"
        return out_string
    
    # Hierarchy methods
    ## Superset Methods
    def set_superset_class(
            self, 
            superset_class: type = None
        ):
        """_Set the superset class_

        Args:
            superset_class (Type[SequenceInterval], optional): 
                Must be a subclass of Sequence Interval, but not the *same* class as the
                current instance. Defaults to None.

        """
        if superset_class:
            if not self.__class__ is Top:
                if issubclass(superset_class, SequenceInterval):
                    if not superset_class is self.__class__:
                        self.superset_class = superset_class
                    else:
                        raise Exception(f"Sequence {self.__class__.__name__} can't have {superset_class.__name__} as its superset class.")
                else:
                    raise Exception(f"Sequence {self.__class__.__name__} superset_class must be subclass of SequenceInterval. {superset_class.__name__} was given.")
            else:
                self.superset_class = None

    def set_super_instance(self, super_instance = None):
        """_Sets the specific superset relationship_

        Args:
            super_instance (SegmentInterval, optional): 
                Sets the superset relationship between this object and `super_instance` object.
                Current object is appended to `super_instance`'s subset list.
        """
        if super_instance:
            if isinstance(super_instance, self.superset_class):
                if not super_instance is self.super_instance:
                    self.super_instance = super_instance
                    self.super_instance.append_subset_list(self)
            else:
                raise Exception(f"The superset_class was defined as {self.superset_class.__name__}, but provided super_instance was {super_instance.__class__.__name__}")
        else:
            warnings.warn("No superset instance provided")                

    ## Subset Methods
    def set_subset_class(self, subset_class = None):
        """_summary_

        Args:
            subset_class (Type[SequenceInterval], optional): 
                Must be a subclass of SequenceInterval, but not the *same* as the current instance.
                Defaults to None.
        """
        if subset_class:
            if not self.__class__ is Bottom:
                if issubclass(subset_class, SequenceInterval):
                    if not subset_class is self.__class__:
                        self.subset_class = subset_class
                    else:
                        raise Exception(f"Sequence {self.__class__.__name__} can't have {subset_class.__name__} as its subset class.")
                else:
                    raise Exception(f"Sequence {self.__class__.__name__} subset_class must be subclass of SequenceInterval. {subset_class.__name__} was given.")
            else:
                self.subset_class = None
    
    def set_subset_list(self, subset_list = None):
        """_Appends all objects to the `subset_list`_

        Args:
            subset_list (List[SequenceInterval], optional): 
                A list of SequenceInterval subclass objects. Cannot be the
                same subclass of the current object. Current object is
                set as the `super_instance` of all objects in the list.
        """
        if subset_list:
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

        if subset_instance:
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
            item_starts = [x.start for x in self.subset_list]
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
              

    # Precedence Methods
    def set_fol(self, next_int):
        """_Sets the following instance_

        Args:
            next_int (SequenceInterval): 
                Sets the `next_int` as the `fol` interval.
        """
        if isinstance(next_int, self.__class__):
            self.fol = next_int
        else:
            raise Exception(f"Following segment must be an instance of {self.__class__.__name__} or Interval")

    def set_prev(self, prev_int):
        """_Sets the previous intance_

        Args:
            prev_int (SequenceInterval):
                Sets the `prev_int` as the `prev` interval
        """
        if isinstance(prev_int, self.__class__):
            self.prev = prev_int
        else:
            raise Exception(f"Previous segment must be an instance of {self.__class__.__name__} or Interval")
    
    def set_final(self):
        """_Sets the current object as having no `fol` interval_
        """
        self.set_fol(self.__class__(Interval(None, None, "#")))  

    def set_initial(self):
        """_Sets the current object as having no `prev` interval_
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

    def return_interval(self):
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

    # def set_superset_class(self):
    #     pass

    # def set_super_instance(self):
    #     pass

class Bottom(SequenceInterval):
    """_A bottom level interval class_

    This is a special subclass intended to be the `subset_class` 
    for classes at the bottom of the hierarchy.

    """
    def __init__(self, Interval=Interval(None, None, None)):
        super().__init__(Interval)

    # def set_subset_class(self):
    #     pass
    
    # def set_subset_list(self):
    #     pass