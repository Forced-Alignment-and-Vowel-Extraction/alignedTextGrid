import pytest
from aligned_textgrid.sequences.sequences import *
from aligned_textgrid.sequences.tiers import *
from aligned_textgrid.custom_classes import custom_classes
from aligned_textgrid import AlignedTextGrid, Word, Phone
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

class TestBasicRead:

    def test_read(self):
        atg1 = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid", 
            entry_classes=[Word, Phone]
            )
        assert len(atg1) == 2
        assert [len(tg) == 2 for tg in atg1]
        
    def test_read_single(self):
        atg1 = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid", 
            entry_classes=[SequenceInterval]
            )
        assert len(atg1) == 4
        assert [len(tg) == 1 for tg in atg1]
        
    def test_read_multi(self):
        atg1 = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid", 
            entry_classes=custom_classes(["W1", "P1"]) + custom_classes(["W2", "P2"])
            )
        assert len(atg1) == 2
        assert [len(tg) == 2 for tg in atg1]
        
    def test_read_partial(self):
        atg1 = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid", 
            entry_classes=[Word]
            )
        assert len(atg1) == 4
        assert [len(tg) == 1 for tg in atg1]

    def test_read_partial2(self):
        atg1 = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid", 
            entry_classes=[Phone]
            )      
        assert len(atg1) == 4
        assert [len(tg) == 1 for tg in atg1]

class TestMultiRead:
    def test_read(self):
        atg_multi = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid", 
            entry_classes=custom_classes(["Word1", "Phone1"]) + 
                custom_classes(["Word2", "Phone2"])
            )

        assert len(atg_multi) == 2
        assert all([len(group) == 2 for group in atg_multi])
        
    def test_read_multi(self):
        Turn = custom_classes(class_list= "Turn")
        atg_multi = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1_multi.TextGrid", 
            entry_classes=[[Word, Phone], [Turn], [Word, Phone], [Turn]]
            )
        assert len(atg_multi) == 4
        assert len(atg_multi[0]) == 2 and len(atg_multi[2]) == 2
        assert len(atg_multi[1]) == 1 and len(atg_multi[3]) == 1

class TestClassSetting:
    atg1 = AlignedTextGrid(
        textgrid_path="tests/test_data/KY25A_1.TextGrid", 
        entry_classes=[MyWord, MyPhone]
        )
    atg2 = AlignedTextGrid(
        textgrid_path="tests/test_data/KY25A_1.TextGrid", 
        entry_classes=[[MyWord, MyPhone], [MyWord, MyPhone]]
        )
    
    atg3 = AlignedTextGrid(
        textgrid_path="tests/test_data/KY25A_1.TextGrid", 
        entry_classes = [
            custom_classes("MyWord", "MyPhone"),
            custom_classes("MyWord", "MyPhone")
        ]
    )
    
    def test_equiv(self):
        assert len(self.atg1.tier_groups) == len(self.atg2.tier_groups)
        
        for g1, g2 in zip(self.atg1.tier_groups, self.atg2.tier_groups):
            assert g1.tier_names == g2.tier_names
        
        assert self.atg1.entry_classes == self.atg2.entry_classes

        assert np.isclose(self.atg1.xmin, self.atg2.xmin)
        assert np.isclose(self.atg1.xmax, self.atg2.xmax)

    def test_get_class_by_name(self):

        target_class1 = self.atg1.get_class_by_name("MyWord")
        target_class2 = self.atg2.get_class_by_name("MyWord")

        assert target_class1 is MyWord
        assert target_class2 is MyWord

        missing_class = self.atg1.get_class_by_name("Foo")
        assert missing_class is None

        target_classes = self.atg3.get_class_by_name("MyWord")
        assert len(target_classes) > 1
    
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

class TestTierGroupNames:

    def test_tiergroup_name(self):
        tg = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid",
            entry_classes=[Word, Phone]
        )

        assert tg[0].name
        assert tg[1].name

        assert isinstance(tg.IVR, TierGroup)

