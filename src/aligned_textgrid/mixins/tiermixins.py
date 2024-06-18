from difflib import SequenceMatcher
from functools import reduce
import re
import warnings
import numpy as np

class TierMixins:
    """Methods and attributes for Sequence Tiers

    Attributes:
        []: indexable and iterable
        first (SequenceInterval): The first entry in the tier.
        last (SequenceInterval): The last entry in the tier.
    """

    def __add__(self, new):
        if not isinstance(new, self.__class__):
            msg = f"A {type(self).__name__} can only be added to a {type(self).__name__}."
            if isinstance(new, PrecedenceMixins):
                msg += " Did you mean to use append()?"
            raise ValueError(msg)
        if not issubclass(self.entry_class, new.entry_class):
            raise ValueError("Added tiers must have the same entry class")
        
        entries = self.sequence_list + new.sequence_list
        new_tier = self.__class__(entries)
        return new_tier

    def append(self, new):
        if not isinstance(new, PrecedenceMixins):
            msg = "Only SequenceIntervals or SequencePoints can be appended to a tier."
            if isinstance(new, TierMixins):
                msg += " Did you mean do add (+)?"
            raise ValueError(msg)
        if not issubclass(self.entry_class, new.entry_class):
            raise ValueError("Entry class must match for appended values.")
        
        entries = self.sequence_list
        entries.append(new)
        new_tier = self.__class__(entries)
        orig_within = self.within
        self = new_tier
        orig_within.re_relate()

    def concat(self, new):
        if self.entry_class.__name__ != new.entry_class.__name__:
            raise ValueError("Added tiers must have the same entry class")
        
        lhs = self.sequence_list
        rhs = new.sequence_list

        lhs.concat(rhs)

        self.sequence_list = lhs

    @property
    def first(self):
        if hasattr(self, "sequence_list") and len(self.sequence_list) > 0:
            return self.sequence_list[0]
        if hasattr(self, "sequence_list"):
            raise IndexError(f"{type(self).__name__} tier with name"\
                             f" {self.name} has empty sequence_list")
        raise AttributeError(f"{type(self).__name__} is not indexable.")

    @property
    def last(self):
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

    def _class_check(self, new):
        if len(self) != len(new):
            raise ValueError("Original TierGroup and new TierGroup must have the same number of tiers.")
        
        orig_classes = [x.__name__ for x in self.entry_classes]
        new_classes = [x.__name__ for x in new.entry_classes]

        for o, n  in zip(orig_classes, new_classes):
            if o != n:
                raise ValueError("Entry classes must be the same between added tier groups")

    def __add__(self, new):

        self._class_check(new)
            
        new_tiers = [
            t1 + t2 for t1, t2 in zip(self, new)
        ]

        new_tg = self.__class__(new_tiers)
        new_tg.name = self.name

        return new_tg
        


    def concat(self, new):
        self._class_check(new)

        _ = [
            t1.concat(t2) for t1, t2 in zip(self, new)
        ]



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