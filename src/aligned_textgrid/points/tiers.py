from praatio.utilities.constants import Interval, Point
from praatio.data_classes.interval_tier import IntervalTier
from praatio.data_classes.point_tier import PointTier
from praatio.data_classes.textgrid import Textgrid
from aligned_textgrid.sequences.sequences import SequenceInterval, Top, Bottom
from aligned_textgrid.sequences.tiers import SequenceTier
from aligned_textgrid.points.points import SequencePoint
from aligned_textgrid.mixins.tiermixins import TierMixins, TierGroupMixins
from aligned_textgrid.mixins.within import WithinMixins
import numpy as np
from typing import Type
from collections.abc import Sequence
import warnings

class SequencePointTier(Sequence, TierMixins, WithinMixins):
    """A SequencePointTier class

    Args:
        tier (PointTier | list[Point]): 
            Either a `praatio` PointTier or a list of `praatio` Points
        entry_class (Type[SequencePoint]):
            A SequencePoint subclass
    
    Attributes:
        ...: 
            All attributes and methods included in TierMixins
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
        tier:PointTier|list[Point] = [], 
        entry_class:Type[SequencePoint] = SequencePoint
    ):
        if isinstance(tier, PointTier):
            self.entry_list = tier.entries
            self.name = tier.name
        else: 
            self.entry_list = tier
            self.name = entry_class.__name__

        self.entry_class = entry_class
        
        entry_order = np.argsort([x.time for x in self.entry_list])
        self.entry_list = [self.entry_list[idx] for idx in entry_order]
        self.sequence_list = []

        for entry in self.entry_list:
            this_point = self.entry_class(entry)
            self.sequence_list += [this_point]
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
        return np.array(
            [x.time for x in self.sequence_list]
        )
    
    @property
    def labels(self):
        return [x.label for x in self.sequence_list]
    
    @property
    def xmin(self):
        if len(self.sequence_list) > 0:
            return self.sequence_list[0].time
        else:
            return None
    
    @property
    def xmax(self):
        if len(self.sequence_list) > 0:
            return self.sequence_list[-1].time
        else:
            return None
    
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

    Args:
        tiers (list[SequencePointTier]: 
            A list of SequencePointTiers
    
    Attributes:
        ...:
            All attributes and methods availale from TierGroupMixins
        entry_classes (list[Type[SequencePointTier],...]):
            A list of the entry classes
    """    
    def __init__(
            self,
            tiers: list[SequencePointTier] = [SequencePointTier()]
    ):
        self.tier_list = tiers
        self.contains = self.tier_list
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
    
