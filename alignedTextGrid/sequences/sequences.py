from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
import numpy as np
import inspect
import warnings
class SequenceInterval:
    def __init__(
        self, 
        Interval = Interval(None, None, None), 
        superset_class = None,
        subset_class = None
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
    
    def set_superset_class(self, superset_class = None):
        if superset_class:
            if SequenceInterval in inspect.getmro(superset_class):
                if not superset_class.__name__ == self.__class__.__name__:
                    self.superset_class = superset_class
                else:
                    raise Exception(f"Sequence {self.__class__.__name__} can't have {superset_class.__name__} as its superset class.")
            else:
                raise Exception(f"Sequence {self.__class__.__name__} superset_class must be subclass of SequenceInterval. {superset_class.__name__} was given.")

    def set_subset_class(self, subset_class = None):
        if subset_class:
            if SequenceInterval in inspect.getmro(subset_class):
                if not subset_class.__name__ == self.__class__.__name__:
                    self.subset_class = subset_class
                else:
                    raise Exception(f"Sequence {self.__class__.__name__} can't have {subset_class.__name__} as its subset class.")
            else:
                raise Exception(f"Sequence {self.__class__.__name__} subset_class must be subclass of SequenceInterval. {subset_class.__name__} was given.")
    
    def set_super_instance(self, super_instance = None):
        if super_instance:
            if super_instance.__class__.__name__ == self.superset_class.__name__:
                if not super_instance is self.super_instance:
                    self.super_instance = super_instance
                    self.super_instance.append_subset_list(self)
            else:
                raise Exception(f"The superset_class was defined as {self.superset_class.__name__}, but provided super_instance was {super_instance.__class__.__name__}")
        else:
            warnings.warn("No superset instance provided")
    
    def set_subset_list(self, subset_list = None):
        if subset_list:
            if all([subint.__class__.__name__ == self.subset_class.__name__ for subint in subset_list]):
                for element in subset_list:
                    self.append_subset_list(element)
                self._set_subset_precedence()
            else:
                subset_class_set = set([x.__class__.__name__ for x in subset_list])
                raise Exception(f"The subset_class was defined as {self.subset_class.__name__}, but provided subset_list contained {subset_class_set}")
        else:
            warnings.warn("No subset list provided")

    def append_subset_list(self, subset_instance):
        if subset_instance:
            if subset_instance.__class__.__name__ == self.subset_class.__name__:
                if not subset_instance in self.subset_list:
                    self.subset_list.append(subset_instance)
                    if not self is subset_instance.super_instance:
                        subset_instance.set_super_instance(self)
                    self._set_subset_precedence()
            else:
                raise Exception(f"The subset_class was defined as {self.subset_class.__name__}, but provided subset_instance was {subset_instance.__class__.__name__}")
            
    def _set_subset_precedence(self):
         ## This could be a location for a check
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
        if len(self.subset_list) > 0:
            item_starts = [x.start for x in self.subset_list]
            item_order = np.argsort(item_starts)
            self.subset_list = [self.subset_list[idx] for idx in item_order]        

    def set_fol(self, next_int):
        if isinstance(next_int, self.__class__):
            self.fol = next_int
        else:
            raise Exception(f"Following segment must be an instance of {self.__class__.__name__} or Interval")

    def set_prev(self, prev_int):
        if isinstance(prev_int, self.__class__):
            self.prev = prev_int
        else:
            raise Exception(f"Previous segment must be an instance of {self.__class__.__name__} or Interval")
    
    def set_final(self):
        self.set_fol(self.__class__(Interval(None, None, "#")))  

    def set_initial(self):
        self.set_prev(self.__class__(Interval(None, None, "#")))

    def set_feature(self, feature, value):
        setattr(self, feature, value)

    def return_interval(self):
        return Interval(self.start, self.end, self.label)

class Top(SequenceInterval):
    def __init__(self, Interval=Interval(None, None, None)):
        super().__init__(Interval)

    def set_superset_class(self):
        pass

    def set_super_instance(self):
        pass

class Bottom(SequenceInterval):
    def __init__(self, Interval=Interval(None, None, None)):
        super().__init__(Interval)

    def set_subset_class(self):
        pass
    
    def set_subset_list(self):
        pass