"""
Module for TextGrid tier classes that contain `SequenceInterval`s
"""

from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from praatio.data_classes.textgrid import Textgrid
from aligned_textgrid.sequences.sequences import SequenceInterval, Top, Bottom
from aligned_textgrid.sequence_list import SequenceList
from aligned_textgrid.mixins.tiermixins import TierMixins, TierGroupMixins
from aligned_textgrid.mixins.within import WithinMixins
import numpy as np
from typing import Type
from collections.abc import Sequence

import sys
if sys.version_info >= (3,11):
    from typing import Self
else:
    from typing_extensions import Self

import warnings

class SequenceTier(Sequence, TierMixins, WithinMixins):
    """A sequence tier

    Given a `praatio` `IntervalTier` or list of `Interval`s, creates
    `entry_class` instances for every interval.

    Args:
        tier (list[Interval] | list[SequenceInterval] | IntervalTier | Self, optional): 
            A list of interval entries. Defaults to `[]`.
        entry_class (Type[SequenceInterval], optional): 
            The sequence class for this tier. Defaults to SequenceInterval.

    Examples:
        ```{python}
        from aligned_textgrid import SequenceInterval, Word, SequenceTier

        the = Word((0,1, "the"))
        dog = Word((0,1,"dog"))

        word_tier = SequenceTier([the, dog])

        print(word_tier)
        ```

        ```{python}
        print(word_tier.sequence_list)
        ```
    
    Attributes:
        sequence_list (list[SequenceInterval]):
        entry_class (Type[SequenceInterval]):
        superset_class (Type[SequenceInterval]):
        subset_class (Type[SequenceInterval]):
        starts (np.ndarray[np.float64]):
        ends (np.ndarray[np.float64]):
        labels (list[str]): 
        xmin (float):
        xmax (float):
        name (str):
        [] : Indexable. Returns a SequenceInterval
        : Iterable
    """
    def __init__(
        self,
        tier: list[Interval] | list[SequenceInterval] | SequenceList | IntervalTier | Self  = SequenceList(),
        entry_class: Type[SequenceInterval] = None
    ):
        
        to_check = tier
        if isinstance(tier, IntervalTier):
            to_check = tier.entries

        has_class = any([hasattr(x, "entry_class") for x in to_check]) 

        if not entry_class and has_class:
            entry_class = tier[0].entry_class
        
        if not entry_class and not has_class:
            entry_class = SequenceInterval
        
        name = entry_class.__name__
        entries = tier

        if isinstance(tier, IntervalTier):
            entries = tier.entries
            name = tier.name
        if isinstance(tier, SequenceTier):
            entries = tier.sequence_list
            if tier.name != tier.entry_class.__name__:
                name = tier.name            

        self.entry_list = entries
        self.name = name
        self._sequence_list = SequenceList()
        self.__set_classes(entry_class)
        self.__build_sequence_list()
        self.__set_precedence()

    def __set_classes(
            self,
            entry_class
    ):
        self.entry_class = entry_class
        self.superset_class = self.entry_class.superset_class
        self.subset_class =  self.entry_class.subset_class
        
    def __build_sequence_list(self):
        intervals = [self.entry_class._cast(entry) for entry in self.entry_list]
        self.sequence_list = SequenceList(*intervals)


    def __getitem__(self, idx):
        return self.sequence_list[idx]

    def __len__(self):
        return len(self.sequence_list)


    def __set_precedence(self):
        for idx,seq in enumerate(self._sequence_list):
            self.__set_intier(seq)
            if idx == 0:
                seq.set_initial()
            else:
                seq.set_prev(self._sequence_list[idx-1])
            if idx == len(self._sequence_list)-1:
                seq.set_final()
            else:
                seq.set_fol(self._sequence_list[idx+1])
        if issubclass(self.superset_class, Top):
            self.contains = self._sequence_list

    def __set_intier(
            self,
            entry
        ):
        """
        Sets the intier attribute of the entry
        """
        entry.intier = self
        entry.tiername = self.name
    
    def pop(
            self,
            entry
    ):
        """Pop an interval

        Args:
            entry (SequenceInterval): Interval to pop

        """
        if entry in self.sequence_list:
            self.sequence_list.remove(entry)
            if self.superset_class is Top:
                self.__set_precedence()
        else:
            raise Exception("Entry not in tier")                    

    def __repr__(self):
        return f"Sequence tier of {self.entry_class.__name__}; .superset_class: {self.superset_class.__name__}; .subset_class: {self.subset_class.__name__}"
    
    @property
    def sequence_list(self):
        return self._sequence_list
    
    @sequence_list.setter
    def sequence_list(self, new):
        self._sequence_list = SequenceList(*new)
        self.__set_precedence()        

    @property
    def starts(self):
        return np.array([x.start for x in self.sequence_list])
    
    @starts.setter
    def starts(self, times):
        if not len(self.sequence_list) == len(times):
            raise Exception("There aren't the same number of new start times as intervals")
        
        for t, i in zip(times, self.sequence_list):
            i.start = t

    @property
    def ends(self):
        return np.array([x.end for x in self.sequence_list])

    @ends.setter
    def ends(self, times):
        if not len(self.sequence_list) == len(times):
            raise Exception("There aren't the same number of new start times as intervals")
        
        for t, i in zip(times, self.sequence_list):
            i.end = t

    def _shift(self, increment):
        self.starts += increment
        self.ends   += increment

    @property
    def labels(self):
        return [x.label for x in self.sequence_list]

    @property
    def xmin(self):
        if len(self.sequence_list) > 0:
            return self.sequence_list.starts.min()
        else:
            return None
    
    @property
    def xmax(self):
        if len(self.sequence_list) > 0:
            return self.sequence_list.ends.max()
        else:
            return None

    def cleanup(self):
        """
        Insert empty intervals where there are gaps in the existing tier.
        """
        existing_intervals = self.sequence_list
        for i in range(len(existing_intervals)):
            if i+1 == len(existing_intervals):
                break

            this_end = existing_intervals[i].end
            next_start = existing_intervals[i+1].start
            
            if np.allclose(this_end, next_start):
                continue

            self.sequence_list.append(
                self.entry_class((this_end, next_start, ""))
            )

        if self.within:
            self.within.re_relate()

    def get_interval_at_time(
            self, 
            time: float
        ) -> int:
        """Gets interval index at specified time

        Args:
            time (float): time at which to get an interval

        Returns:
            (int): Index of the interval
        """
        out_idx = np.searchsorted(self.starts, time, side = "left") - 1
        if np.allclose(self.starts[out_idx+1], time):
            out_idx = out_idx+1
        return out_idx
    
    def return_tier(self) -> IntervalTier:
        """Returns a `praatio` interval tier

        Returns:
            (praatio.data_classes.interval_tier.IntervalTier):
                A `praatio` interval tier. Useful for saving results
                back as a Praat TextGrid.
        """
        all_intervals = [entry.return_interval() for entry in self.sequence_list]
        interval_tier = IntervalTier(name = self.name, entries = all_intervals)
        return interval_tier

    
    def save_as_tg(
            self, 
            save_path: str
        ):
        """Saves as a textgrid

        Uses `praatio.data_classes.textgrid.Textgrid.save()` method.

        Args:
            save_path (str): Output path
        """
        interval_tier = self.return_tier()
        out_tg = Textgrid()
        out_tg.addTier(tier = interval_tier)
        out_tg.save(save_path, "long_textgrid")


