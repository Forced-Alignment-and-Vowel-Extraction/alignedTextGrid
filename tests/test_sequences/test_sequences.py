import pytest
from alignedTextGrid.sequences.sequences import *
import numpy as np
from praatio.utilities.constants import Interval

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
        assert local_sample.get_seq_by_relative_tieridx(1) is None

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
