import numpy as np
import pandas as pd

from src.preprocessing import FeatureMeta, build_preprocessor


def test_preprocessor_keeps_fold_empty_numeric_feature():
    meta = FeatureMeta(numeric_cols=["sparse_vital"])
    train = pd.DataFrame({"sparse_vital": [np.nan, np.nan, np.nan]})
    test = pd.DataFrame({"sparse_vital": [12.0]})

    transformer = build_preprocessor(meta)
    train_out = transformer.fit_transform(train)
    test_out = transformer.transform(test)

    assert train_out.shape == (3, 1)
    assert test_out.shape == (1, 1)
