from . import dataframe_dataset, dataframe_lambdas, dataframe_optimize
from . import dataframe_quickplot, dataframe_tests
from . import series_asciiplot, series_datetime
from . import series_map_categorical_binning, series_map_numerical_binning
from . import series_pctg, series_scaler, series_tests
from .series_scaler import standardize
from .pipeline import Pipeline
from ._utils import makeDataFrame

__version__ = "0.0.1rc0"
