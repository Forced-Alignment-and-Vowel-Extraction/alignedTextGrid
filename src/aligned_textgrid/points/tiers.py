from praatio.utilities.constants import Interval, Point
from praatio.data_classes.interval_tier import IntervalTier
from praatio.data_classes.point_tier import PointTier
from praatio.data_classes.textgrid import Textgrid
from aligned_textgrid.sequences.sequences import SequenceInterval, Top, Bottom
from aligned_textgrid.sequences.tiers import SequenceTier
from aligned_textgrid.points.points import SequencePoint
from aligned_textgrid.mixins.tiermixins import TierMixins, TierGroupMixins
from aligned_textgrid.mixins.within import WithinMixins
from aligned_textgrid.sequence_list import SequenceList
import numpy as np
from typing import Type
from collections.abc import Sequence

import sys
if sys.version_info >= (3,11):
    from typing import Self
else:
    from typing_extensions import Self

import warnings

class SequencePointTier(Sequence, TierMixins, WithinMixins):
    """A SequencePointTier class

    `SequencePointTier`s have all the same methods and attributes as
    [](`~aligned_textgrid.mixins.tiermixins.TierMixins`) and 
    [](`~aligned_textgrid.mixins.within.WithinMixins`)

    Args:
        tier (list[Point]|list[SequencePoint]|PointTier|Self): 
            A list of SequencePoints, or another SequencePointTier
        entry_class (Type[SequencePoint]):
            A SequencePoint subclass

    Examples:
        ```{python}
        from aligned_textgrid import SequencePoint, SequencePointTier

        point_a = SequencePoint((0,"a"))
        point_b = SequencePoint((1, "b"))

        point_tier = SequencePointTier([point_a, point_b])

        print(point_tier)
        ```

        ```{python}
        print(point_tier.sequence_list)
        ```

    Attributes:
        entry_class (Type[SequencePoint]):
            The class of entries within the tier
        name (str):
            The name of the tier
        times (np.array):
            The times of points in the tier
        labels (list[str,...]):
            The labels of points in the tier
        xmin (float):
            The time of the first point in the tier
        xmax (float):
            The time of the last point in the tier
        []:
            Indexable and iterable
        
    """
    def __init__(
        self, 
        tier:list[Point]|list[SequencePoint]|SequenceList|PointTier|Self = [], 
        entry_class:Type[SequencePoint] = None
    ):
        to_check = tier
        if isinstance(tier, PointTier):
            to_check = tier.entries
        
        has_class = any([hasattr(x, "entry_class") for x in to_check])

        if not entry_class and has_class:
            entry_class = tier[0].entry_class
        
        if not entry_class and not has_class:
            entry_class = SequencePoint

        name = entry_class.__name__
        entries = tier

        if isinstance(tier, PointTier):
            entries = tier.entries
            name = tier.name

        if isinstance(tier, SequencePointTier):
            entries = tier.entry_list
            if tier.name != tier.entry_class.__name__:
                name = tier.name
        
        self.entry_list = entries
        self.entry_class = entry_class
        self.name = name
        entry_order = np.argsort([x.time for x in self.entry_list])
        self.entry_list = [self.entry_list[idx] for idx in entry_order]
        self.sequence_list = SequenceList()
       
        for entry in self.entry_list:
            this_point = self.entry_class._cast(entry)
            self.sequence_list.append(this_point)
        self.__set_precedence()
    
    def __getitem__(self, idx):
        return self.sequence_list[idx]
    
    def __len__(self):
        return len(self.sequence_list)

    def __set_precedence(self):
        for idx,seq in enumerate(self.sequence_list):
            self.__set_intier(seq)
            if idx == 0:
                seq.set_initial()
            else:
                seq.set_prev(self.sequence_list[idx-1])
            if idx == len(self.sequence_list)-1:
                seq.set_final()
            else:
                seq.set_fol(self.sequence_list[idx+1])
        self.contains = self.sequence_list

    def __set_intier(
            self,
            entry
        ):
        entry.intier = self
        entry.tiername = self.name                 

    def __repr__(self):
        return f"Sequence Point tier of {self.entry_class.__name__};"

    @property
    def times(self):
        return self.sequence_list.starts
    
    @times.setter
    def times(self, new_times):
        if not len(self.sequence_list) == len(new_times):
            raise Exception("There aren't the same number of new start times as intervals")
        
        for p, t in zip(self.sequence_list, new_times):
            p.time = t

    @property
    def labels(self):
        return self.sequence_list.labels
    
    @property
    def xmin(self):
        if len(self.sequence_list) > 0:
            return self.sequence_list.starts.min()
        else:
            return None
    
    @property
    def xmax(self):
        if len(self.sequence_list) > 0:
            return self.sequence_list.starts.max()
        else:
            return None
        
    def _shift(self, increment):
        self.times += increment
    
    def cleanup(self):
        pass
    
    def get_nearest_point_index(
            self, 
            time: float
        ) -> int:
        """Returns the index of the closest point to `time`

        Args:
            time (float): The time at which to get the nearest point

        Returns:
            (int): The index of the nearest point within the tier
        """
        out_idx = np.abs(self.times-time).argmin()
        return out_idx
    
    def get_nearest_point(
            self,
            time:float
        )->SequencePoint:
        """Returns nearest point

        Args:
            time (float): time at which to get the nearest point

        Returns:
            (SequencePoint): the nearest point to `time`
        """
        out_idx = self.get_nearest_point_index(time)
        return self.sequence_list[out_idx]

    def return_tier(self) -> PointTier:
        """Returns SequencePointTier as a `praatio` PointTier

        Returns:
            (PointTier): A `praatio` point tier
        """
        all_points = [entry.return_point() for entry in self.sequence_list]
        point_tier = PointTier(name = self.name, entries=all_points)
        return(point_tier)
    
    def save_as_tg(
            self, 
            save_path: str):
        """Saves the current point tier as a textgrid

        Args:
            save_path (str): path to where you want to save the textgrid.
        """
        point_tier = self.return_tier()
        out_tg = Textgrid()
        out_tg.addTier(tier = point_tier)
        out_tg.save(save_path, "long_textgrid")

