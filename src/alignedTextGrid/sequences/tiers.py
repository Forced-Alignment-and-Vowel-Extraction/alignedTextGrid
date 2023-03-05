"""
Module for TextGrid tier classes that contain `SequenceInterval`s
"""

from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from praatio.data_classes.textgrid import Textgrid
from alignedTextGrid.sequences.sequences import SequenceInterval, Top, Bottom
import numpy as np
from typing import Type
import warnings

class SequenceTier:
    """_A sequence tier_

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
        tier: list[Interval] | IntervalTier = [Interval(None, None, None)],
        entry_class: Type[SequenceInterval] = SequenceInterval
    ):
        if isinstance(tier, IntervalTier):
            self.entry_list = tier.entries
            self.name = tier.name
        else:
            self.entry_list = tier
            self.name = entry_class.__name__
        self.entry_class = entry_class
        self.superset_class = self.entry_class.superset_class
        self.subset_class =  self.entry_class.subset_class
        entry_order = np.argsort(self.starts)
        self.entry_list = [self.entry_list[idx] for idx in entry_order]
        self.sequence_list = []
        for entry in self.entry_list:
            this_seq = self.entry_class(entry)
            this_seq.set_superset_class(self.superset_class)
            this_seq.set_subset_class(self.subset_class)
            self.sequence_list += [this_seq]
        for idx,seq in enumerate(self.sequence_list):
            seq.set_feature("tier_index", idx)
            if idx == 0:
                seq.set_initial()
            else:
                seq.set_prev(self.sequence_list[idx-1])
            if idx == len(self.sequence_list)-1:
                seq.set_final()
            else:
                seq.set_fol(self.sequence_list[idx+1])

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

    def __repr__(self):
        return f"Sequence tier of {self.entry_class.__name__}; .superset_class: {self.superset_class.__name__}; .subset_class: {self.subset_class.__name__}"

    @property
    def starts(self):
        return np.array([x.start for x in self.entry_list])

    @property
    def ends(self):
        return np.array([x.end for x in self.entry_list])
    
    @property
    def labels(self):
        return [x.label for x in self.entry_list]

    @property
    def xmin(self):
        return self.sequence_list[0].start
    
    @property
    def xmax(self):
        return self.sequence_list[-1].end

    def get_interval_at_time(
            self, 
            time: float
        ) -> int:
        """_Gets interval index at specified time_

        Args:
            time (float): time at which to get an interval

        Returns:
            (int): Index of the interval
        """
        out_idx = np.searchsorted(self.starts, time, side = "left") - 1
        return out_idx
    
    def return_tier(self) -> IntervalTier:
        """_Returns a `praatio` interval tier_

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
        """_Saves as a textgrid_

        Uses `praatio.data_classes.textgrid.Textgrid.save()` method.

        Args:
            save_path (str): Output path
        """
        interval_tier = self.return_tier()
        out_tg = Textgrid()
        out_tg.addTier(tier = interval_tier)
        out_tg.save(save_path, "long_textgrid")


class RelatedTiers:
    """_Relates tiers_

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
        tiers: list[SequenceTier] = [SequenceTier(), SequenceTier()]
    ):
        self.tier_list = self._arrange_tiers(tiers)
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

    def __contains__(self, item):
        return item in self.tier_list
    
    def __getitem__(self, idx):
        return self.tier_list[idx]
        
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
    
    def __repr__(self):
        n_tiers = len(self.tier_list)
        classes = [x.__name__ for x in self.entry_classes]
        return f"RelatedTiers with {n_tiers} tiers. {repr(classes)}"
    
    def _arrange_tiers(
            self, 
            tiers: list[SequenceTier]
        ) -> list[SequenceTier]:
        """_Arranges tiers by hierarchy_

        Args:
            tiers (list[SequenceTier]): _description_
        """
        top_to_bottom = []
        to_arrange = len(tiers)
        top_idx = [x.superset_class for x in tiers].index(Top)
        top_to_bottom.append(tiers[top_idx])
        to_arrange += -1
        while to_arrange > 0:
            curr = top_to_bottom[-1]
            next_idx = [x.entry_class for x in tiers].index(curr.subset_class)
            top_to_bottom.append(tiers[next_idx])
            to_arrange += -1
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


    def show_structure(self):
        """_Show the hierarchical structure_
        """
        tab = "  "
        for idx, tier in enumerate(self.tier_list):
            if idx == 0:
                print(f"{tier.superset_class.__name__}(\n")
            print(f"{tab*(idx+1)}{tier.entry_class.__name__}(\n")
            if idx == len(self.tier_list)-1:
                print(f"{tab*(idx+2)}{tier.subset_class.__name__}(\n")
    