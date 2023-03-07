import pytest
from alignedTextGrid.sequences.sequences import *
from alignedTextGrid.sequences.tiers import *
import numpy as np
from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from praatio.textgrid import openTextgrid

class TestSequenceTierDefault:

    default_tier = SequenceTier()

    def test_default_entryclass(self):
        assert self.default_tier.entry_class is SequenceInterval

    def test_default_name(self):
        assert self.default_tier.name == "SequenceInterval"

    def test_default_super(self):
        assert self.default_tier.superset_class is Top
    
    def test_default_sub(self):
        assert self.default_tier.subset_class is Bottom
    
    def test_default_sequence_list(self):
        assert len(self.default_tier.sequence_list) == 0

    def test_default_starts(self):
        starts = self.default_tier.starts
        assert type(starts) is np.ndarray
        assert len(starts) == 0

    def test_default_ends(self):
        ends = self.default_tier.ends
        assert type(ends) is np.ndarray
        assert len(ends) == 0
    
    def test_default_labels(self):
        labs = self.default_tier.labels
        assert type(labs) is list
        assert len(labs) == 0
    
    def test_default_xmin(self):
        assert self.default_tier.xmin is None
    
    def test_default_xmax(self):
        assert self.default_tier.xmax is None

    def test_default_getitme(self):
        with pytest.raises(IndexError):
            _ = self.default_tier[0]

class TestReadTier:
    read_tg = openTextgrid(
        fnFullPath="tests/test_data/josef-fruehwald_speaker.TextGrid",
        includeEmptyIntervals=True)

    class MyWord(SequenceInterval):
        def __init__(self, Interval = Interval(None, None, None)):
            super().__init__(Interval)

    class MyPhone(SequenceInterval):
        def __init__(self, Interval = Interval(None, None, None)):
            super().__init__(Interval)

    MyWord.set_subset_class(MyPhone)

    def test_process_tier(self):
        try:
            word_tier = SequenceTier(self.read_tg.tiers[0])
        except:
            assert False
        
        assert len(word_tier.sequence_list) == len(self.read_tg.tiers[0].entries)

    def test_process_entries(self):
        try:
            word_tier = SequenceTier(self.read_tg.tiers[0].entries)
        except:
            assert False

        assert len(word_tier.sequence_list) == len(self.read_tg.tiers[0].entries)

    def test_with_class(self):

        word_tier = SequenceTier(
            self.read_tg.tiers[0], 
            entry_class=self.MyWord
        )

        word_tier2 = SequenceTier(
            self.read_tg.tiers[0].entries, 
            entry_class=self.MyWord
        )

        assert word_tier.entry_class is self.MyWord
        assert word_tier.superset_class is Top
        assert word_tier.subset_class is self.MyPhone

        # are all entries MyWord?
        assert all([type(x) is self.MyWord for x in word_tier.sequence_list])

        assert word_tier2.entry_class is self.MyWord
        assert word_tier2.superset_class is Top
        assert word_tier2.subset_class is self.MyPhone

        # are all entries MyWord?
        assert all([type(x) is self.MyWord for x in word_tier2.sequence_list])

    def test_properties(self):
        word_tier = SequenceTier(
            self.read_tg.tiers[0], 
            entry_class=self.MyWord
        )

        ## it's sorted?
        assert np.all(np.diff(word_tier.starts) > 0)
        assert np.all(np.diff(word_tier.ends) > 0)

        assert word_tier.xmin == np.min(word_tier.starts)
        assert word_tier.xmax == np.max(word_tier.ends)

        assert word_tier.name == self.read_tg.tiers[0].name

        orig_labels = [x.label for x in self.read_tg.tiers[0].entries]
        assert all([x in orig_labels for x in word_tier.labels])

    def test_in_get_len(self):
        word_tier = SequenceTier(
            self.read_tg.tiers[0], 
            entry_class=self.MyWord
        )

        try:
            _ = len(word_tier)
        except:
            assert False

        assert len(word_tier) == len(self.read_tg.tiers[0].entries)
        
        sample_interval = word_tier.sequence_list[5]
        assert sample_interval in word_tier
        assert sample_interval is word_tier[5]
    
    def test_iter(self):
        word_tier = SequenceTier(
            self.read_tg.tiers[0], 
            entry_class=self.MyWord
        )

        assert all([type(x) is self.MyWord for x in word_tier])
    
    def test_get_interval_at_time(self):
        word_tier = SequenceTier(
            self.read_tg.tiers[0], 
            entry_class=self.MyWord
        )
        target_int = 40
        sample_interval = word_tier[target_int]
        mid_time = np.median(np.array([sample_interval.start, sample_interval.end]))

        assert word_tier.get_interval_at_time(mid_time) == target_int
        assert word_tier.get_interval_at_time(sample_interval.start) == target_int
        assert word_tier.get_interval_at_time(sample_interval.end) == target_int + 1

    def test_return_tier(self):
        word_tier = SequenceTier(
            self.read_tg.tiers[0], 
            entry_class=self.MyWord
        )

        out_tier = word_tier.return_tier()
        assert type(out_tier) is IntervalTier
        assert len(out_tier.entries) == len(word_tier)
                             



        






