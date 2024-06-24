import polars as pl
from aligned_textgrid import SequenceInterval, \
                             SequencePoint, \
                             SequenceTier, \
                             SequencePointTier, \
                             AlignedTextGrid

from aligned_textgrid.sequences.tiers import TierGroup
from aligned_textgrid.points.tiers import PointsGroup


def sequence_to_df(
        obj: SequenceInterval | SequencePoint,
        with_subset: bool = True
        ) -> pl.DataFrame:
    
    attributes_to_get = [
        "id",
        "tier_index",
        "label",
        "start", 
        "end"
    ]

    class_name = type(obj).__name__

    if isinstance(obj, SequencePoint):
        attributes_to_get.pop(
            attributes_to_get.index("end")
        )

    col_names = attributes_to_get
    if isinstance(obj, SequenceInterval) and with_subset:
        col_names = [
            f"{class_name}_{att}" for att in attributes_to_get
        ]


    sub_df_rows = None
    if len(obj.contains) > 0 and with_subset:
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

    if isinstance(obj, SequencePoint) or not with_subset:
        df = df.with_columns(
            entry_class = pl.lit(class_name)
        )

    return df


def tier_to_df(
        obj: SequenceInterval | SequencePointTier,
        with_subset: bool = True
        ) -> pl.DataFrame:
    
    all_interval_dfs = [
        sequence_to_df(x, with_subset) for x in obj
    ]

    out_df = pl.concat(all_interval_dfs, how="diagonal")
    return out_df


def tiergroup_to_df(
        obj: TierGroup | PointsGroup,
        with_subset: bool = True
        ) -> pl.DataFrame:

    if isinstance(obj, TierGroup) and with_subset:
        out_df = tier_to_df(obj[0], with_subset)
    else:
        all_df = [
            tier_to_df(x, with_subset) for x in obj
        ]
        out_df = pl.concat(all_df, how = "diagonal")

    if hasattr(obj, "name"):
       out_df = out_df.with_columns(
            name=pl.lit(obj.name)
        )

    return out_df


def textgrid_to_df(
        obj: AlignedTextGrid,
        with_subset: bool = True
        ) -> pl.DataFrame:

    all_df = [
        tiergroup_to_df(x, with_subset) for x in obj
    ]

    out_df = pl.concat(all_df, how="diagonal")

    return out_df


def to_df(
        obj: SequenceInterval | SequencePoint | SequenceTier |
        SequencePointTier | TierGroup | PointsGroup |
        AlignedTextGrid,
        with_subset: bool = True        
        ) -> pl.DataFrame:
    """Return an `aligned_textgrid` object as a dataframe

    Args:
        obj (SequenceInterval | SequencePoint | SequenceTier | SequencePointTier | TierGroup | PointsGroup | AlignedTextGrid): An `aligned_textgrid` object
        with_subset (bool, optional): Whether or not to include subset relationships. Defaults to True.

    Returns:
        (pl.DataFrame): A polars dataframe
    """
    if isinstance(obj, SequenceInterval) or isinstance(obj, SequencePoint):
       return sequence_to_df(obj, with_subset)
    
    if isinstance(obj, SequenceTier) or isinstance(obj, SequencePointTier):
        return tier_to_df(obj, with_subset)
    
    if isinstance(obj, TierGroup) or isinstance(obj, PointsGroup):
        return tiergroup_to_df(obj, with_subset)

    if isinstance(obj, AlignedTextGrid):
        return textgrid_to_df(obj, with_subset)

    raise ValueError("obj is not an aligned-textgrid class.")
