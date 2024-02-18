import pytest
from aligned_textgrid.sequences.sequences import *
from aligned_textgrid.points.points import SequencePoint
from aligned_textgrid.sequences.tiers import *
import numpy as np
from praatio.utilities.constants import Interval
from praatio.utilities.constants import Point

class TestSequenceIntervalDefault:
    """_Test default behavior of SequenceInterval_
    """
    seq_int = SequenceInterval()
    class SampleClassI(SequenceInterval):
        def __init__(
                self, 
                Interval = Interval(None, None, None)
            ):
            super().__init__(Interval = Interval)

    def test_default_class(self):
        assert self.seq_int.__class__ is SequenceInterval
    
    def test_default_super_class(self):
        assert self.seq_int.superset_class is Top
    
    def test_default_subset_class(self):
        assert self.seq_int.subset_class is Bottom
    
    def test_default_super_instance(self):
        assert self.seq_int.super_instance is None

    def test_default_subset_list(self):
        assert type(self.seq_int.subset_list) is list
        assert len(self.seq_int.subset_list) == 0

    def test_default_sub_starts(self):
        assert type(self.seq_int.sub_starts) is np.ndarray
        assert len(self.seq_int.sub_starts) == 0

    def test_default_sub_ends(self):
        assert type(self.seq_int.sub_ends) is np.ndarray
        assert len(self.seq_int.sub_ends) == 0
    
    def test_default_sub_labels(self):
        assert type(self.seq_int.sub_labels) is list
        assert len(self.seq_int.sub_labels) == 0

    def test_default_intervalinfo(self):
        assert self.seq_int.start is None
        assert self.seq_int.end is None
        assert self.seq_int.label is None

    def test_default_fol(self):
        assert self.seq_int.fol.label == "#"

    def test_default_prev(self):
        assert self.seq_int.fol.label == "#"

    def test_default_super_strictness(self):
        local_sample = self.SampleClassI()
        with pytest.raises(Exception):
            self.seq_int.set_super_instance(local_sample)

    def test_default_sub_strictness(self):
        local_sample = self.SampleClassI()
        with pytest.raises(Exception):
            self.seq_int.append_subset_list(local_sample)
    
    def test_default_intier(self):
        local_sample = self.SampleClassI()
        assert local_sample.intier is None
    
    def test_default_tieridx(self):
        local_sample = self.SampleClassI()
        assert local_sample.tier_index is None

    def test_defaul_getby(self):
        local_sample = self.SampleClassI()
        assert local_sample.get_tierwise(1) is None

class TestSuperSubClassSetting:
    class LocalClassA(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)):
            super().__init__(Interval = Interval)

    class LocalClassB(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)):
            super().__init__(Interval = Interval)

    pre_instanceA = LocalClassA()
    pre_instanceB = LocalClassB()    

    def test_presetting(self):
        assert self.pre_instanceA.superset_class is Top
        assert self.pre_instanceA.subset_class is Bottom
        assert self.pre_instanceB.superset_class is Top
        assert self.pre_instanceB.subset_class is Bottom

    def test_presetting_instances(self):
        with pytest.raises(Exception):
            self.pre_instanceB.set_super_instance(self.pre_instanceA)
        
        with pytest.raises(Exception):
            self.pre_instanceA.append_subset_list(self.pre_instanceB)

    def test_bad_super_setting(self):
        with pytest.raises(Exception):
            self.LocalClassA.set_superset_class("B")
        
        with pytest.raises(Exception):
            self.LocalClassA.set_superset_class(self.LocalClassA)
        
        self.LocalClassA.set_superset_class()
    
    def test_bad_sub_setting(self):
        with pytest.raises(Exception):
            self.LocalClassA.set_subset_class("B")
        
        with pytest.raises(Exception):
            self.LocalClassA.set_subset_class(self.LocalClassA)

        self.LocalClassA.set_subset_class()

    def test_none_setting(self):
        new_instanceA = self.LocalClassA()

        try:
            new_instanceA.set_super_instance()
        except:
            assert False 

    def test_super_setting(self):
        self.LocalClassA.set_superset_class(self.LocalClassB)
        new_instanceA = self.LocalClassA()
        new_instanceB = self.LocalClassB()
        assert self.pre_instanceA.superset_class is self.LocalClassB
        assert new_instanceA.superset_class is self.LocalClassB

        assert self.pre_instanceB.subset_class is self.LocalClassA
        assert new_instanceB.subset_class is self.LocalClassA


    def test_postsetting_instances(self):
        try:
            self.pre_instanceA.set_super_instance(self.pre_instanceB)
        except Exception as exc:
            assert False, f"{exc}"

        assert self.pre_instanceA.super_instance is self.pre_instanceB
        assert self.pre_instanceA in self.pre_instanceB.subset_list

