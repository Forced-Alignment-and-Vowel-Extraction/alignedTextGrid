"""
Module for TextGrid tier classes that contain `SequenceInterval`s
"""

from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from praatio.data_classes.textgrid import Textgrid
from aligned_textgrid.sequences.sequences import SequenceInterval, Top, Bottom
from aligned_textgrid.mixins.tiermixins import TierMixins, TierGroupMixins
from aligned_textgrid.mixins.within import WithinMixins
import numpy as np
from typing import Type
import warnings

class SequenceTier(TierMixins, WithinMixins):
    """A sequence tier

    Given a `praatio` `IntervalTier` or list of `Interval`s, creates
    `entry_class` instances for every interval.

    Args:
        tier (list[Interval] | IntervalTier, optional): 
            A list of interval entries. Defaults to [Interval(None, None, None)].
        entry_class (Type[SequenceInterval], optional): 
            The sequence class for this tier. Defaults to SequenceInterval.
    
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
        tier: list[Interval] | IntervalTier = [],
        entry_class: Type[SequenceInterval] = SequenceInterval
    ):
        super().__init__()
        if isinstance(tier, IntervalTier):
            self.entry_list = tier.entries
            self.name = tier.name
        else:
            self.entry_list = tier
            self.name = entry_class.__name__
        self.entry_class = entry_class
        self.superset_class = self.entry_class.superset_class
        self.subset_class =  self.entry_class.subset_class
        entry_order = np.argsort([x.start for x in self.entry_list])
        self.entry_list = [self.entry_list[idx] for idx in entry_order]
        self.sequence_list = []
        for entry in self.entry_list:
            this_seq = self.entry_class(entry)
            this_seq.set_superset_class(self.superset_class)
            this_seq.set_subset_class(self.subset_class)
            self.sequence_list += [this_seq]
        self.__set_precedence()

    def __set_precedence(self):
        for idx,seq in enumerate(self.sequence_list):
            self.__set_intier(seq)
            if idx == 0:
                seq.set_initial()
            else:
                seq.set_prev(self.sequence_list[idx-1])
            if idx == len(self.sequence_list)-1:
                seq.set_final()
            else:
                seq.set_fol(self.sequence_list[idx+1])
        if issubclass(self.superset_class, Top):
            self.contains = self.sequence_list

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
            pop_idx = self.index(entry)
            self.sequence_list.pop(pop_idx)
            if self.superset_class is Top:
                self.__set_precedence()
        else:
            raise Exception("Entry not in tier")                    

    def __repr__(self):
        return f"Sequence tier of {self.entry_class.__name__}; .superset_class: {self.superset_class.__name__}; .subset_class: {self.subset_class.__name__}"
    
                
    @property
    def starts(self):
        return np.array([x.start for x in self.sequence_list])

    @property
    def ends(self):
        return np.array([x.end for x in self.sequence_list])
    
    @property
    def labels(self):
        return [x.label for x in self.sequence_list]

    @property
    def xmin(self):
        if len(self.sequence_list) > 0:
            return self.sequence_list[0].start
        else:
            return None
    
    @property
    def xmax(self):
        if len(self.sequence_list) > 0:
            return self.sequence_list[-1].end
        else:
            return None

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


class TierGroup(TierGroupMixins, WithinMixins):
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
        tiers: list[SequenceTier] = [SequenceTier()]
    ):
        super().__init__()
        self.tier_list = self._arrange_tiers(tiers)
        self.name = self.make_name()

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
        
    def __repr__(self):
        n_tiers = len(self.tier_list)
        classes = [x.__name__ for x in self.entry_classes]
        return f"TierGroup with {n_tiers} tiers. {repr(classes)}"
    
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
    