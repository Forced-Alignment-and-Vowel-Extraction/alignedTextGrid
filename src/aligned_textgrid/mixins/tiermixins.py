from difflib import SequenceMatcher
from aligned_textgrid.mixins.mixins import SequenceBaseClass
from functools import reduce
import re
import warnings
import numpy as np
import sys
from collections.abc import Sequence
if sys.version_info >= (3,11):
    from typing import Self
else:
    from typing_extensions import Self

from typing import TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from aligned_textgrid import SequenceInterval, \
        SequencePoint, \
        SequenceTier, \
        SequencePointTier,\
        TierGroup,\
        PointsGroup

TierType = TypeVar("TierType", 'SequenceTier', 'SequencePointTier')
TierGroupType = TypeVar("TierGroupType", 'TierGroup', 'PointsGroup')



class TierMixins:
    """Methods and attributes for Sequence Tiers

    Attributes:
        []: indexable and iterable
        first (SequenceInterval): The first entry in the tier.
        last (SequenceInterval): The last entry in the tier.
    """
    @classmethod
    def _set_seq_type(cls, seq_type):
        cls._seq_type = seq_type

    def __add__(self:TierType, new:TierType):
        if not isinstance(new, self.__class__):
            msg = f"A {type(self).__name__} can only be added to a {type(self).__name__}."
            if isinstance(new, SequenceBaseClass):
                msg += " Did you mean to use append()?"
            raise ValueError(msg)
        if not (issubclass(self.entry_class, new.entry_class) or issubclass(new.entry_class, self.entry_class)):
            raise ValueError("Added tiers must have the same entry class")
        
        entries = self.sequence_list + new.sequence_list
        new_tier = self.__class__(entries)
        return new_tier

    def append(self, new:'SequenceInterval|SequencePoint', re_relate = True):
        """Append a new SequenceInterval or Sequence Point to a tier.

        If the tier is already in a TierGroup, and an appended SequenceInterval
        already has a subset_list, or super_instance, these will be appended to the
        appropriate tiers above and below.

        Examples:
            ```{python}
            from aligned_textgrid import SequenceTier, TierGroup, Word, Phone

            word_tier = SequenceTier([     # <1>
                Word((0,10, "the"))        # <1>
            ])                             # <1>
            phone_tier = SequenceTier([    # <1>
                Phone((0,5,"DH")),         # <1>
                Phone((5,10, "AH0"))       # <1>
            ])                             # <1>

            tier_group = TierGroup([word_tier, phone_tier]) # <2>

            dog = Word((10, 25, "dog"))         # <3>
            dog.append(Phone((10,15, "D")))     # <3>
            dog.append(Phone((15, 20, "AO1")))  # <3>
            dog.append(Phone((20,25, "G")))     # <3>

            word_tier.append(dog)               # <4>

            print(phone_tier.labels)            # <5>
            ```
            1. Creation of  Word and Phone tier containing "the" and its phones.
            2. Relating the Word and Phone tiers within a tier group.
            3. Creating a Word for "dog" and appending its phones.
            4. Appending the "dog" word to the Word tier.
            5. The phones of "dog" have been automatically appended to the Phone tier.

        Args:
            new (SequenceInterval|SequencePoint): 
                The SequenceInterval or SequencePoint object to append
            re_relate (bool, optional): 
                If the tier is already within a TierGroup, whether or not 
                to re-run tier-relation. Defaults to True.
        """
        if not isinstance(new, SequenceBaseClass):
            msg = "Only SequenceIntervals or SequencePoints can be appended to a tier."
            if isinstance(new, TierMixins):
                msg += " Did you mean to add (+)?"
            raise ValueError(msg)
        if not (issubclass(self.entry_class, new.entry_class)
                or issubclass(new.entry_class, self.entry_class)):
            raise ValueError("Entry class must match for appended values.")

        if new in self:
            return
        
        ## triggers precedence resetting
        self.sequence_list += [new]
        if hasattr(new, "subset_list") \
           and len(new) > 0 \
           and self.within:
            down_tier = self.within_index+1
            for interval in new.subset_list:
                self.within[down_tier].append(interval, re_relate = False)
        
        if hasattr(new, "super_instance")\
           and new.super_instance \
           and self.within:
            uptier  = self.within_index-1
            self.within[uptier].append(new.super_instance, re_relate = False)
            
        if self.within and re_relate:
            self.within.re_relate()



    def concat(self:TierType, new:TierType):
        """Horizontally concatenate a new tier.

        This will horizontally concatenate the `new` tier onto the existing tier.
        The time values of `new` will be rightward shifted according to the 
        end of the original tier.

        Args:
            new (TierType): 
                The tier to concatenate.
        """
        if not (issubclass(self.entry_class, new.entry_class) or issubclass(new.entry_class, self.entry_class)):
            raise ValueError("Added tiers must have the same entry class")
        
        lhs = self.sequence_list
        rhs = new.sequence_list

        lhs.concat(rhs)

        self.sequence_list = lhs

    @property
    def first(self) -> 'SequenceInterval|SequencePoint':
        if hasattr(self, "sequence_list") and len(self.sequence_list) > 0:
            return self.sequence_list[0]
        if hasattr(self, "sequence_list"):
            raise IndexError(f"{type(self).__name__} tier with name"\
                             f" {self.name} has empty sequence_list")
        raise AttributeError(f"{type(self).__name__} is not indexable.")

    @property
    def last(self)->'SequenceInterval|SequencePoint':
        if hasattr(self, "sequence_list") and len(self.sequence_list) > 0:
            return self.sequence_list[-1]
        if hasattr(self, "sequence_list"):
            raise IndexError(f"{type(self).__name__} tier with name"\
                             f" {self.name} has empty sequence_list")
        raise AttributeError(f"{type(self).__name__} is not indexable.")
    

    