class TierGroup(Sequence,TierGroupMixins, WithinMixins):
    """Tier Grouping

    Args:
        tiers (list[SequenceTier]): A list of sequence tiers that are 
            meant to be in hierarchical relationships with eachother
    
    Attributes:
        tier_list (list[SequenceTier]): List of sequence tiers that have been
            related.
        entry_classes (list[Type[SequenceInterval]]): 
            A list of the entry classes for each tier.
        tier_names (list[str]): 
            A list of tier names
        xmax (float):
            Maximum time
        xmin (float):
            Minimum time
        [] : Indexable. Returns a SequenceTier
    """
    def __init__(
        self,
        tiers: list[SequenceTier]|Self = [SequenceTier()]
    ):
        name = None        
        if hasattr(tiers, "name"):
            name = tiers.name

        if isinstance(tiers, TierGroup):
            tiers = [tier for tier in tiers]

        self.tier_list = self._arrange_tiers(tiers)

        if name:
            self._name = name
        else:
            self._name = self.make_name()
        self._set_tier_names()

        #self.entry_classes = [x.__class__ for x in self.tier_list]
        for idx, tier in enumerate(self.tier_list):
            if idx == len(self.tier_list)-1:
                break
            else:
                upper_tier = self.tier_list[idx]
                lower_tier = self.tier_list[idx+1]

                upper_starts = upper_tier.starts
                upper_ends = upper_tier.ends
                lower_starts = lower_tier.starts
                lower_ends = lower_tier.ends
                
                starts = np.searchsorted(lower_starts, upper_starts, side = "left")
                ends = np.searchsorted(lower_ends, upper_ends, side = "right")
                if not np.all(starts[1:] == ends[:-1]):
                    warnings.warn("Some intervals on subset tier have no superset instance")

                lower_sequences = [lower_tier[starts[idx]:ends[idx]] for idx,_ in enumerate(upper_tier)]
                
                for u,l in zip(upper_tier, lower_sequences):
                    u.set_subset_list(l)
                    u.validate()
    
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

    def __len__(self):
        return len(self.tier_list)
        
    def __repr__(self):
        n_tiers = len(self.tier_list)
        classes = [x.__name__ for x in self.entry_classes]
        return f"TierGroup with {n_tiers} tiers. {repr(classes)}"
    
        
    def __setstate__(self, d):
        self.__dict__ = d
    
    def _arrange_tiers(
            self, 
            tiers: list[SequenceTier]
        ) -> list[SequenceTier]:
        """_Arranges tiers by hierarchy_

        Args:
            tiers (list[SequenceTier]): _description_
        """
        top_to_bottom = []
        tier_classes = [x.entry_class for x in tiers]
        seed_tier = tiers[0]
        done = False
        while not done:
            if issubclass(seed_tier.superset_class, Top):
                top_idx = tiers.index(seed_tier)
                done = True
                break
            elif seed_tier.superset_class not in tier_classes:
                top_idx = tiers.index(seed_tier)
                done = True
                break
            else:
                next_tier_idx = tier_classes.index(seed_tier.superset_class)
                seed_tier = tiers[next_tier_idx]


        top_to_bottom.append(tiers[top_idx])
        done = False
        while not done:
            curr = top_to_bottom[-1]
            if issubclass(curr.subset_class, Bottom):
                done = True
                break
            else:
                try:
                    next_idx = [x.entry_class for x in tiers].index(curr.subset_class)
                except ValueError:
                    return top_to_bottom
                
                top_to_bottom.append(tiers[next_idx])
        self.contains = top_to_bottom
        return(top_to_bottom)
            
    @property
    def entry_classes(self):
        return [x.entry_class for x in self.tier_list]
    
    @property
    def tier_names(self):
        return [x.name for x in self.tier_list]
    
    @property
    def xmin(self):
        return np.array([tier.xmin for tier in self.tier_list]).min()
    
    @property
    def xmax(self):
        return np.array([tier.xmax for tier in self.tier_list]).min()
    
    def cleanup(self):
        for tier in self:
            tier.cleanup()
        
   

        starts = np.array([tier.xmin for tier in self])
        ends = np.array([tier.xmax for tier in self])

        if ~np.allclose(starts.ptp(), 0.0):
            new_start = self.xmin
            
            for tier in self:
                if np.allclose(tier.xmin, new_start):
                    continue

                empty_interval = tier.entry_class((new_start, tier.xmin, ""))
                tier.append(empty_interval)
            

        
        if ~np.allclose(ends.ptp(), 0.0):
            new_end = self.xmax

            for tier in self:
                if np.allclose(tier.xmax, new_end):
                    continue
                
                empty_interval = tier.entry_class((tier.xmax, new_end, ""))
                tier.append(empty_interval)

        self = TierGroup(self)


    def shift(
            self,
            increment: float
        ):
        """Shift the start and end times of all intervals within
        the TierGroup by the increment size

        Args:
            increment (float): 
                The time increment by which to shift the
                intervals within the TierGroup. Could be
                positive or negative
        """
        for tier in self.tier_list:
            tier._shift(increment)

    def get_intervals_at_time(
            self, 
            time: float
        ) -> list[int]:
        """Get intervals at time

        Returns a list of intervals at `time` for each tier.

        Args:
            time (float): Time in intervals

        Returns:
            (list[int]): A list of interval indices, one for each tier in `tier_list`
        """
        return [tier.get_interval_at_time(time) for tier in self.tier_list]

    def show_structure(self):
        """Show the hierarchical structure
        """
        tab = "  "
        for idx, tier in enumerate(self.tier_list):
            if idx == 0:
                print(f"{tier.superset_class.__name__}(\n")
            print(f"{tab*(idx+1)}{tier.entry_class.__name__}(\n")
            if idx == len(self.tier_list)-1:
                print(f"{tab*(idx+2)}{tier.subset_class.__name__}(\n")
    