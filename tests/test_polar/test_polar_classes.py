import pytest
from aligned_textgrid.sequences.tiers import SequenceTier, TierGroup
from aligned_textgrid.sequences.sequences import SequenceInterval
from aligned_textgrid.points.ptiers import SequencePointTier, PointsGroup
from aligned_textgrid.points.points import SequencePoint
from aligned_textgrid.polar.polar_classses import PrStr, ToBI, \
    TurningPoints, Ranges, Levels, Misc
from aligned_textgrid.polar.polar_grid import PolarGrid
from aligned_textgrid.sequences.word_and_phone import Word, Phone

class TestGrid:
    entry_classes = [
        [Word, Phone],
        [ToBI, PrStr, TurningPoints, Levels],
        [Ranges]
    ]
    ptg = PolarGrid(
        textgrid_path="tests/test_data/amelia_knew2-basic.TextGrid",
        entry_classes=entry_classes
    )

    def test_read_success(self):
        assert self.ptg

    def test_ptg_len(self):
        assert len(self.ptg) == 3

    def test_tier_groups(self):
        assert isinstance(self.ptg[0], TierGroup)
        assert isinstance(self.ptg[1], PointsGroup)
        assert isinstance(self.ptg[2], TierGroup)

    def test_tier_classes(self):
        class_check_1 = [isinstance(x, SequenceTier) for x in self.ptg[0]]
        assert all(class_check_1)

        print(self.ptg[1])
        class_check_2 = [isinstance(x, SequencePointTier) for x in self.ptg[1]]
        assert all(class_check_2)

        class_check_3 = [isinstance(x, SequenceTier) for x in self.ptg[2]]
        assert all(class_check_3)
