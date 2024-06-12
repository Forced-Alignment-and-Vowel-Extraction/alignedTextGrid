import pytest
from aligned_textgrid.sequences.tiers import SequenceTier, TierGroup
from aligned_textgrid.sequences.sequences import SequenceInterval
from aligned_textgrid.points.tiers import SequencePointTier, PointsGroup
from aligned_textgrid.points.points import SequencePoint
from aligned_textgrid.polar.polar_classes import PrStr, ToBI, \
    TurningPoints, Ranges, Levels, Misc
from aligned_textgrid.polar.polar_grid import PolarGrid
from aligned_textgrid.sequences.word_and_phone import Word, Phone
import numpy as np

class TestPolarGrid:
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

    def test_ptg_indexing(self):
        start = self.ptg.Word_Phone.xmin
        end = self.ptg.Word_Phone.xmax
        mid = ((end-start)/2)+start

        interval_idx = self.ptg.get_intervals_at_time(mid)
        results = self.ptg[interval_idx]

        assert len(interval_idx) == len(self.ptg)
        for int_gr, gr, res in zip(interval_idx, self.ptg, results):
            assert len(int_gr) == len(gr) == len(res)



class TestPolarClasses:
    entry_classes = [
        [Word, Phone],
        [ToBI, PrStr, TurningPoints, Levels],
        [Ranges]
    ]
    ptg = PolarGrid(
        textgrid_path="tests/test_data/amelia_knew2-basic.TextGrid",
        entry_classes=entry_classes
    )

    def test_ranges(self):
        range_ints = [x for x in self.ptg.Ranges]
        is_sequence = [isinstance(x, SequenceInterval) for x in range_ints]
        assert all(is_sequence)

        all_lows = [x.low for x in self.ptg.Ranges]
        is_float = [isinstance(x, np.float_) for x in all_lows]
        assert all(is_float)

        is_number = [not np.isnan(x) for x in all_lows]
        assert(any(is_number))

        all_ranges = [x.range for x in self.ptg.Ranges]
        assert all([len(x)==2 for x in all_ranges])

        all_bands = [x.bands for x in self.ptg.Ranges]
        assert all([len(x)==6 for x in all_bands])

    def test_prstr(self):
        prstr_points = [x for x in self.ptg.PrStr]
        is_point = [isinstance(x, SequencePoint) for x in prstr_points]
        assert all(is_point)

        certainties = [x.certainty for x in prstr_points]
        is_valid_cert = [x in ['certain', 'uncertain'] for x in certainties]
        assert all(is_valid_cert)

        all_status = [x.status for x in prstr_points]
        is_valid_status = [x in ["prominence", "edge"] for x in all_status]
        assert all(is_valid_status)

    def test_tobi(self):
        tobi_points = [x for x in self.ptg.ToBI]
        is_point = [isinstance(x, SequencePoint) for x in tobi_points]
        assert all(is_point)
    
    def test_tpoint(self):
        turning_points = [x for x in self.ptg.TurningPoints]
        is_point = [isinstance(x, SequencePoint) for x in turning_points]
        assert all(is_point)

        tpoint_levels = [x.level for x in turning_points]
        is_point2 = [isinstance(x, Levels) for x in tpoint_levels]
        assert all(is_point2)

    def test_levels(self):
        all_levels = [x for x in self.ptg.Levels]
        is_point = [isinstance(x, SequencePoint) for x in all_levels]
        assert all(is_point)

        level_range_tier = [x.ranges_tier for x in all_levels]
        is_tier = [isinstance(x, SequenceTier) for x in level_range_tier]
        assert all(is_tier)

        level_ranges = [x.range_interval for x in all_levels]
        is_interval = [isinstance(x, Ranges) for x in level_ranges]
        assert all(is_interval)

        level_levels = [x.level for x in all_levels]
        is_int = [isinstance(x, int) for x in level_levels]
        assert all(is_int)

        level_bands = [x.band for x in all_levels]
        is_array = [isinstance(x, np.ndarray) for x in level_bands]
        assert all(is_array)

    def test_properties(self):
        xmin = self.ptg.xmin
        xmax = self.ptg.xmax

        assert xmax > xmin