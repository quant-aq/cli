from loguru import logger
import pandas as pd
import rich
from rich.table import Table

from quantaq_cli.variables import FLAG_DEFINITIONS, FLAG_VALUES
from quantaq_cli.variables import Range, Gap, Single, Multiple, Ratio, OPS, flag_name_to_criteria
from quantaq_cli.utilities import fix_timestamps, determine_timestamp_column
from quantaq_cli.utilities import infer_data_source, infer_data_model
from quantaq_cli.schema import validate_schema


def evaluate_criterion(df, criterion):
    """Create a mask that is True for every row meeting the flag criterion.
    
    Args:
        df (pd.DataFrame): DataFrame to mask.
        criterion: The rule used to decide which rows should be flagged. 
    
    Returns:
        pd.Series: Boolean mask - True for rows that meet the criterion.
    """
    
    if isinstance(criterion, Range):
        if criterion.column not in df.columns:
            return pd.Series(False, index=df.index)
        col = df[criterion.column]
        mask = (col < criterion.lo) | (col > criterion.hi)
        return mask
    
    elif isinstance(criterion, Single):
        if criterion.column not in df.columns:
            return pd.Series(False, index=df.index)
        col = df[criterion.column]
        mask = OPS[criterion.op](col, criterion.value)
        return mask
    
    elif isinstance(criterion, Ratio):
        if (
            criterion.column_denominator not in df.columns
            or criterion.column_numerator not in df.columns
        ):
            return pd.Series(False, index=df.index)
        ratio = df[criterion.column_numerator] / df[criterion.column_denominator]
        mask = OPS[criterion.op](ratio, criterion.value)
        return mask

    elif isinstance(criterion, Gap):
        # to do: check if the dataframe is sorted here (this should be done before calling
        # _evaluate_criterion() -- we don't want to sort the df in this block unless
        # we also reindex the mask on the original df, so that we can combine masks

        # this block might need to live somewhere else, but basically, we don't bother
        # to set FLAG_STARTUP for devices without gas measurements since only the 
        # gas columns get nan'd when FLAG_STARTUP is set --- we don't have a 
        # startup flag for other devices yet so this is mostly to avoid confusion
        model = infer_data_model(df)
        if model not in {"modulair", "modulair-x"}:
            return pd.Series(False, index=df.index)

        tscol = determine_timestamp_column(df)
        tdiff = df[tscol].diff().dt.total_seconds()
        
        if criterion.warmup_min_lipo_soc is not None:
            # if there's a warmup_min_lipo_soc criterion (as in RAWSD_CRITERIA),
            # the gap_starts are defined if the device was offline for the past hour 
            # AND if the LIPO SOC is < warmup_min_lipo_soc (10%)
            gap_starts_mask = (tdiff > criterion.gap_in_seconds) & (df['soc'] < criterion.warmup_min_lipo_soc)
            gap_starts = df.loc[gap_starts_mask, tscol]
        else:
            # if there's no warmup_min_lipo_soc criterion (as in DATABASE_CRITERIA),
            # the gap_starts are defined only if the device was offine for the past hour
            gap_starts = df.loc[tdiff > criterion.gap_in_seconds, tscol]
        
        # set mask to True for every row that falls within post_gap_flag_length_seconds 
        # after any detected timestamp gap larger than gap_in_seconds
        postgap_delta = pd.Timedelta(seconds=criterion.post_gap_flag_length_seconds)
        mask = pd.Series(False, index=df.index)
        for ts in gap_starts: 
            mask |= (df[tscol] >= ts) & (df[tscol] <= ts + postgap_delta)
        return mask
            
    elif isinstance(criterion, Multiple):
        masks = [evaluate_criterion(df, c) for c in criterion.criteria]
        if criterion.logical_operator == "AND":
            # start with first mask and progressively AND the remaining ones
            mask = masks[0]
            for m in masks[1:]:
                mask = mask & m
            return mask
        else:
            # not bothering to implement logical_operator = "OR" because that's the
            # default behavior for items in the top-level criteria lists. 
            error = NotImplementedError(
            f"Unsupported logical_operator: {criterion.logical_operator!r} "
            f"(only 'AND' is implemented, use a regular criteria list for OR)"
            )
            logger.error(error)
            raise error
    else:
        error = NotImplementedError(f"Unsupported criterion type: {type(criterion)}")
        logger.error(error)
        raise error

