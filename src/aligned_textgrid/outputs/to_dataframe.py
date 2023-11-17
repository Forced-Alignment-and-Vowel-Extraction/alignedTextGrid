import polars as pl

def interval_to_df(self):
    attributes_to_get =[
        "tier_index",
        "start",
        "end",
        "label"
    ]
    class_name = type(self).__name__
    col_names = [
        f"{class_name}_{att}" for att in attributes_to_get
    ]    
    
    sub_df_rows = None
    if len(self.contains) > 0:
        sub_df = interval_to_df(self.contains)
        sub_df_rows = sub_df.shape[0]

    out_dict = {
        att: getattr(self, att)
        for att in attributes_to_get
    }

    df = pl.DataFrame(out_dict, schema=col_names)
    if sub_df_rows:
        df = df.with_columns(
            n = pl.lit(sub_df_rows)
        ).select(
            pl.exclude("n").repeat_by("n").explode()
        )
        df = pl.concat(df, sub_df, how="horizontal")

    return(df)