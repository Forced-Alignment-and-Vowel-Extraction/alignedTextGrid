import pytest
import numpy as np
from aligned_textgrid.points.points import *
from aligned_textgrid.points.ptiers import *
from aligned_textgrid.sequences.sequences import *
from aligned_textgrid.sequences.tiers import *
from praatio.utilities.constants import Point
from praatio.data_classes.point_tier import PointTier

class TestPointTierCreation:
    point_a = Point(1, "a")
    point_b = Point(2, "b")

    point_tier = PointTier(name = "test", entries = [point_a, point_b])

    seq_point_tier = SequencePointTier(point_tier)
    seq_point_a = seq_point_tier[0]

    def test_tier_name(self):
        assert self.seq_point_tier.name == "test"

    def test_tier_class(self):
        assert self.seq_point_tier.entry_class == SequencePoint
    
    def test_tier_length(self):
        assert len(self.seq_point_tier) == 2
    
    def test_indexing(self):
        assert self.seq_point_tier[0]
    
    def test_tier_contains(self):
        assert self.seq_point_a in self.seq_point_tier
    
    def test_intier(self):
        assert self.seq_point_a.intier is self.seq_point_tier

    def test_xmin(self):
        assert np.allclose(self.seq_point_tier.xmin, 1)

    def test_xmax(self):
        assert np.allclose(self.seq_point_tier.xmax, 2)
    
    def test_times(self):
        assert np.allclose(self.seq_point_tier.times, np.array([1,2]))
    
    def test_labels(self):
        assert self.seq_point_tier.labels == ["a", "b"]

    def test_nearest(self):
        assert self.seq_point_tier.get_nearest_point(1.1) == 0
    
    def test_return(self):
        out_tier = self.seq_point_tier.return_tier()
        assert isinstance(out_tier, PointTier)