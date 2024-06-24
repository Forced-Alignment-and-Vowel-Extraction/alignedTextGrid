import pytest
from aligned_textgrid.sequences.sequences import *
from aligned_textgrid.sequences.tiers import *
from aligned_textgrid import Word, Phone
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

class TestTierMaking:

    def test_class_setting(self):
        the = Word((0,1,"the"))
        dog = Word((1,2,"dog"))
        tier = SequenceTier([the, dog])
        assert issubclass(tier.entry_class, Word)
        assert all([isinstance(x, Word) for x in tier])

        tier2 = SequenceTier([the, dog], entry_class=Phone)
        assert issubclass(tier2.entry_class, Phone)
        assert all([isinstance(x, Phone) for x in tier2])

        tier3 = SequenceTier(tier2, entry_class=Word)
        assert issubclass(tier3.entry_class, Word)
        assert all([isinstance(x, Word) for x in tier3])

    


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

    def test_time_setting(self):
        word_tier1 = SequenceTier(
            self.read_tg.tiers[0], 
            entry_class=self.MyWord
        )

        word_tier2 = SequenceTier(
            self.read_tg.tiers[0], 
            entry_class=self.MyWord
        )        

        n = len(word_tier1.sequence_list)
        fake_times = np.linspace(0, 1, n)

        word_tier1.starts = fake_times
        assert np.all(fake_times == word_tier1.starts)
        assert not np.all(word_tier2.starts == word_tier1.starts)

        word_tier1.ends = fake_times
        assert np.all(fake_times == word_tier1.ends)
        assert not np.all(word_tier2.ends == word_tier1.ends)

        too_short = np.linspace(0, 1, n - 20)
        with pytest.raises(Exception):
            word_tier1.starts = too_short

        with pytest.raises(Exception):
            word_tier1.ends = too_short


    def test_shift(self):
        word_tier1 = SequenceTier(
            self.read_tg.tiers[0], 
            entry_class=self.MyWord
        )

        word_tier2 = SequenceTier(
            self.read_tg.tiers[0], 
            entry_class=self.MyWord
        )        

        word_tier1._shift(5)

        s_shifts = word_tier1.starts - word_tier2.starts
        e_shifts = word_tier1.ends - word_tier2.ends

        assert np.all(np.isclose(s_shifts, 5))
        assert np.all(np.isclose(e_shifts, 5))

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

    def test_index(self):
        word_tier = SequenceTier(
            self.read_tg.tiers[0], 
            entry_class=self.MyWord
        )
        target_idx = 10
        entry = word_tier[target_idx]
        assert word_tier.index(entry) == target_idx
    
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

class TestIntierSetting:
    interval1 = Interval(0,1,"one")
    interval2 = Interval(1,2, "two")
    interval3 = Interval(2,3, "three")

    def test_inteir(self):
        try:
            tier = SequenceTier(
                tier = [
                    self.interval1,
                    self.interval2,
                    self.interval3
                    ]
                )
        except:
            assert False

        assert tier[0].intier is tier

    def test_sequence_index(self):
        tier = SequenceTier(
            tier = [
                self.interval1,
                self.interval2,
                self.interval3
                ]
            )
        for idx, entry in enumerate(tier):
            assert entry.tier_index == idx
    
    def test_first_last(self):
        tier = SequenceTier(
            tier = [
                self.interval1,
                self.interval2,
                self.interval3
                ]
            )
        
        first_interval = tier[0]
        assert tier.first is first_interval

        last_interval = tier[-1]
        assert tier.last is last_interval
    
    def test_first_last_errors(self):
        tier = SequenceTier()

        with pytest.raises(IndexError):
            tier.first
    
    def test_get_tieridx(self):
        tier = SequenceTier(
            tier = [
                self.interval1,
                self.interval2,
                self.interval3
                ]
            )

        entry = tier[0]
        assert entry.get_tierwise(0) is entry
        assert entry.get_tierwise(1) is entry.fol
        
        entry2 = tier[2]
        assert entry2.get_tierwise(-1) is entry2.prev
        with pytest.raises(IndexError):
            _ =  entry2.get_tierwise(1)

class TestTierPop:
    interval1 = Interval(0,1,"one")
    interval2 = Interval(1,2, "two")
    interval3 = Interval(2,3, "three")
    tier = SequenceTier(
                tier = [
                    interval1,
                    interval2,
                    interval3
                    ]
                )
    
    def test_tier_pop(self):
        a = self.tier[0]
        b = self.tier[1]
        c = self.tier[2]
        try:
            self.tier.pop(b)
        except:
            assert False

        assert not b in self.tier

        assert len(self.tier) == 2
        assert a.fol is c

class TestTierGroupDefault:
    rt = TierGroup()
    
    def test_ranges(self):
        assert self.rt.xmin is None
        assert self.rt.xmax is None

    def test_tier_properties(self):
        assert len(self.rt.tier_list) == 1
        assert self.rt.tier_names[0] == "SequenceInterval"

class TestReadTiers:
    read_tg = openTextgrid(
        fnFullPath="tests/test_data/josef-fruehwald_speaker.TextGrid",
        includeEmptyIntervals=True
    )

    class MyWord(SequenceInterval):
        def __init__(self, Interval = Interval(None, None, None)):
            super().__init__(Interval)

    class MyPhone(SequenceInterval):
        def __init__(self, Interval = Interval(None, None, None)):
            super().__init__(Interval)

    MyWord.set_subset_class(MyPhone)
    tg_word = SequenceTier(read_tg.tiers[0], entry_class=MyWord)
    tg_phone = SequenceTier(read_tg.tiers[1], entry_class=MyPhone)

    def test_relation(self):
        rt = TierGroup([self.tg_word, self.tg_phone])
        rt2 = TierGroup([self.tg_phone, self.tg_word])

        assert rt.entry_classes == rt2.entry_classes
        assert all([type(x) is self.MyWord for x in rt.tier_list[0]])
        assert all([type(x) is self.MyPhone for x in rt.tier_list[1]])

        assert type(rt.tier_list[0][10][-1]) is self.MyPhone
        assert rt.tier_list[0][10][-1].fol.label == "#"

        assert all([len(x)>0 for x in rt[0]])
        assert all([not x.super_instance is None for x in rt[1]])
    
    def test_in_get_len(self):
        rt = TierGroup([self.tg_word, self.tg_phone])

        assert self.tg_phone in rt
        assert rt[0] is self.tg_word
        assert len(rt) == 2

    def test_iter(self):
        rt = TierGroup([self.tg_word, self.tg_phone])

        assert [x.name for x in rt] == [self.tg_word.name, self.tg_phone.name]
    
    def test_get_intervals_at_time(self):
        rt = TierGroup([self.tg_word, self.tg_phone])

        target_time = 5
        idx1 = rt[0].get_interval_at_time(5)
        idx2 = rt[1].get_interval_at_time(5)

        assert rt.get_intervals_at_time(5) == [idx1, idx2]