class TestInterleave:
    
   
    def test_top_interleave(self):
        Word,Phone = custom_classes(["Word", "Phone"])

        tg = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid",
            entry_classes= [Word, Phone]
        )

        tg.interleave_class(
            name = "Testing",
            above = Word
        )

        all_len = [len(tgr) for tgr in tg]
        assert len(all_len) > 0
        assert all([l == 3 for l in all_len])

        assert tg[0][0].subset_class is Word
        assert not issubclass(tg[0].Word.superset_class, Top)

    def test_mid_interleave(self):
        Word,Phone = custom_classes(["Word", "Phone"])        
        tg = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid",
            entry_classes=[Word, Phone]
        )

        tg.interleave_class(
            name = "Testing",
            below = Word
        )

        all_len = [len(tgr) for tgr in tg]
        assert len(all_len) > 0
        assert all([l == 3 for l in all_len])

        assert tg[0][0].entry_class is Word
        assert not issubclass(tg[0].Word.subset_class, Phone)

    def test_multi_interleave(self):
        Word,Phone = custom_classes(["Word", "Phone"])        
        tg = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid",
            entry_classes=[Word, Phone]
        )

        tg.interleave_class(
            name = "Syllable",
            below = Word
        )

        tg.interleave_class(
            name = "SylPart",
            above = Phone
        )


        tg_lens = [len(tgr) for tgr in tg]
        assert all([l == 4 for l in tg_lens])

        assert tg[0]\
            .Phone\
            .superset_class\
            .superset_class\
            .superset_class == Word
    
    def test_bottom_class(self):
        Word,Phone = custom_classes(["Word", "Phone"])        
        tg = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid",
            entry_classes=[Word, Phone]
        )

        tg.interleave_class(
            name = "SubPhone",
            below = Phone,
            timing_from="above"
        )

        assert tg[0][-1].superset_class is Phone
        assert issubclass(tg[0][-1].subset_class, Bottom)

    def test_label_copy(self):
        Word,Phone = custom_classes(["Word", "Phone"])        
        tg = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid",
            entry_classes=[Word, Phone]
        )

        tg.interleave_class(
            name = "Syllable",
            below = Word,
            timing_from="above"
        )

        tg.interleave_class(
            name = "SylPart",
            above = Phone,
            timing_from = "below",
            copy_labels = False
        )

        copy_labs = [len(x.label) for x in tg[0].Syllable]
        assert any([x>0 for x in copy_labs])

        no_copy_labs = [len(x.label) for x in tg[0].SylPart]
        assert all([x==0 for x in no_copy_labs])

    def test_tiergroup_specificity(self):
        Word1, Phone1 = custom_classes(["Word1", "Phone1"])
        Word2, Phone2 = custom_classes(["Word2", "Phone2"])

        tg = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid",
            entry_classes=[[Word1, Phone1],[Word2, Phone2]]
        )

        tg.interleave_class(
            name = "Syllable",
            above = Phone1
        )

        assert len(tg[0]) == 3
        assert len(tg[1]) == 2

    def test_interleave_with_string(self):
        tg = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid",
            entry_classes=custom_classes(["Word", "Phone"])
        )

        tg.interleave_class(
            name = "Syllable", 
            below = "Word"
        )

        assert len(tg[0]) == 3
        assert isinstance(tg[0].Syllable, SequenceTier)

    def test_exceptions(self):
        Word,Phone = custom_classes(["Word", "Phone"])        
        tg = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid",
            entry_classes=[Word, Phone]
        )

        with pytest.raises(ValueError):
            tg.interleave_class("Syllable")
        
        with pytest.raises(ValueError):
            tg.interleave_class(
                "Syllable",
                below = Word,
                above = Phone
            )
        
        with pytest.raises(Exception):
            tg.interleave_class(
                below = "Word"
            )

        with pytest.raises(ValueError):
            tg.interleave_class(
                name = "Syllable",
                below = Word,
                timing_from="Word"
            )