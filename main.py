#!/usr/bin/env python

import sys
from argparse import ArgumentParser

import pandas as pd


def parse_args():
    ap = ArgumentParser()
    ap.add_argument('--input-file', '--input_file', '-i', required=True, type=str, help='Input file name')
    ap.add_argument('--output-file', '--output_file', '-o', required=True, type=str, help='Output file name')
    ap.add_argument('--columns', '-c', type=str, nargs='+', required=True, help='Column names to keep')

    # Defaults to 'match any row'. See https://stackoverflow.com/a/53861261
    ap.add_argument('--query', '-q', type=str, help='Query string to apply', default='tuple()')
    return ap.parse_args()


def filter_columns(data, column_list):
    # First, check for each column's existence because pandas.Dataframe.loc[[]] doesn't seem
    # to understand that it should always raise KeyError when the column in a list doesn't exist
    # Example:
    #
    # In [20]: df = pd.DataFrame([[1, 2], [3, 4]], columns=['first', 'second'])
    #
    # In [21]: df
    # Out[21]:
    #    first  second
    # 0      1       2
    # 1      3       4
    #
    # In [22]: df.loc[:, ['first', 'third']]
    # /usr/lib/python3.7/site-packages/pandas/core/indexing.py:1418: FutureWarning:
    # Passing list-likes to .loc or [] with any missing label will raise
    # KeyError in the future, you can use .reindex() as an alternative.
    #
    # See the documentation here:
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#deprecate-loc-reindex-listlike
    #   return self._getitem_tuple(key)
    # Out[22]:
    #    first  third
    # 0      1    NaN
    # 1      3    NaN
    columns = set(data.columns)
    for col in column_list:
        if col not in columns:
            raise Exception(f'column `{col}` does not exist in the dataset')

    # Ok, having written these few lines of code to ensure adequate behaviour in case of invalid input,
    # let's proceed to the main, the most complex and meaningful part
    return data.loc[:, column_list]


def apply_query(data, query_string):
    try:
        return data.query(query_string)
    except Exception as e:
        raise Exception(f'invalid query: {e}') from e


def main():
    config = parse_args()
    data = pd.read_csv(config.input_file)
    data = filter_columns(data, config.columns)
    data = apply_query(data, config.query)
    data.to_csv(config.output_file, index=False, header=True)


def main_wrapper():
    try:
        main()
    except Exception as e:
        print(f'Error: {str(e)}', file=sys.stderr)


if __name__ == '__main__':
    main_wrapper()
