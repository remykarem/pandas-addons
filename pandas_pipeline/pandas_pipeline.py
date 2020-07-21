import math
from functools import reduce
from itertools import combinations

import pandas as pd
import colorful as cf
from pandas import CategoricalDtype


@pd.api.extensions.register_dataframe_accessor("pipeline")
class Pipeline:
    """
    df.pipeline.transform({
        "Survived": {"astype": "category"}
    })
    """

    stuff = "fff"

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def drop_duplicate_columns(self, inplace=False):
        to_drop = []
        pairs = combinations(self._obj.columns, 2)

        num_combinations = math.comb(len(self._obj.columns), 2)
        print(f"Checking {num_combinations} combinations")

        for pair in pairs:
            col_a, col_b = pair
            if col_a in to_drop or col_b in to_drop:
                continue
            if self._obj[col_a].equals(self._obj[col_b]):
                to_drop.append(col_b)

        print(f"Duplicate columns: {to_drop}")

        return self._obj.drop(columns=to_drop, inplace=inplace)

    def drop_columns_apply(self, *functions):
        df = self._obj.copy()

        cols_to_drop = []
        for col_name in df:
            for f in functions:
                if all(df[col_name].apply(f)):
                    cols_to_drop.append(col_name)
                    break

        df = df.drop(columns=cols_to_drop)

        return df

    def drop_columns_sapply(self, *functions):
        df = self._obj.copy()

        cols_to_drop = []
        for col_name in df:
            for f in functions:
                if f(df[col_name]):
                    cols_to_drop.append(col_name)
                    break

        df = df.drop(columns=cols_to_drop)

        return df

    def dapply(self, *functions):
        """Functions must return something

        Returns
        -------
        pandas.DataFrame
            Mutated dataframe
        """
        df = self._obj.copy()
        run_steps = reduce(lambda f, g: lambda x: g(f(x)),
                           functions,
                           lambda x: x)
        return run_steps(df)

    @property
    def xinfo(self):
        return self._obj.info()

    def sapply(self, d, inplace=False):
        if not isinstance(d, dict):
            raise ValueError("Must be dict")
        if inplace:
            df = self._obj
        else:
            df = self._obj.copy()

        for cols, function in d.items():
            if len(cols) == 1 or isinstance(cols, str):
                col_old, col_new = cols, cols
            elif len(cols) == 2:
                col_old, col_new = cols
            else:
                raise ValueError("Wrong key")
            df[col_new] = function(df[col_old])

        return df

    def map_categorical_binning(self, binnings, inplace=False):
        df = self._obj if inplace else self._obj.copy()

        for cols, binning in binnings.items():
            if len(cols) == 1 or isinstance(cols, str):
                col_old, col_new = cols, cols
            elif len(cols) == 2:
                col_old, col_new = cols
            else:
                raise ValueError("Wrong key")

            mapping = {v: k for k, values in binning.items()
                       for v in values}
            df[col_new] = df[col_old].map(mapping)

        return df

    def map(self, mappings, inplace=False):
        df = self._obj if inplace else self._obj.copy()

        for cols, mapping in mappings.items():
            if len(cols) == 1 or isinstance(cols, str):
                col_old, col_new = cols, cols
            elif len(cols) == 2:
                col_old, col_new = cols
            else:
                raise ValueError("Wrong key")
            df[col_new] = df[col_old].map(mapping)

        return df if inplace else None

    def apply(self, d, inplace=False):
        df = self._obj if inplace else self._obj.copy()

        for cols, function in d.items():
            if len(cols) == 1 or isinstance(cols, str):
                col_old, col_new = cols, cols
            elif len(cols) == 2:
                col_old, col_new = cols
            else:
                raise ValueError("Wrong key")
            df[col_new] = df[col_old].apply(function)

        return df

    def fillna(self, d, inplace=False):
        df = self._obj if inplace else self._obj.copy()

        for cols, fill_value in d.items():
            if len(cols) == 1 or isinstance(cols, str):
                col_old, col_new = cols, cols
            elif len(cols) == 2:
                col_old, col_new = cols
            else:
                raise ValueError("Wrong key")

            df[col_new] = df[col_old].fillna(fill_value)

        return df

    def convert_dtypes(self, d, inplace=False):
        df = self._obj if inplace else self._obj.copy()

        for cols, params in d.items():

            if isinstance(cols, str):
                if cols == "*":
                    cols = tuple(list(df))
                else:
                    cols = tuple([cols])

            if params == "index":
                df = df.set_index(cols[0])
                continue

            for col in cols:
                if isinstance(params, type):
                    if params.__name__ not in ["int", "float", "bool", "str"]:
                        raise ValueError("Wrong type")
                elif isinstance(params, str):
                    if params not in ["category", "int", "float", "bool", "str"]:
                        raise ValueError("Wrong type")
                elif not isinstance(params, CategoricalDtype):
                    raise ValueError("Wrong type")

                df[col] = df[col].astype(params)
        return df

    def to_numerics(self, target=None, inplace=False,
                    remove_missing=True):
        """Convert dataframe to numpy values

        Parameters
        ----------
        target : [type], optional
            [description], by default None
        inplace : bool, optional
            [description], by default False
        remove_missing : bool, optional
            [description], by default True

        Returns
        -------
        [type]
            [description]
        """
        df = self._obj if inplace else self._obj.copy()
        df = df.select_dtypes(exclude=["object"])

        if remove_missing:
            df = df.dropna(axis=0)

        nominal_categories = []
        for col in df:
            if df[col].dtype.name == "category":
                if not df[col].dtype.ordered:
                    nominal_categories.append(col)
                df[col] = df[col].cat.codes + int(df[col].hasnans)
            elif df[col].dtype.name == "bool":
                df[col] = df[col].astype(int)

        if target:
            X, y = df.loc[:, df.columns != target], df[target]
            X, y = X.values, y.values
            categories = [X.columns.get_loc(col)
                          for col in nominal_categories]
            return X, y, categories
        else:
            categories = [df.columns.get_loc(col)
                          for col in nominal_categories]
            return df.values, categories