class PointsGroup(Sequence, TierGroupMixins, WithinMixins):
    """A collection of point tiers
    `PointsGroup`s have all the same methods and attributes as
    [](`~aligned_textgrid.mixins.tiermixins.TierGroupMixins`) and 
    [](`~aligned_textgrid.mixins.within.WithinMixins`)

    Args:
        tiers (list[SequencePointTier]|PointsGroup): 
            A list of SequencePointTiers
    
    Attributes:
            A list of the entry classes
    """    
    def __init__(
            self,
            tiers: list[SequencePointTier]|Self = [SequencePointTier()]
    ):
        if isinstance(tiers, PointsGroup):
            tiers = [tier for tier in tiers]
        self.tier_list = tiers
        self.contains = self.tier_list
        self._set_tier_names()
        self._name = self.make_name()

    def __getitem__(
            self,
            idx: int|list
    ):
        if type(idx) is int:
            return self.tier_list[idx]
        if len(idx) != len(self):
            raise Exception("Attempt to index with incompatible list")
        if type(idx) is list:
            out_list = []
            for x, tier in zip(idx, self.tier_list):
                out_list.append(tier[x])
            return(out_list)
    
    def __len__(self):
        return len(self.tier_list)

    def shift(
        self, 
        increment: float
    ):
        """Shift the times of all points within
        the PointsGroup by the increment size

        Args:
            increment (float): 
                The time increment by which to shift the
                points within the PointsGroup. Could be
                positive or negative
        """

        for tier in self.tier_list:
            tier._shift(increment)

    def get_nearest_points_index(
            self, 
            time: float
        ) -> list:
        """Get indicies of nearest point

        Args:
            time (float): time from which the nearest index should be returned.

        Returns:
            list: A list of indices
        """
        return [tier.get_nearest_point_index(time) for tier in self.tier_list]

    def get_intervals_at_time(self, time):
        # convenience function to play nice with 
        # AlignedTextGrid.get_intervals_at_time
        return self.get_nearest_points_index(time)
    
    @property
    def entry_classes(self):
        return [x.entry_class for x in self.tier_list]
    
    @property
    def xmin(self):
        times = np.array(
            [t.xmin for t in self.tier_list]
        )
        return times.min()

    @property    
    def xmax(self):
        times = np.array(
            [t.xmin for t in self.tier_list]
        )
        return times.max()
    
    def __repr__(self):
        n_tiers = len(self.tier_list)
        classes = [x.__name__ for x in self.entry_classes]
        return f"PointsGroup with {n_tiers} tiers. {repr(classes)}"
    
SequencePointTier._set_seq_type(SequencePoint)
PointsGroup._set_seq_type(SequencePoint)