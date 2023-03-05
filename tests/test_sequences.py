import pytest
from alignedTextGrid.sequences.sequences import *
import numpy as np

class TestSequenceIntervalDefault:
    seq_int = SequenceInterval()

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
        assert self.seq_int.fol.label is "#"

    def test_default_prev(self):
        assert self.seq_int.fol.label is "#"

