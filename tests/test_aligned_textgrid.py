import pytest
from aligned_textgrid.sequences.sequences import *
from aligned_textgrid.sequences.tiers import *
from aligned_textgrid.custom_classes import custom_classes
from aligned_textgrid import AlignedTextGrid, Word, Phone
import numpy as np
from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from praatio.textgrid import openTextgrid
from pathlib import Path

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

    def test_read_arg(self):
        """
        Test that the first unnamed arg can process
        str, Path, and praatio.Textgrid classes correctly.
        """
        tg = openTextgrid(
            fnFullPath="tests/test_data/KY25A_1.TextGrid",
            includeEmptyIntervals=True
        )        

        atg1 = AlignedTextGrid(
            "tests/test_data/KY25A_1.TextGrid",
            entry_classes=[Word, Phone]
        )
        atg2 = AlignedTextGrid(
            Path("tests/test_data/KY25A_1.TextGrid"),
            entry_classes=[Word, Phone]
        )
        atg3 = AlignedTextGrid(
           tg,
            entry_classes=[Word, Phone]
        )

        assert len(atg1) == len(atg2) == len(atg3)

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
            entry_classes=[custom_classes(["W1", "P1"]), custom_classes(["W2", "P2"])]
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


class TestMultiRead:
    def test_read(self):
        atg_multi = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid", 
            entry_classes=[
                custom_classes(["Word1", "Phone1"]),
                custom_classes(["Word2", "Phone2"])
                ]
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
            custom_classes(["MyWord", "MyPhone"]),
            custom_classes(["MyWord", "MyPhone"])
        ]
    )
    atg4 = AlignedTextGrid()
    
    def test_equiv(self):
        assert len(self.atg1.tier_groups) == len(self.atg2.tier_groups)
        
        for g1, g2 in zip(self.atg1.tier_groups, self.atg2.tier_groups):
            assert g1.tier_names == g2.tier_names
        
        # Intentionally broken (issue #180)
        # assert self.atg1.entry_classes == self.atg2.entry_classes

        assert np.isclose(self.atg1.xmin, self.atg2.xmin)
        assert np.isclose(self.atg1.xmax, self.atg2.xmax)

    def test_get_class_by_name(self):

        target_class1 = self.atg1.get_class_by_name("MyWord")
        target_class2 = self.atg2.get_class_by_name("MyWord")

        assert target_class1.__qualname__ == "MyWord"
        assert target_class2.__qualname__ == "MyWord"

        missing_class1 = self.atg1.get_class_by_name("Foo")
        missing_class2 = self.atg2.get_class_by_name("Foo")
        missing_class4 = self.atg4.get_class_by_name("Foo")
        assert missing_class1 is None
        assert missing_class2 is None
        assert missing_class4 is None


    def test_empty_class_indexing(self):
        assert len(self.atg4) == 0

        with pytest.raises(IndexError):
            self.atg4[0]

        with pytest.raises(IndexError):
            idx_list = [0,1,2]
            self.atg4[idx_list]

        with pytest.raises(IndexError):
            empty_idx_list = []
            self.atg4[empty_idx_list]

    def test_empty_class_attributes(self):
        with pytest.raises(ValueError):
            self.atg4.xmin

        with pytest.raises(ValueError):
            self.atg4.xmax

        with pytest.raises(ValueError):
            self.atg4.tier_names
    
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

class TestProperties:
    atg = AlignedTextGrid(
        textgrid_path="tests/test_data/KY25A_1.TextGrid", 
        entry_classes=[MyWord, MyPhone]
        )
    
    def test_xmin(self):
        assert self.atg.xmin is not None
    
    def test_xmax(self):
        assert self.atg.xmax is not None

    def test_tier_names(self):
        names = self.atg.tier_names
        assert len(names) == len(self.atg)
        for name, group in zip(names, self.atg):
            assert len(name) == len(group)

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

    def test_tiergroup_name_duplicates(self):
        with pytest.warns():
            tg = AlignedTextGrid(
                textgrid_path="tests/test_data/josef-fruehwald_speaker_dup.TextGrid",
                entry_classes=[Word, Phone]
            )
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

        assert issubclass(tg[0][0].subset_class, Word)
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

        assert issubclass(tg[0][0].entry_class, Word)
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

        assert issubclass(tg[0]\
            .Phone\
            .superset_class\
            .superset_class\
            .superset_class, Word)
    
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

        assert issubclass(tg[0][-1].superset_class,Phone)
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

class TestPop:

    Turns, Word,Phone = custom_classes(["Turns", "Word", "Phone"])        
    atg = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1_multi.TextGrid",
            entry_classes=[Word, Phone, Turns]
        )
    turn_lens = [
            len(x.contains) 
            for tg in atg
            for x in tg.Turns
            if len(x.label) > 0
        ]

    def test_pre_pop(self):
       for tg in self.atg:
           entry_class_names = [x.__name__ for x in tg.entry_classes]
           assert "Word" in entry_class_names
    
    def test_run_pop(self):
        self.atg.pop_class(Word)

        for tg in self.atg:
           entry_class_names = [x.__name__ for x in tg.entry_classes]
           assert "Word" not in entry_class_names

    def test_pop_result(self):
        self.new_turn_lens = [
            len(x.contains) 
            for tg in self.atg
            for x in tg.Turns
            if len(x.label) > 0
        ]

        for old, new in zip(self.turn_lens, self.new_turn_lens):
            assert new > old

    def test_no_pop(self):
        assert len(self.atg[0]) == 2
        self.atg.pop_class("NotInAtg")
        assert len(self.atg[0]) == 2

    def test_all_pop(self):
        self.atg.pop_class("Turns")
        with pytest.warns():
            self.atg.pop_class("Phone")

class TestClassCloning:

    def test_class_clone(self):
        tg = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid",
            entry_classes= [Word, Phone]
        )

        flat_classes = [c for l in  tg.entry_classes for c in l]
        
        assert not Word in flat_classes

        assert any(
            [issubclass(c, Word) for c in flat_classes]
        )

    def test_post_interleave(self):
        tg = AlignedTextGrid(
            textgrid_path="tests/test_data/KY25A_1.TextGrid",
            entry_classes= [Word, Phone]
        )

        tg.interleave_class(name = "Syl", above=Phone)

        p_entry = tg[0].Phone.entry_class
        assert not p_entry is Phone
        assert issubclass(p_entry, Phone)

        assert not p_entry.superset_class is Phone.superset_class
        assert Phone.superset_class is Word
        assert not p_entry.superset_class is Word