from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from alignedTextGrid.sequences.sequences import SequenceInterval, Top, Bottom
import numpy as np


class SequenceTier:
    def __init__(
        self,
        entry_list = [Interval(None, None, None)],
        entry_class = SequenceInterval(),
        superset_class = Top(),
        subset_class = Bottom()
    ):
        self.entry_list = entry_list
        self.entry_class = entry_class
        self.superset_class = superset_class
        self.subset_class = subset_class
        entry_order = np.argsort(self.starts)
        self.entry_list = [self.entry_list[idx] for idx in entry_order]
        self.sequence_list = []
        for entry in self.entry_list:
            this_seq = self.entry_class.__class__(entry)
            this_seq.set_superset_class(self.superset_class)
            this_seq.set_subset_class(self.subset_class)
            self.sequence_list += [this_seq]
        for idx,seq in enumerate(self.sequence_list):
            if idx == 0:
                seq.set_initial()
            else:
                seq.set_prev(self.sequence_list[idx-1])
            if idx == len(self.sequence_list)-1:
                seq.set_final()
            else:
                seq.set_fol(self.sequence_list[idx+1])

    def __iter__(self):
        self._idx = 0
        return self

    def __next__(self):
        if self._idx < len(self.sequence_list):
            out = self.sequence_list[self._idx]
            self._idx += 1
            return(out)
        raise StopIteration

    def __repr__(self):
        return f"Sequence tier of {self.entry_class.__class__.__name__}; .superset_class: {self.superset_class.__class__.__name__}; .subset_class: {self.subset_class.__class__.__name__}"

    def __getitem__(self, idx):
        return self.sequence_list[idx]

    @property
    def starts(self):
        return [x.start for x in self.entry_list]

    @property
    def ends(self):
        return [x.end for x in self.entry_list]

    @property
    def xmin(self):
        return self.sequence_list[0].start
    
    @property
    def xmax(self):
        return self.sequence_list[-1].end

    def get_interval_at_time(self, time):
        out_idx = np.searchsorted(self.starts, time, side = "left") - 1
        return out_idx

class RelatedTiers:
    def __init__(
        self,
        top_to_bottom = [SequenceTier(), SequenceTier()]
    ):
        self.tier_list = top_to_bottom
        for idx, tier in enumerate(top_to_bottom):
            if idx == len(top_to_bottom)-1:
                break
            else:
                upper_tier = top_to_bottom[idx]
                lower_tier = top_to_bottom[idx+1]

                upper_starts = upper_tier.starts
                upper_ends = upper_tier.ends
                lower_starts = lower_tier.starts
                lower_ends = lower_tier.ends
                
                starts = np.searchsorted(lower_starts, upper_starts, side = "left")
                ends = np.searchsorted(lower_ends, upper_ends, side = "right")

                lower_sequences = [lower_tier[starts[idx]:ends[idx]] for idx,_ in enumerate(upper_tier)]

                for u,l in zip(upper_tier, lower_sequences):
                    u.set_subset_list(l)

    def __getitem__(self, idx):
        return self.tier_list[idx]