@pd.api.extensions.register_series_accessor("pctg")
class Percentage:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    @property
    def zeros(self):
        return (self._obj == 0).sum() / len(self._obj)

    @property
    def nans(self):
        return self._obj.isna().sum() / len(self._obj)

    @property
    def uniques(self):
        return self._obj.nunique() / len(self._obj)


@pd.api.extensions.register_dataframe_accessor("optimize")
class Optimize:
    """
    df.pipeline.transform({
        "Survived": {"astype": "category"}
    })
    """

    def __init__(self, pandas_obj):
        #         self._validate(pandas_obj)
        self._obj = pandas_obj
        self.history = None
        self._params = {}

    def drop_with_rules(self, *functions):
        pass

    def convert_categories(self, max_cardinality=20, inplace=False):
        if inplace:
            df = self._obj
        else:
            df = self._obj.copy()

        for col in df:
            if not df[col].dtype == "object":
                continue

            num_uniques = df[col].nunique()

            if num_uniques == 1:
                # Drop this column!
                print(cf.red(f"{col} has only 1 value."))
            elif num_uniques <= max_cardinality:
                df[col] = df[col].astype("category")

        if inplace:
            return None
        else:
            return df

    def __call__(self, dry_run=True, max_cardinality=20):

        befores = 0
        afters = 0

        for col in self._obj:

            num_uniques = self._obj[col].nunique()
            before = self._obj[col].memory_usage(index=False)
            befores += before

            if num_uniques == 1:
                print(
                    cf.red(f"{col} has only 1 value. Drop to save {before}."))
            elif num_uniques == 2:
                if self._obj[col].dtype.name in ["category", "bool"]:
                    print(cf.green(f"{col} looks good"))
                    continue
                after = self._obj[col].astype(
                    "category").memory_usage(index=False)
                afters += after
                savings = (before-after)/before * 100

                # if containts yes-no or true-false or t-f or 1-0

                print(cf.red(f"{col} can be optimised. "
                             "Consider bool or cat. "
                             f"Consider category. Save {savings:.0f}%"))
            elif num_uniques == 3:
                if self._obj[col].dtype.name in ["category", "bool"]:
                    print(cf.green(f"{col} looks good"))
                    continue
                after = self._obj[col].astype(
                    "category").memory_usage(index=False)
                afters += after
                savings = (before-after)/before * 100

            elif num_uniques <= max_cardinality:
                # print(self._obj[col].memory_usage(index=False))
                if self._obj[col].dtype == "object":
                    print(cf.red(f"{col} can be optimised. "
                                 f"{num_uniques} uniques found. "
                                 f"Consider category."))
                elif self._obj[col].dtype.name.startswith("int"):
                    after = self._obj[col].astype(
                        "category").memory_usage(index=False)
                    afters += after
                    savings = (before-after)/before * 100
                    print(cf.red(f"{col} can be optimised. "
                                 f"{num_uniques} uniques found. "
                                 f"Consider category. Save {savings:.0f}%"))
                elif self._obj[col].dtype.name in ["category", "bool"]:
                    print(cf.green(f"{col} looks good"))
                    continue
                else:
                    print(f"{col} not evaluated")
            else:
                print(cf.green(f"{col} looks good"))

        # print(f"Before: {befores/1e6:.1f}MB")
        # print(f"Total savings: {(befores-afters)/1e6:.1f}MB")
        print(f"Total savings: {afters/1e6:.1f}MB")
