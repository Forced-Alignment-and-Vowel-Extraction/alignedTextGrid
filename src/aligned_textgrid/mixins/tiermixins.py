from difflib import SequenceMatcher
from functools import reduce
import re
import warnings

class TierMixins:
    """Methods and attributes for Sequence Tiers

    Attributes:
        []: indexable and iterable
        first (SequenceInterval): The first entry in the tier.
        last (SequenceInterval): The last entry in the tier.
    """

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
        raise AttributeError(f"{type(self).__name__} is not indexable.")\
    

class TierGroupMixins:
    """Methods and attributes for grouped tiers

    Attributes:
        []: Indexable and iterable
    """

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