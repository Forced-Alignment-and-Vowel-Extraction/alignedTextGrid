import pytest
from alignedTextGrid.sequences.sequences import *
import numpy as np
from praatio.utilities.constants import Interval

class TestSequenceIntervalDefault:
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
    
    def test_fol_success(self):
        A1 = self.LocalClassA()
        A2 = self.LocalClassA()

        try:
            A1.set_fol(A2)
        except Exception as exc:
            assert False, f"{exc}"
        
        assert A1.fol is A2
        assert A2.prev is A1
