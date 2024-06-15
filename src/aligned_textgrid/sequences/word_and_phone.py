"""
Convenience classes for `Word` and `Phone` sequence intervals.
"""
import aligned_textgrid
from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from aligned_textgrid.sequences.sequences import SequenceInterval, Top, Bottom
import numpy as np

class Phone(SequenceInterval):
    
    """A Phone subclass of [](`~aligned_textgrid.sequences.sequences.SequenceInterval`)

    Has all the same methods and attributes as [](`~aligned_textgrid.sequences.sequences.SequenceInterval`) 
    in addition to attributes described below. `superset_class` set to 
    [](`~aligned_textgrid.sequences.word_and_phone.Word`), 
    and `subset_class` set to [](`~aligned_textgrid.sequences.sequences.Bottom`)

    Args:
        interval (list|tuple|Interval|SequenceInterval): 
            A tuple or list of start, end and label, 
            or another [](`~aligned_textgrid.sequences.sequences.SequenceInterval`)

    Examples:
        ```{python}
        from aligned_textgrid import Word, Phone

        DH = Phone((0, 1, "DH"))
        AH0 = Phone((1, 2, "AH0"))

        THE = Word((0, 2, "THE"))

        DH.set_word(THE)
        AH0.set_word(THE)

        print(
            (
            f"The phone is {DH.label}. "
            f"The next phone is {DH.fol.label}. "
            f"It is in the word {DH.inword.label}."
            )
        )
        ```

    Attributes:
        inword (Word): The word instance this phone appears in.
    """
    def __init__(
            self, 
            interval: list|tuple|Interval|SequenceInterval= (None, None, None),
            *,  
            Interval = None
            ):
         super().__init__(interval, Interval=Interval)

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
    """A Word subclass of [](`~aligned_textgrid.sequences.sequences.SequenceInterval`)

    Has all the same methods and attributes as [](`~aligned_textgrid.sequences.sequences.SequenceInterval`) 
    in addition to attributes described below.  
    `superset_class` set to [](`~aligned_textgrid.sequences.sequences.Top`), 
    and `subset_class` set to [](`~aligned_textgrid.sequences.word_and_phone.Phone`)

    Args:
        interval (list|tuple|Interval|SequenceInterval): 
            A tuple or list of start, end and label, 
            or another [](`~aligned_textgrid.sequences.sequences.SequenceInterval`)

    Examples:
        ```{python}
        from aligned_textgrid import Word, Phone

        DH = Phone((0, 1, "DH"))
        AH0 = Phone((1, 2, "AH0"))

        THE = Word((0, 2, "THE"))

        THE.set_phones([DH, AH0])

        print(THE.phones)
        ```
    
    Attributes:
        phone_list (list[Phone]): A list of Phone objects
        phones (list[str]): A list of phone labels
    """
    def __init__(
            self, 
            interval: list|tuple|Interval|SequenceInterval= (None, None, None),
            *,  
            Interval = None

        ):
        super().__init__(interval, Interval=Interval)
    
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

class Top_wp(Top):
    def __init__(self):
        super.__init__()

class Bottom_wp(Bottom):
    def __init__(self):
        super.__init__()


Word.set_superset_class(Top_wp)
Word.set_subset_class(Phone)
Phone.set_subset_class(Bottom_wp)
# not necessary
# Phone.set_superset_class(Word)