class TestPrecedence:
    class LocalClassA(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)):
            super().__init__(Interval = Interval)

    class LocalClassB(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)):
            super().__init__(Interval = Interval)
    
    def test_fol_prev_success(self):
        A1 = self.LocalClassA()
        A2 = self.LocalClassA()

        with pytest.raises(Exception):
            A1.set_fol(A1)

        with pytest.raises(Exception):
            A1.set_prev(A1)

        try:
            A1.set_fol(A2)
        except Exception as exc:
            assert False, f"{exc}"
        
        assert A1.fol  is A2
        assert A2.prev is A1

        try: 
            A1.set_prev(A2)
        except Exception as exc:
            assert False, f"{exc}"
            
        assert A1.prev is A2
        assert A2.fol  is A1
    
    def test_fol_prev_exception(self):
        A1 = self.LocalClassA()
        B2 = self.LocalClassB()

        with pytest.raises(Exception):
            A1.set_fol(B2)

        with pytest.raises(Exception):
            A1.set_prev(B2)

class TestHierarchy:

    class UpperClass(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)
            ):
            super().__init__(Interval)
    
    class LowerClass(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)
            ):
            super().__init__(Interval)

    UpperClass.set_subset_class(LowerClass)

    def test_super_instance(self):
        upper1 = self.UpperClass(Interval(0,10,"upper"))
        upper2 = self.UpperClass(Interval(0,10,"upper2"))
        lower1 = self.LowerClass(Interval(0,5,"lower1"))
        lower2 = self.LowerClass(Interval(5,10,"lower2"))

        try:
            lower1.set_super_instance(upper1)
        except Exception as exc:
            assert False, f"{exc}"
        
        assert lower1.super_instance is upper1
        assert lower1 in upper1

        try:
            lower2.set_super_instance(upper1)
        except Exception as exc:
            assert False, f"{exc}"

        assert lower2.super_instance is upper1
        assert lower2 in upper1

        assert lower1.fol is lower2
        assert lower2.prev is lower1


        upper2.append_subset_list(lower1)

        assert not lower1 in upper1
        assert lower1.super_instance is upper2

    def test_subset_instance(self):
        upper1 = self.UpperClass(Interval(0,10,"upper"))
        lower1 = self.LowerClass(Interval(0,5,"lower1"))
        lower2 = self.LowerClass(Interval(5,10,"lower2"))

        try:
            upper1.append_subset_list(lower1)
        except Exception as exc:
            assert False, f"{exc}"
        
        assert lower1.super_instance is upper1
        assert lower1 in upper1

        try:
            upper1.set_subset_list([lower2, lower1])
        except Exception as exc:
            assert False, f"{exc}"
        
        assert lower1.super_instance is upper1
        assert lower1 in upper1
        assert lower2.super_instance is upper1
        assert lower2 in upper1
        assert lower1.fol is lower2
        assert lower2.prev is lower1
    
    def test_remove_from_subset(self):
        upper1 = self.UpperClass(Interval(0,10,"upper"))
        lower1 = self.LowerClass(Interval(0,5,"lower1"))
        lower2 = self.LowerClass(Interval(5,10,"lower2"))

        upper1.set_subset_list([lower1, lower2])

        assert lower1 in upper1
        assert upper1.first is lower1

        upper1.remove_from_subset_list(lower1)

        assert not lower1 in upper1
        assert upper1.first is lower2

        assert lower1.within is None
        assert not lower1 in upper1.contains

    def test_remove_superset(self):
        upper1 = self.UpperClass(Interval(0,10,"upper"))
        lower1 = self.LowerClass(Interval(0,5,"lower1"))
        lower2 = self.LowerClass(Interval(5,10,"lower2"))

        upper1.set_subset_list([lower1, lower2])

        assert lower2 in upper1
        assert lower2.within is upper1

        lower2.remove_superset()

        assert lower2.within is None
        assert not lower2 in upper1.contains

        assert len(upper1) == 1

        try:
            upper1.remove_superset()
            assert True
        except:
            assert False


    def test_subset_index(self):
        upper1 = self.UpperClass(Interval(0,10,"upper"))
        lower1 = self.LowerClass(Interval(0,5,"lower1"))
        lower2 = self.LowerClass(Interval(5,10,"lower2"))
        lower3 = self.LowerClass(Interval(5,10,"lower2"))

        upper1.set_subset_list([lower1, lower2])

        assert upper1.index(lower1) == 0
        assert upper1.index(lower2) == 1

        with pytest.raises(ValueError):
            _ = upper1.index(lower3)
        
    def test_first_last(self):
        upper1 = self.UpperClass(Interval(0,10,"upper"))
        lower1 = self.LowerClass(Interval(0,5,"lower1"))
        lower2 = self.LowerClass(Interval(5,10,"lower2"))
        lower3 = self.LowerClass(Interval(11,15,"lower3"))

        upper1.set_subset_list([lower1, lower2, lower3])

        first_interval = upper1[0]
        assert upper1.first is first_interval

        last_interval = upper1[-1]
        assert upper1.last is last_interval

    def test_first_last_errors(self):
        upper1 = self.UpperClass(Interval(0,10,"upper"))
        point1 = SequencePoint(Point(0, "point"))

        with pytest.raises(IndexError):
            upper1.first

        with pytest.raises(IndexError):
            upper1.last

        with pytest.raises(AttributeError):
            point1.first

        with pytest.raises(AttributeError):
            point1.last            


    def test_subset_pop(self):
        upper1 = self.UpperClass(Interval(0,10,"upper"))
        lower1 = self.LowerClass(Interval(0,5,"lower1"))
        lower2 = self.LowerClass(Interval(5,10,"lower2"))
        lower3 = self.LowerClass(Interval(5,10,"lower2"))

        upper1.set_subset_list([lower1, lower2, lower3])

        assert len(upper1) == 3
        assert lower3 in upper1
        assert lower3.fol.label == "#"
        assert lower2.fol is lower3

        upper1.pop(lower3)
        assert len(upper1) == 2
        assert not lower3 in upper1
        assert lower2.fol.label == "#"
        assert not lower2.fol is lower3

        upper1.set_subset_list([lower1, lower2, lower3])

        upper1.pop(lower2)
        assert lower1.fol is lower3
        assert lower3.prev is lower1



    def test_hierarchy_strictness(self):
        upper1 = self.UpperClass(Interval(0,10,"upper"))
        lower1 = self.LowerClass(Interval(0,5,"lower1"))

        with pytest.raises(Exception):
            upper1.set_super_instance(lower1)
        
        with pytest.raises(Exception):
            lower1.append_subset_list(upper1)
        
        with pytest.raises(Exception):
            lower1.set_super_instance(lower1)
        
        with pytest.raises(Exception):
            lower1.append_subset_list(lower1)

    def test_validation(self):
        upper1 = self.UpperClass(Interval(0,10,"upper"))
        lower1 = self.LowerClass(Interval(0,5,"lower1"))
        gap = self.LowerClass(Interval(6,10,"gap"))
        overlap = self.LowerClass(Interval(4,10,"overlap"))
        snug = self.LowerClass(Interval(5,10,"snug"))

        upper1.set_subset_list([lower1, snug])
        assert upper1.validate()

        upper1.set_subset_list([lower1, gap])
        assert not upper1.validate()

        upper1.set_subset_list([lower1, overlap])
        assert not upper1.validate()

