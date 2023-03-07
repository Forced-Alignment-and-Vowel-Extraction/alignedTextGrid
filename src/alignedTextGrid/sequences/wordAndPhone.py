"""
Convenience classes for `Word` and `Phone` sequence intervals.
"""

from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from alignedTextGrid.sequences.sequences import SequenceInterval, Top, Bottom
import numpy as np


class Phone(SequenceInterval):
    
    """_A Phone subclass of SequenceInterval_

    Has all the same methods and attributes as SequenceInterval in addition
    to attributes described below. `superset_class` set to `Word`, 
    and `subset_class` set to `Bottom`

    Args:
        Interval (Interval): A praatio Inteval

    Attributes:
        inword (Word): The word instance this phone appears in.
    """
    def __init__(self, Interval = Interval(None, None, None)):
         super().__init__(Interval)

    def set_word(
            self, 
            word
        ):
        """_Convenience function to set word for this Phone_

        Args:
            word (Word): Word instance.
        """
        self.set_super_instance(word)

    @property
    def inword(self):
        return self.super_instance

class Word(SequenceInterval):
    """_A Word subclass of SequenceInterval_

    Has all the same methods and attributes as SequenceInterval in addition
    to attributes described below. `superset_class` set to `Top`, 
    and `subset_class` set to `Phone`

    Args:
        Interval (Interval): A praatio `Interval`
    
    Attributes:
        phone_list (list[Phone]): A list of Phone objects
        phones (list[str]): A list of phone labels
    """
    def __init__(
            self, 
            Interval = Interval(None, None, None)
        ):
        super().__init__(Interval)
    
    def set_phones(self, phone_list):
        """_Convenience function to set the phones_

        Args:
            phone_list (list[Phone]): List of Phone instances
        """
        self.set_subset_list(phone_list)

    @property
    def phone_list(self):
        return self.subset_list

    @property
    def phones(self):
        return self.sub_labels

Word.set_superset_class(Top)
Word.set_subset_class(Phone)
Phone.set_subset_class(Bottom)
# not necessary
# Phone.set_superset_class(Word)