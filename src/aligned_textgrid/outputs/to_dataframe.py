import polars as pl
from aligned_textgrid import SequenceInterval, \
                             SequencePoint, \
                             SequenceTier, \
                             SequencePointTier, \
                             AlignedTextGrid

from aligned_textgrid.sequences.tiers import TierGroup
from aligned_textgrid.points.tiers import PointsGroup

from typing import Union

def sequence_to_df(
        obj: SequenceInterval | SequencePoint
        ) -> pl.DataFrame:
    
    attributes_to_get = [
        "id",
        "tier_index",
        "label"
    ]

    if isinstance(obj, SequenceInterval):
        attributes_to_get += ["start", "end"]

    if isinstance(obj, SequencePoint):
        attributes_to_get += ["time"]

    class_name = type(obj).__name__
    col_names = [
        f"{class_name}_{att}" for att in attributes_to_get
    ]

    sub_df_rows = None
    if len(obj.contains) > 0:
        sub_df_list = [sequence_to_df(x) for x in obj.contains]
        sub_df = pl.concat(sub_df_list, how="diagonal")
        sub_df_rows = sub_df.shape[0]

    out_dict = {
        att: getattr(obj, att)
        for att in attributes_to_get
    }

    df = pl.DataFrame(out_dict, schema=col_names)
    if sub_df_rows:
        df = df.with_columns(
            n=pl.lit(sub_df_rows)
        ).select(
            pl.exclude("n").repeat_by("n").explode()
        )
        df = pl.concat([df, sub_df], how="horizontal")

    return df


def tier_to_df(
        obj: SequenceInterval | SequencePointTier
        ) -> pl.DataFrame:
    
    all_interval_dfs = [
        sequence_to_df(x) for x in obj
    ]

    out_df = pl.concat(all_interval_dfs, how="diagonal")
    return out_df


def tiergroup_to_df(
        obj: TierGroup | PointsGroup
        ) -> pl.DataFrame:

    out_df = tier_to_df(obj[0])
    if hasattr(obj, "name"):
        out_df.with_columns(
            name=pl.lit(obj.name)
        )

    return out_df


def textgrid_to_df(
        obj: AlignedTextGrid
        ) -> pl.DataFrame:

    all_df = [
        tiergroup_to_df(x) for x in obj
    ]

    out_df = pl.concat(all_df, how="diagonal")

    return out_df


def to_df(
        obj: SequenceInterval | SequencePoint | SequenceTier |
        SequencePointTier | TierGroup | PointsGroup |
        AlignedTextGrid
        ) -> pl.DataFrame:
    
    if isinstance(obj, SequenceInterval) or isinstance(obj, SequencePoint):
       return sequence_to_df(obj)
    
    if isinstance(obj, SequenceTier) or isinstance(obj, SequencePointTier):
        return tier_to_df(obj)
    
    if isinstance(obj, TierGroup) or isinstance(obj, PointsGroup):
        return tiergroup_to_df(obj)

    if isinstance(obj, AlignedTextGrid):
        return textgrid_to_df(obj)

    raise ValueError("obj is not an aligned-textgrid class.")
