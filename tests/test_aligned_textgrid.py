import pytest
from aligned_textgrid.sequences.sequences import *
from aligned_textgrid.sequences.tiers import *
from aligned_textgrid.aligned_textgrid import AlignedTextGrid
import numpy as np
from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from praatio.textgrid import openTextgrid

class MyWord(SequenceInterval):
    def __init__(self, Interval = Interval(None, None, None)):
        super().__init__(Interval)

class MyPhone(SequenceInterval):
    def __init__(self, Interval = Interval(None, None, None)):
        super().__init__(Interval)

MyWord.set_subset_class(MyPhone)


# default behavior is kind of a mess
# class TestAlignedDefault:  
#     my_aligned = AlignedTextGrid()

class TestReadFile:
    
    def test_readfile(self):
        atg = AlignedTextGrid(textgrid_path="tests/test_data/KY25A_1.TextGrid")
    
    def test_readobj(self):
        tg = openTextgrid(
            fnFullPath="tests/test_data/KY25A_1.TextGrid",
            includeEmptyIntervals=True
        )
        atg = AlignedTextGrid(textgrid = tg)

class TestClassSetting:
    atg1 = AlignedTextGrid(
        textgrid_path="tests/test_data/KY25A_1.TextGrid", 
        entry_classes=[MyWord, MyPhone]
        )
    atg2 = AlignedTextGrid(
        textgrid_path="tests/test_data/KY25A_1.TextGrid", 
        entry_classes=[[MyWord, MyPhone], [MyWord, MyPhone]]
        )
    
    def test_equiv(self):
        assert len(self.atg1.tier_groups) == len(self.atg2.tier_groups)
        
        for g1, g2 in zip(self.atg1.tier_groups, self.atg2.tier_groups):
            assert g1.tier_names == g2.tier_names
        
        assert self.atg1.entry_classes == self.atg2.entry_classes

        assert np.isclose(self.atg1.xmin, self.atg2.xmin)
        assert np.isclose(self.atg1.xmax, self.atg2.xmax)
    
class TestInGetLen:
    atg = AlignedTextGrid(
        textgrid_path="tests/test_data/KY25A_1.TextGrid", 
        entry_classes=[MyWord, MyPhone]
        )
    
    def test_in(self):
        assert self.atg.tier_groups[0] in self.atg
    
    def test_get(self):
        assert self.atg.tier_groups[0] is self.atg[0]
    
    def test_len(self):
        assert len(self.atg) == len(self.atg.tier_groups)

    def test_iter(self):
        assert len([x.xmin for x in self.atg]) == len(self.atg)

class TestGetInterval:
    atg = AlignedTextGrid(
        textgrid_path="tests/test_data/KY25A_1.TextGrid", 
        entry_classes=[MyWord, MyPhone]
        )

    def test_get_interval_at_time(self):
        target_time = 5
        idxes = [x.get_intervals_at_time(target_time) for x in self.atg]
        assert self.atg.get_intervals_at_time(target_time) == idxes

    def test_get_intervals(self):
        target_time = 11
        idxes = self.atg.get_intervals_at_time(target_time)
        test_list = []
        for tgidx, tg in zip(idxes, self.atg):
            test_list_inset = []
            for tier_idx,tier in zip(tgidx, tg):
                test_list_inset.append(tier[tier_idx])
            test_list.append(test_list_inset)

        eval_list = self.atg[idxes]
        for test0, eval0 in zip(test_list, eval_list):
            for test1, eval1 in zip(test0, eval0):
                assert test1 is eval1
    
    def test_get_interval_fail(self):
        with pytest.raises(Exception):
            self.atg[[0,0,0]]


class TestReturn:
    orig_tg = openTextgrid(
        "tests/test_data/KY25A_1.TextGrid", 
        includeEmptyIntervals=True)
    
    atg = AlignedTextGrid(
        textgrid = orig_tg, 
        entry_classes=[MyWord, MyPhone]
    )

    def test_return_textgrid(self):
        out_tg = self.atg.return_textgrid()

        assert type(out_tg) is Textgrid
        assert len(out_tg.tiers) == len(self.orig_tg.tiers)
        assert all([x in self.orig_tg.tierNames for x in out_tg.tierNames])

