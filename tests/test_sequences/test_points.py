import pytest
import numpy as np
from aligned_textgrid.points.points import *
from aligned_textgrid.points.ptiers import *
from aligned_textgrid.sequences.sequences import *
from aligned_textgrid.sequences.tiers import *
from praatio.utilities.constants import Point

class TestSequencePointDefault:
    seq_point = SequencePoint()

    def test_default_class(self):
        assert self.seq_point.__class__ is SequencePoint
    
    def test_default_time(self):
        assert self.seq_point.time is None

    def test_default_label(self):
        assert self.seq_point.label is None
    
    def test_default_fol(self):
        assert self.seq_point.fol.label == "#"
    
    def test_default_prev(self):
        assert self.seq_point.prev.label == "#"

class TestPrecedence:
    seq_point_a = SequencePoint(Point(1, "a"))
    seq_point_b = SequencePoint(Point(2, "b"))
    seq_point_c = SequencePoint(Point(3, "c"))    

    seq_point_a.set_initial()
    seq_point_a.set_fol(seq_point_b)
    seq_point_b.set_final()

    def test_fol(self):
        assert self.seq_point_a.fol is self.seq_point_b

    def test_prev(self):
        assert self.seq_point_b.prev is self.seq_point_a

    def test_not_self_fol(self):
        with pytest.raises(Exception):
            self.seq_point_c.set_fol(self.seq_point_c)
    
    def test_initial_prev(self):
        with pytest.warns(Warning):
            self.seq_point_a.prev_distance
    
    def test_final_fol(self):
        with pytest.warns(Warning):
            self.seq_point_b.fol_distance


class TestDistances:
    seq_point_a = SequencePoint(Point(1, "a"))
    seq_point_b = SequencePoint(Point(2, "b"))

    seq_point_c = SequencePoint(Point(3, "c"))

    seq_interval = SequenceInterval(Interval(0, 1.5, "cc"))

    seq_point_a.set_fol(seq_point_b)

    def test_fol_distance(self):
        assert np.allclose(self.seq_point_a.fol_distance, 1)
    
    def test_prev_distance(self):
        assert np.allclose(self.seq_point_b.prev_distance, -1)

    def test_point_distance_bc(self):
        assert np.allclose(
            self.seq_point_b.distance_from(self.seq_point_c),
            -1
        )
    
    def test_point_distance_ca(self):
        assert np.allclose(
            self.seq_point_c.distance_from(self.seq_point_a),
            2
        )
    
    def test_point_sequence_distance(self):
        distances = self.seq_point_a.distance_from(self.seq_interval)

        assert np.allclose(distances[0], 1)
        assert np.allclose(distances[1], -0.5)

class TestWarnings:

    seq_point_a = SequencePoint(Point(1, "a"))

    def test_in_warn(self):
        with pytest.warns(Warning):
            "a" in self.seq_point_a
    
    def test_index_warn(self):
        with pytest.warns(Warning):
            self.seq_point_a[1]