class TestIteration:
    class UpperClass(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)
            ):
            super().__init__(Interval)
    
    class LowerClass(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)
            ):
            super().__init__(Interval)

    UpperClass.set_subset_class(LowerClass)

    def test_iter(self):
        upper1 = self.UpperClass(Interval(0, 10, "one"))
        for x in range(10):
            upper1.append_subset_list(
                self.LowerClass(Interval(x, x+1, str(x)))
            )

        try:
            for item in upper1:
                pass
        except Exception as exc:
            assert False, f"{exc}"
        
        labels = [x.label for x in upper1]
        assert len(labels) == 10

class TestGetLenIn:
    class UpperClass(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)
            ):
            super().__init__(Interval)
    
    class LowerClass(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)
            ):
            super().__init__(Interval)

    UpperClass.set_subset_class(LowerClass)
    upper1 = UpperClass(Interval(0, 10, "upper"))

    lower1 = LowerClass(Interval=Interval(0,3,"lower1"))
    lower2 = LowerClass(Interval=Interval(3,8,"lower2"))        
    lower3 = LowerClass(Interval=Interval(8,10,"lower3"))
    lower4 = LowerClass(Interval=Interval(10,11,"lower4"))
    upper1.set_subset_list([lower1, lower2, lower3])

    def test_in(self):
        assert self.lower1 in self.upper1
        assert not self.lower4 in self.upper1

    def test_get(self):
        assert self.lower1 is self.upper1[0]
        for a,b in zip([self.lower2, self.lower3], self.upper1[1:3]):
            assert a is b
        with pytest.raises(IndexError):
            _ = self.upper1[4]
    
    def test_len(self):
        assert len(self.upper1) == 3

