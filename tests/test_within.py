from aligned_textgrid.mixins.within import WithinMixins
from aligned_textgrid import AlignedTextGrid, Word, Phone,\
                            SequenceTier
from aligned_textgrid.sequences.tiers import TierGroup
from aligned_textgrid.points.tiers import PointsGroup, SequencePointTier
from aligned_textgrid.polar.polar_classes import PrStr, ToBI, \
    TurningPoints, Ranges, Levels, Misc
from aligned_textgrid.polar.polar_grid import PolarGrid

class TestWithin:

    class Alpha(WithinMixins):
        def __init__(self):
            pass

    class Beta(WithinMixins):
        def __init__(self):
            pass        

    def test_within(self):
        this_a = self.Alpha()
        a_list = [this_a]

        assert not this_a.within
        
        this_a.within = a_list

        assert type(this_a.within) is list
        assert this_a in this_a.within

class TestContains:

    class Alpha(WithinMixins):
        def __init__(self):
            pass

    class Beta(WithinMixins):
        def __init__(self):
            pass

    class Delta(WithinMixins):
        def __init__(self):
            pass

    def test_contains(self):
        this_a = self.Alpha()
        this_b = self.Beta()

        assert len(this_b.contains) == 0

        this_b.contains = [this_a]

        assert len(this_b.contains) == 1
        assert this_a.within is this_b

        assert this_a.within_index == 0

    def test_path(self):
        this_a1 = self.Alpha()
        this_b1 = self.Beta()
        this_b2 = self.Beta()
        this_d1 = self.Delta()
        this_d2 = self.Delta()

        this_a1.contains = [this_b1, this_b2]
        this_b1.contains = [this_d1]
        this_b2.contains = [this_d2]

        d1_path = this_d1.within_path
        d2_path = this_d2.within_path

        assert len(d1_path) == 2
        for x,y in zip(d1_path, [0,0]):
            assert x==y

        for x,y in zip(d2_path, [1,0]):
            assert x==y

        assert len(this_b2.within_path) == 1
    
    def test_id(self):
        this_a1 = self.Alpha()
        this_b1 = self.Beta()
        this_b2 = self.Beta()
        this_d1 = self.Delta()
        this_d2 = self.Delta()

        this_a1.contains = [this_b1, this_b2]
        this_b1.contains = [this_d1]
        this_b2.contains = [this_d2]

        assert this_d1.id == "0-0"
        assert this_d2.id == "1-0"

class TestWithinTG:

    one_tg = AlignedTextGrid(
        textgrid_path="tests/test_data/josef-fruehwald_speaker.TextGrid",
        entry_classes=[Word, Phone]
    )
    
    two_tg = AlignedTextGrid(
        textgrid_path="tests/test_data/KY25A_1.TextGrid",
        entry_classes=[Word, Phone]
    )

    entry_classes = [
        [Word, Phone],
        [ToBI, PrStr, TurningPoints, Levels],
        [Ranges]
    ]
    ptg = PolarGrid(
        textgrid_path="tests/test_data/amelia_knew2-basic.TextGrid",
        entry_classes=entry_classes
    )


    def test_classes_correct(self):
        phone_interval = self.one_tg[0].Phone[0]
        assert isinstance(phone_interval, Phone)
        assert isinstance(phone_interval.within, Word)
        assert isinstance(phone_interval.within.within, SequenceTier)
        assert isinstance(phone_interval.within.within.within, TierGroup)
        assert isinstance(phone_interval.within.within.within.within, AlignedTextGrid)

    def test_within_path(self):
        phone_interval1 = self.one_tg[0].Phone[0]

        phone_interval2 = self.two_tg[1].Phone[0]

        assert len(phone_interval1.within_path) == 4
        assert phone_interval1.id == "0-0-0-0"

        assert len(phone_interval2.within_path) == 4
        assert phone_interval2.id == "1-0-0-0"

    def test_path_subset(self):
        """
        The id of superset instances should be a subset
        of the subset instance id
        """
        for phone in self.one_tg[0].Phone:
            assert phone.within.id in phone.id
    
    def test_points_within(self):
        prstr = self.ptg[1].PrStr.first
        
        assert isinstance(prstr.within, SequencePointTier)
        assert isinstance(prstr.within.within, PointsGroup)
        assert isinstance(prstr.within.within.within, PolarGrid)

        assert prstr.id == "1-1-0"