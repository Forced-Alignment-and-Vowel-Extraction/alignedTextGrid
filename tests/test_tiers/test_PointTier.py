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

    point_a2 = SequencePoint((1, "a"))
    point_b2 = SequencePoint((2, "b"))

    point_tier = PointTier(name = "test", entries = [point_a, point_b])

    seq_point_tier = SequencePointTier(point_tier)
    seq_point_tier2 = SequencePointTier([point_a2, point_b2])
    seq_point_a = seq_point_tier[0]
    seq_point_a2 = seq_point_tier2[0]

    def test_tier_name(self):
        assert self.seq_point_tier.name == "test"
        assert self.seq_point_tier2.name == "SequencePoint"

    def test_tier_class(self):
        assert self.seq_point_tier.entry_class == SequencePoint
        assert self.seq_point_tier2.entry_class == SequencePoint
    
    def test_tier_length(self):
        assert len(self.seq_point_tier) == 2
        assert len(self.seq_point_tier2) == 2
    
    def test_indexing(self):
        assert self.seq_point_tier[0]
        assert self.seq_point_tier2[0]
    
    def test_tier_contains(self):
        assert self.seq_point_a in self.seq_point_tier
        assert self.seq_point_a2 in self.seq_point_tier2
    
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

class TestClassSetting:

    class MyPointA(SequencePoint):
        def __init__(self, *args):
            super().__init__(*args)

    class MyPointB(SequencePoint):
        def __init__(self, *args):
            super().__init__(*args)

    def test_class_from_point(self):
        point_a = self.MyPointA((1, "a"))
        point_b = self.MyPointA((2, "b"))

        point_tier = SequencePointTier([point_a, point_b])
        assert issubclass(point_tier.entry_class, self.MyPointA)    

    def test_override_class(self):
        point_a = self.MyPointA((1, "a"))
        point_b = self.MyPointA((2, "b"))

        point_tier = SequencePointTier([point_a, point_b], entry_class=self.MyPointB)

        assert issubclass(point_tier.entry_class, self.MyPointB)
        assert not issubclass(point_tier.entry_class, self.MyPointA)


class TestPointPrecedence:

    def test_first_last(self):
        point_a = Point(1, "a")
        point_b = Point(2, "b")
        point_c = Point(3, "c")

        tier = SequencePointTier(tier = [point_a, point_b, point_c])

        first_point = tier[0]
        assert tier.first is first_point

        last_point = tier[-1]
        assert tier.last is last_point

    def test_first_last_error(self):
        tier = SequencePointTier()

        with pytest.raises(IndexError):
            tier.first
        
        with pytest.raises(IndexError):
            tier.last

class TestPointTime:
    def test_time_set(self):
        point_a = Point(1, "a")
        point_b = Point(2, "b")
        point_c = Point(3, "c")

        tier = SequencePointTier(tier = [point_a, point_b, point_c])

        tier.times += 1
        assert tier.times[0] == 2

        tier.times = np.array([4, 5, 6])
        assert tier.times[0] == 4

        with pytest.raises(Exception):
            tier.times = np.array([6, 7])

    def test_time_shift(self):
        point_a = Point(1, "a")
        point_b = Point(2, "b")
        point_c = Point(3, "c")

        tier = SequencePointTier(tier = [point_a, point_b, point_c])
        
        orig_times = tier.times

        tier._shift(3)

        assert all(np.isclose(tier.times - orig_times, 3))

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
    
class TestPointGroupShift:
    point_a = Point(1, "a")
    point_b = Point(2, "b")
    point_c = Point(1.5, "c")
    point_d = Point(2.5, "d")        

    point_tier1 = PointTier(name = "test1", entries = [point_a, point_b])
    point_tier2 = PointTier(name = "test2", entries = [point_c, point_d])

    seq_point_tier1 = SequencePointTier(point_tier1)
    seq_point_tier2 = SequencePointTier(point_tier2)

    point_group = PointsGroup(
        [seq_point_tier1, seq_point_tier2]
    )        

    def test_shift(self):
        orig_times = [
            tier.times 
            for tier in self.point_group.tier_list
        ]

        self.point_group.shift(3)

        new_times = [
            tier.times 
            for tier in self.point_group.tier_list
        ]

        for o, n in zip(orig_times, new_times):
            assert np.all(np.isclose(n-o, 3))
            
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

    def test_successful_access(self):
        assert self.seq_point_group1.MyPointClassA
        assert isinstance(self.seq_point_group1.MyPointClassA[0], self.MyPointClassA)
    
    def test_missing_access(self):
       with pytest.raises(AttributeError, match="has no attribute"):
           self.seq_point_group1.SequencePoint

    def test_too_many(self):
        with pytest.warns():
            seq_point_group2 = PointsGroup(tiers = [self.seq_point_tier1, self.seq_point_tier3])
            