class TestSetFeature:
    class SampleClass(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)
            ):
            super().__init__(Interval)
    
    sample_obj = SampleClass(Interval=Interval(0, 10, "sample"))

    def test_set_feature(self):
        self.sample_obj.set_feature("new_feat", 5)
        assert self.sample_obj.new_feat == 5

        self.sample_obj.new_feat = "A"
        assert self.sample_obj.new_feat == "A"

class TestReturnInterval:
    class SampleClass(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)
            ):
            super().__init__(Interval)

    sample_obj = SampleClass(Interval=Interval(0, 10, "sample"))

    def test_return_interval_class(self):
        out_interval = self.sample_obj.return_interval()
        assert out_interval.__class__ is Interval
    def test_return_interval_values(self):
        out_interval = self.sample_obj.return_interval()
        assert out_interval.start == 0
        assert out_interval.end == 10
        assert out_interval.label == "sample"

class TestFusion:
    class SampleClass(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)
            ):
            super().__init__(Interval)

    class Upper(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)
            ):
            super().__init__(Interval)
    
    class Lower(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)
            ):
            super().__init__(Interval)

    Lower.set_superset_class(Upper)                        

    def test_rightwards_simple(self):
        fuser = self.SampleClass(Interval(0,1,"one"))
        fusee = self.SampleClass(Interval(1, 2, "two"))
        fuser.set_fol(fusee)

        try:
            fuser.fuse_rightwards()
        except:
            assert False
        
        assert fuser.label == "one two"
        assert fuser.end == 2

        with pytest.raises(Exception):
            fuser.fuse_rightwards()

    def test_leftwards_simple(self):
        fusee = self.SampleClass(Interval(0,1,"one"))
        fuser = self.SampleClass(Interval(1, 2, "two"))
        fuser.set_prev(fusee)

        try:
            fuser.fuse_leftwards()
        except:
            assert False
        
        assert fuser.label == "one two"
        assert fuser.start == 0

        with pytest.raises(Exception):
            fuser.fuse_leftwards()

    def test_rightwards_hierarchy(self):
        upper1 = self.Upper(Interval(0,5, "upper1"))
        upper2 = self.Upper(Interval(5,10, "upper2"))
        lower1 = self.Lower(Interval(0,1, "lower1"))
        lower2 = self.Lower(Interval(1,5, "lower2"))
        lower3 = self.Lower(Interval(5,6, "lower3"))
        lower4 = self.Lower(Interval(6,10, "lower3"))

        upper1.set_subset_list([lower1, lower2])
        upper2.set_subset_list([lower3, lower4])
        upper1.set_fol(upper2)

        assert len(upper1) == 2
        assert lower2 in upper1
        assert lower1.fol is lower2
        try:
            lower1.fuse_rightwards()
        except:
            assert False

        assert len(upper1) == 1
        assert not lower2 in upper1
        assert lower1.fol.label == "#"

        assert not lower3 in upper1

        upper1.fuse_rightwards()

        assert len(upper1) == 3
        assert lower3 in upper1
        assert lower1.fol is lower3

    def test_leftwards_hierarchy(self):
        upper1 = self.Upper(Interval(0,5, "upper1"))
        upper2 = self.Upper(Interval(5,10, "upper2"))
        lower1 = self.Lower(Interval(0,1, "lower1"))
        lower2 = self.Lower(Interval(1,5, "lower2"))
        lower3 = self.Lower(Interval(5,6, "lower3"))
        lower4 = self.Lower(Interval(6,10, "lower3"))

        upper1.set_subset_list([lower1, lower2])
        upper2.set_subset_list([lower3, lower4])
        upper1.set_fol(upper2)

        assert len(upper1) == 2
        assert lower2 in upper1
        assert lower1.fol is lower2
        try:
            lower2.fuse_leftwards()
        except:
            assert False

        assert len(upper1) == 1
        assert not lower1 in upper1
        assert lower2.prev.label == "#"

        assert not lower2 in upper2

        upper2.fuse_leftwards()

        assert len(upper2) == 3
        assert lower2 in upper2
        assert lower3.prev is lower2

    def test_rightward_tier(self):
        tier1 = SequenceTier(tier = [
            Interval(0, 5, "upper1"),
            Interval(5, 10, "upper2")
        ],
        entry_class=self.Upper)
        tier2 =  SequenceTier(tier = [
            Interval(0, 2, "lower1"),
            Interval(2, 5, "lower2"),
            Interval(5, 7, "lower3"),
            Interval(7, 10, "lower4")
        ],
        entry_class=self.Lower)

        rt = TierGroup(tiers=[tier1, tier2])
        assert len(rt[0]) == 2
        assert len(rt[1]) == 4

        assert len(rt[0][0]) == 2
        assert rt[1][1].fol.label == "#"

        third_lower = rt[1][2]

        assert third_lower.tier_index == 2
    
        rt[1][0].fuse_rightwards()

        assert len(rt[0]) == 2
        assert len(rt[1]) == 3

        assert len(rt[0][0]) == 1
        assert rt[1][0].fol.label == "#"

        assert third_lower.tier_index == 1

        with pytest.raises(Exception):
            rt[1][0].fuse_rightwards()
        
        rt[0][0].fuse_rightwards()
        assert len(rt[0]) == 1
        assert len(rt[1]) == 3

        assert rt[0][0].fol.label == "#"

        try:
            rt[1][0].fuse_rightwards()
        except:
            assert False

    def test_leftward_tier(self):
        tier1 = SequenceTier(tier = [
            Interval(0, 5, "upper1"),
            Interval(5, 10, "upper2")
        ],
        entry_class=self.Upper)
        tier2 =  SequenceTier(tier = [
            Interval(0, 2, "lower1"),
            Interval(2, 5, "lower2"),
            Interval(5, 7, "lower3"),
            Interval(7, 10, "lower4")
        ],
        entry_class=self.Lower)

        rt = TierGroup(tiers=[tier1, tier2])
        assert len(rt[0]) == 2
        assert len(rt[1]) == 4

        assert len(rt[0][0]) == 2
        assert rt[1][0].prev.label == "#"

        third_lower = rt[1][2]

        assert third_lower.tier_index == 2
    
        rt[1][1].fuse_leftwards()

        assert len(rt[0]) == 2
        assert len(rt[1]) == 3

        assert len(rt[0][0]) == 1
        assert rt[1][0].prev.label == "#"

        assert third_lower.tier_index == 1

        with pytest.raises(Exception):
            rt[1][0].fuse_leftwards()
        
        rt[0][1].fuse_leftwards()
        assert len(rt[0]) == 1
        assert len(rt[1]) == 3

        assert rt[0][0].fol.label == "#"

        try:
            rt[1][1].fuse_leftwards()
        except:
            assert False
class TestTop:
    class SampleClass(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)
            ):
            super().__init__(Interval)

    sample_obj = SampleClass(Interval=Interval(1,2, "sample"))

    def test_top_default(self):
        assert Top.superset_class is None

    def test_top_insensitivity(self):
        Top.set_superset_class(self.SampleClass)
        assert Top.superset_class is None

    def test_no_top_superinstance(self):
        with pytest.raises(Exception):
            t = Top()
            t.set_super_instance(self.sample_obj)

class TextBottom:
    class SampleClass(SequenceInterval):
        def __init__(
                self, 
                Interval: Interval = Interval(None, None, None)
            ):
            super().__init__(Interval)

    sample_obj = SampleClass(Interval=Interval(1,2, "sample"))

    def test_bottom_default(self):
        assert Bottom.subset_class is None
    
    def test_bottom_insensitivity(self):
        Bottom.set_subset_class(self.SampleClass)
        assert Bottom.subset_class is None

    def test_bottom_no_append_subset(self):
        b = Bottom()
        with pytest.raises(Exception):
            b.append_subset_list(self.sample_obj)

    def test_bottom_no_set_subset(self):
        b = Bottom()
        with pytest.raises(Exception):
            b.set_subset_list([self.sample_obj])
