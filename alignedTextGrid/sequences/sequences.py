from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
import numpy as np
import inspect
import warnings
class SequenceInterval:
    def __init__(
        self, 
        Interval = Interval(None, None, None), 
        focus = True
    ):
        self.start = Interval.start
        self.end = Interval.end
        self.label = Interval.label
        if focus:
            self.fol = self.__class__(focus=False)
            self.prev = self.__class__(focus=False)
        
        self.superset_class = None
        self.subset_class = None
        self.super_instance = None
        self.subset_list = None

    def set_superset_class(self, superset_class = None):
        if superset_class:
            if isinstance(superset_class, SequenceInterval):
                if not superset_class.__class__.__name__ == self.__class__.__name__:
                    self.superset_class = superset_class
                else:
                    raise Exception(f"Sequence {self.__class__.__name__} can't have {superset_class.__class__.__name__} as its superset class.")
            else:
                raise Exception(f"Sequence {self.__class__.__name__} superset_class must be subclass of SequenceInterval. {superset_class.__class__.__name__} was given.")

    def set_subset_class(self, subset_class = None):
        if subset_class:
            if isinstance(subset_class, SequenceInterval):
                if not subset_class.__class__.__name__ == self.__class__.__name__:
                    self.subset_class = subset_class
                else:
                    raise Exception(f"Sequence {self.__class__.__name__} can't have {subset_class.__class__.__name__} as its subset class.")
            else:
                raise Exception(f"Sequence {self.__class__.__name__} subset_class must be subclass of SequenceInterval. {subset_class.__class__.__name__} was given.")
    
    def set_super_instance(self, super_instance = None):
        if super_instance:
            if isinstance(super_instance, self.superset_class.__class__):
                self.super_instance = super_instance
            else:
                raise Exception(f"The superset_class was defined as {self.superset_class.__class__.__name__}, but provided super_instance was {super_instance.__class__.__name__}")
        else:
            warnings.warn("No superset instance provided")
    
    def set_subset_list(self, subset_list = None):
        if subset_list:
            if all([isinstance(subint, self.subset_class.__class__) for subint in subset_list]):
                self.subset_list = subset_list
                for element in subset_list:
                    element.set_super_instance(self)
                for idx, p in enumerate(self.subset_list):
                    if idx == 0:
                        p.set_initial()
                    else:
                        p.set_prev(self.subset_list[idx-1])
                    if idx == len(self.subset_list)-1:
                        p.set_final()
                    else:
                        p.set_fol(self.subset_list[idx+1])
            else:
                subset_class_set = set([x.__class__.__name__ for x in subset_list])
                raise Exception(f"The subset_class was defined as {self.subset_class.__class__.__name__}, but provided subset_list contained {subset_class_set}")
        else:
            warnings.warn("No subset list provided")        

    def set_fol(self, next_int):
        if isinstance(next_int, self.__class__):
            self.fol = next_int
        elif isinstance(next_int, Interval):
            self.fol = self.__class__(next_int, focus = False)
        else:
            raise Exception(f"Following segment must be an instance of {self.__class__.__name__} or Interval")

    def set_prev(self, prev_int):
        if isinstance(prev_int, self.__class__):
            self.prev = prev_int
        elif isinstance(prev_int, Interval):
            self.prev = self.__class__(prev_int, focus = False)
        else:
            raise Exception(f"Previous segment must be an instance of {self.__class__.__name__} or Interval")
    
    def set_final(self):
        self.set_fol(Interval(None, None, "#"))  

    def set_initial(self):
        self.set_prev(Interval(None, None, "#"))

    def set_feature(self, feature, value):
        setattr(self, feature, value)

    def return_interval(self):
        return Interval(self.start, self.end, self.label)
