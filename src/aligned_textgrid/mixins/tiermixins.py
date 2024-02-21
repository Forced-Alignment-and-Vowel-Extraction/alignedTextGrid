from difflib import SequenceMatcher
from functools import reduce
import re

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
        raise AttributeError(f"{type(self).__name__} is not indexable.")

    def __contains__(self, item):
        return item in self.sequence_list
    
    def __getitem__(self, idx):
        return self.sequence_list[idx]
    
    def __iter__(self):
        self._idx = 0
        return self

    def __len__(self):
        return len(self.sequence_list)

    def __next__(self):
        if self._idx < len(self.sequence_list):
            out = self.sequence_list[self._idx]
            self._idx += 1
            return(out)
        raise StopIteration

    def index(
            self, 
            entry
        ) -> int:
        """Return index of a tier entry

        Args:
            entry (SequencePoint |SequenceInterval):
                A SequenceInterval or a PointInterval to get the index of.

        Returns:
            (int): The entry's index
        """
        return self.sequence_list.index(entry)
    

class TierGroupMixins:
    """Methods and attributes for grouped tiers

    Attributes:
        []: Indexable and iterable
    """

    def __contains__(self, item):
        return item in self.tier_list
    
    def __getattr__(
            self,
            name: str
    ):
        entry_class_names = [x.__name__ for x in self.entry_classes]
        match_list = [x  for x in entry_class_names if x == name]

        if len(match_list) == 1:
            match_idx = entry_class_names.index(name)
            self.__setattr__(name, self.tier_list[match_idx])
            return self.tier_list[match_idx]
        
        if len(match_list) > 1:
            raise AttributeError(f"{type(self).__name__} has multiple entry classes for {name}")
        
        if len(match_list) < 1:
            raise AttributeError(f"{type(self).__name__} has no attribute {name}")
    
    def __getitem__(
            self,
            idx: int|list
    ):
        if type(idx) is int:
            return self.tier_list[idx]
        if len(idx) != len(self):
            raise Exception("Attempt to index with incompatible list")
        if type(idx) is list:
            out_list = []
            for x, tier in zip(idx, self.tier_list):
                out_list.append(tier[x])
            return(out_list)
    
    def __iter__(self):
        self._idx = 0
        return self

    def __len__(self):
        return len(self.tier_list)

    def __next__(self):
        if self._idx < len(self.tier_list):
            out = self.tier_list[self._idx]
            self._idx += 1
            return(out)
        raise StopIteration
    
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