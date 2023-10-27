import pytest
import numpy as np
from aligned_textgrid.points.points import *
from aligned_textgrid.points.tiers import *
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

    def test_nearest_index(self):
        assert self.seq_point_tier.get_nearest_point_index(1.1) == 0
    
    def test_nearest(self):
        nearest_idx = self.seq_point_tier.get_nearest_point_index(1.1)
        nearest_point = self.seq_point_tier[nearest_idx]
        assert self.seq_point_tier.get_nearest_point(1.1) is nearest_point
    
    def test_return(self):
        out_tier = self.seq_point_tier.return_tier()
        assert isinstance(out_tier, PointTier)

class TestPointGroup:
    point_a = Point(1, "a")
    point_b = Point(2, "b")
    point_c = Point(1.5, "c")
    point_d = Point(2.5, "d")        

    point_tier1 = PointTier(name = "test1", entries = [point_a, point_b])
    point_tier2 = PointTier(name = "test2", entries = [point_c, point_d])

    seq_point_tier1 = SequencePointTier(point_tier1)
    seq_point_tier2 = SequencePointTier(point_tier2)

    def test_creation(self):
        assert PointsGroup(
            [self.seq_point_tier1, self.seq_point_tier2]
        )
    
    def test_indexing(self):
        point_group = PointsGroup(
            [self.seq_point_tier1, self.seq_point_tier2]
        )

        assert point_group[0]
    
    def test_single_indexing(self):
        point_group = PointsGroup(
            [self.seq_point_tier1, self.seq_point_tier2]
        )        
        
        tier = point_group[0]
        assert isinstance(tier, SequencePointTier)

    def test_nested_indexing(self):
        point_group = PointsGroup(
            [self.seq_point_tier1, self.seq_point_tier2]
        )

        points = point_group[[0][0]]
        assert len(points) == 2
        assert isinstance(points[0], SequencePoint)
    
    def test_nearest(self):
        point_group = PointsGroup(
            [self.seq_point_tier1, self.seq_point_tier2]
        )

        nearest = point_group.get_nearest_points_index(1.25)
        assert len(nearest) == 2

class TestAccessors:
    class MyPointClassA(SequencePoint):
        def __init__(self, point):
            super().__init__(point)
    
    class MyPointClassB(SequencePoint):
        def __init__(self, point):
            super().__init__(point)
    
    point_a = Point(1, "a")
    point_b = Point(2, "b")
    point_c = Point(1.5, "c")
    point_d = Point(2.5, "d")        

    point_tier1 = PointTier(name = "test1", entries = [point_a, point_b])
    point_tier2 = PointTier(name = "test2", entries = [point_c, point_d])

    seq_point_tier1 = SequencePointTier(point_tier1, entry_class=MyPointClassA)
    seq_point_tier2 = SequencePointTier(point_tier2, entry_class=MyPointClassB)
    seq_point_tier3 = SequencePointTier(point_tier2, entry_class=MyPointClassA)

    seq_point_group1 = PointsGroup(tiers = [seq_point_tier1, seq_point_tier2])
    seq_point_group2 = PointsGroup(tiers = [seq_point_tier1, seq_point_tier3])

    def test_successful_access(self):
        assert self.seq_point_group1.MyPointClassA
        assert isinstance(self.seq_point_group1.MyPointClassA[0], self.MyPointClassA)
    
    def test_missing_access(self):
       with pytest.raises(AttributeError, match="has no attribute"):
           self.seq_point_group1.SequencePoint

    def test_too_many(self, match = "has multiple entry classes"):
        with pytest.raises(AttributeError):
            self.seq_point_group2.MyPointClassA