class TierGroupMixins:
    """Methods and attributes for grouped tiers

    Attributes:
        []: Indexable and iterable
    """
    @classmethod
    def _set_seq_type(cls, seq_type):
        cls._seq_type = seq_type

    def _class_check(self:TierGroupType, new:TierGroupType):
        if len(self) != len(new):
            raise ValueError("Original TierGroup and new TierGroup must have the same number of tiers.")
        
        orig_classes = [x.__name__ for x in self.entry_classes]
        new_classes = [x.__name__ for x in new.entry_classes]

        for o, n  in zip(orig_classes, new_classes):
            if o != n:
                raise ValueError("Entry classes must be the same between added tier groups")

    def __add__(self:TierGroupType, new:TierGroupType):

        self._class_check(new)
            
        new_tiers = [
            t1 + t2 for t1, t2 in zip(self, new)
        ]

        new_tg = self.__class__(new_tiers)
        new_tg.name = self.name

        return new_tg
        
    def append(self:TierGroupType, new:TierType):
        """Append a new tier to a TierGroup.

        This will add a new tier to a TierGroup

        Examples:
            ```{python}
            from aligned_textgrid import TierGroup, SequenceTier, Word, Phone

            word_tier = SequenceTier([
                Word((0,10,"the"))
            ])
            phone_tier = SequenceTier([
                Phone((0,5,"DH")),
                Phone((5,10,"AH0"))
            ])

            tier_group = TierGroup([word_tier])
            tier_group.append(phone_tier)
            ```

        Args:
            new (TierType): 
                A SequenceTier if a TierGroup, or a SequencePointTier if a PointsGroup
        """
        if not self._seq_type is new._seq_type:
            raise ValueError((
                f"Only a tier of {self._seq_type.__name__} "
                f"can be appended to a {self.__class__.__name__}"
            ))
        
        if self.within:
            self.within._reclone_classes([new.entry_class])
            new_class, = self.within._swap_classes([new.entry_class], self.within._cloned_classes)
            new.__init__(new, entry_class=new_class)
        
        possible_set = {SequenceBaseClass}
        existing_set = set()
        if len(self) > 0:
            if hasattr(self[0], "subset_class"):
                possible_classes = [
                    [tier.subset_class, tier.superset_class]
                    for tier in self
                ]
                possible_flat = [cl for gr in possible_classes for cl in gr]
                possible_set = set(possible_flat)

            existing_set = {tier.entry_class for tier in self}

        existing_matches = [
            issubclass(cl, new.entry_class) or issubclass(new.entry_class, cl)
            for cl in existing_set
        ]

        if any(existing_matches):
            raise ValueError((
                f"This {self.__class__.__name__} already has a "
                f"{new.entry_class.__name__} tier"
            ))

        possible_matches = [
            issubclass(cl, new.entry_class) or issubclass(new.entry_class, cl)
            for cl in possible_set
        ]

        if not any(possible_matches):
            raise ValueError((
                f"A tier with {new.entry_class.__name__} entry class "
                "does not fit into the sequence hierarchy."
            ))

        orig_tiers = self.tier_list
        orig_tiers += [new]

        self.__init__(orig_tiers)
        

        pass

    def concat(self:TierGroupType, new:TierType):
        """Horizontally concatenate a tier group.

        The two tier groups must have the same number of tiers and the same
        entry classes. All time values of `new` will be rightward shifted
        according to the original TierGroup or PointsGroup.


        Args:
            new (TierGroupType):
                A TierGroup or PointsGroup to append.
        """
        self._class_check(new)
        increment = self.xmax
        for t1, t2 in zip(self, new):
            for interval in t2:
                if interval.super_instance is not None:
                    continue
                if interval in t1:
                    continue
                interval._shift(increment)
                t1.append(interval)



    def _set_tier_names(self):
        entry_class_names = [x.__name__ for x in self.entry_classes]
        duplicate_names = [
            name 
            for name in entry_class_names 
            if entry_class_names.count(name)>1
        ]

        if len(duplicate_names) > 0:
            warnings.warn(
                (
                    f"Some tiers have the same entry class {set(duplicate_names)}. "
                    "Named accessors will be unavailable."
                 )
            )
            return

        for idx, name in enumerate(entry_class_names):
            setattr(self, name, self.tier_list[idx])

    @property
    def name(self):
        if self._name:
            return self._name
        
        self._name = self.make_name()
        return self._name
        
    @name.setter
    def name(self, name):
        self._name = name

    def re_relate(self):
        self.__init__(self)
    
    def get_longest_name_string(
            self,
            a: str,
            b: str
        ):
        matches = SequenceMatcher(a=a, b=b).get_matching_blocks()
        longest_match = matches[0]
        if longest_match.size < 1:
            return ''
        
        out_str = a[longest_match.a:(longest_match.a + longest_match.size)]
        return out_str
    
    def make_name(self):
        tier_names = [x.name for x in self.tier_list]
        name_candidate = reduce(self.get_longest_name_string, tier_names)
        name_candidate = re.sub(r"^[\s_-]+|[\s_-]+$", '', name_candidate)
        name_candidate = re.sub(r"\W", "_", name_candidate)

        if len(name_candidate) > 1:
            return name_candidate
        
        try: 
            return f"group_{self.within.index(self)}"
        except:
            return None