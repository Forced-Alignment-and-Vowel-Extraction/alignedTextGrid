from aligned_textgrid import SequenceInterval, SequenceTier, Top
from aligned_textgrid.sequences.sequences import IntervalList
import numpy as np
from itertools import groupby, islice
import warnings
from typing import Callable


def take(n, iterable):
    "Return first n items of the iterable as a list."
    return list(islice(iterable, n))

def all_equal(iterable, key=None):
    "Returns True if all the elements are equal to each other."
    return len(take(2, groupby(iterable, key))) <= 1

def validate_entry_classes(
        intervals:list[SequenceInterval]|IntervalList = IntervalList()
    ):
    all_classes = [x.entry_class for x in intervals]
    if not all_equal(all_classes):
        raise ValueError(
            (
                "All SequenceIntervals must have the same class."
            )
        )
    return


def check_no_overlaps(
        intervals:list[SequenceInterval]|IntervalList = IntervalList(),
        warn: bool = True
)->bool:
    intervals = IntervalList(*intervals)
    starts = intervals.starts
    ends = intervals.ends

    a = np.array([e > starts for e in ends])
    b = np.array([s < ends for s in starts])

    n_overlaps = (a&b).sum()

    overlaps = n_overlaps > len(intervals)

    if overlaps and warn:
        warnings.warn("Some intervals provded overlap in time")

    return not n_overlaps > len(intervals)

def check_snug(
        intervals: list[SequenceInterval]|IntervalList  = IntervalList(),
        warn:bool = True
)->bool:
    intervals = IntervalList(*intervals)
    starts = np.array([x.start for x in intervals])
    ends = np.array([x.end for x in intervals])

    snug = np.allclose(starts[1:], ends[:-1])

    if (not snug) and warn:
        warnings.warn("There are gaps between some provided intervals.")
    
    return snug


def build_superset(
        intervals: list[SequenceInterval]|IntervalList = IntervalList(),
        label: str|Callable = lambda x: "".join(x)
):
    intervals = IntervalList(*intervals)
    if not check_no_overlaps(intervals):
        raise Exception("SequenceIntervals cannot overlap")
    snug = check_snug(intervals)
    validate_entry_classes(intervals)

    superset_class = intervals[0].superset_class

    if isinstance(superset_class, Top):
        warnings.warn("Cannot create superset as superset class is Top.")
        return

    start = intervals.starts.min()
    end = intervals.ends.max()

    if isinstance(label, Callable):
        label = label(intervals.labels)
    
    superset = superset_class((start, end, label))

    superset.subset_list = intervals
    
    return superset