def add_flag(df, mask, flag_name, flag_value):
    """Set the 'flag' column to the flag bitmask value if the mask evaluates to true.

    For each row that meets the specified criterion, this function modifies the 'flag' 
    column by applying a bitwise OR operation with the given flag value.

    Args:
        df (pd.DataFrame): DataFrame to which the flag will be added.
        flag_name (str): Name of the flag to be added.
        flag_value (int): Bitmask value of the flag to be added.
        mask (pd.Series): True where the flag criterion are true.
    
    Returns:
        pd.DataFrame: DataFrame with the flag added.
    """
    if not mask.any(): # skip if every value in the mask is False
        return df
    df.loc[mask, "flag"] |= flag_value  
    logger.info(
        f"Flagged: {flag_name} (flag {flag_value}) --> {mask.sum()} rows",
    )

    return df

def flag_summary(df):
    """Create a table with a summary of flags.

    Args:
        df (pd.DataFrame): DataFrame with flags to summarize.
    
    Returns:
        pd.DataFrame: A new DataFrame, suitable for human consumption.
    """

    # create flag column if it doesn't exist
    if "flag" not in df.columns:
        df["flag"] = 0

    # force the flag column to be an int
    df["flag"] = df["flag"].astype(int, errors='ignore')

    rows = []
    for name, value, _ in FLAG_DEFINITIONS:
        mask = df["flag"] & value
        num_naffected = mask.astype(bool).sum()
        percent_affected = f"{100 * num_naffected / df.shape[0]:.1f}"
        rows.append([name, int(value), num_naffected, percent_affected])

    explained_df = pd.DataFrame(
        rows,
        columns=["FLAG", "FLAG VALUE", "# OCCURENCES", "% DATA"],
    ).set_index("FLAG")
    return explained_df

def echo_flag_table(df):
    """Print a table of flag statistics for a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with flags to summarize.
    """
    explained_df = flag_summary(df)

    table = Table()
    for column in ["FLAG", *explained_df.columns]:
        table.add_column(
            column,
            justify="right" if column != "FLAG" else "left",
            style="bold",
        )
    for row in explained_df.itertuples():
        table.add_row(*map(str, row))
    rich.print(table)

def flag_dataframe(df):
    """Re-flags a DataFrame by iterating through the FLAG_DEFINITIONS and calling
    the _add_flag() function one-by-one.

    Args:
        df (pd.DataFrame): DataFrame to be flagged (or re-flagged).

    Returns:
        pd.DataFrame: The flagged DataFrame.
    """
    df = df.copy()

    # Drop nan flags (could happen after a merge)
    if "flag" not in df.columns:
        df["flag"] = 0
    elif df["flag"].isna().any():
        logger.warning("Dropping {} rows with NaN flags", df["flag"].isna().sum())
        df = df.dropna(how='any', subset=["flag"])

    # only need column names to be valid for flagging
    # we don't coerce dtypes so that merged files can be flagged
    # (this causes issues when the outer merge introduces nans in Int cols)
    df = validate_schema(df)

    source = infer_data_source(df)

    # get flag criteria (this also checks if the data source is valid)
    name_to_criteria = flag_name_to_criteria(source).items()

    # create flag column if it doesn't exist
    if "flag" not in df.columns:
        df["flag"] = 0


    # sort the dataframe once before adding flags
    df = fix_timestamps(df, sort_values=True)

    # set the flag for each flag_name and their respective crtieria 
    for flag_name, criteria in name_to_criteria:
        flag_value = FLAG_VALUES[flag_name]                      
        for criterion in criteria:
            mask =  evaluate_criterion(df, criterion)             
            df = add_flag(df, mask, flag_name, flag_value)
    return df
