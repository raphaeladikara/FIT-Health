import numpy as np
import pandas as pd

from src.preprocessing import build_preprocessor, make_feature_frame


def test_stateless_derivation_preserves_category_strings():
    raw = pd.DataFrame(
        {
            "Centre de santé": ["DAFRA", "DO", "DAFRA"],
            "Symptom class": ["mild", "severe", None],
            "Temperature": ["37,2", "39,1", None],
        }
    )

    frame, meta = make_feature_frame(raw, list(raw.columns))

    assert frame["Centre de santé"].tolist() == ["DAFRA", "DO", "DAFRA"]
    assert frame["Symptom class"].iloc[:2].tolist() == ["mild", "severe"]
    assert set(meta.categorical_cols) == {"Centre de santé", "Symptom class"}


def test_fold_local_encoder_and_imputer_learn_training_rows_only():
    train = pd.DataFrame(
        {
            "site": ["A", "B", "A"],
            "temperature": [36.0, np.nan, 40.0],
        }
    )
    validation = pd.DataFrame(
        {
            "site": ["UNSEEN"],
            "temperature": [1000.0],
        }
    )
    train_frame, meta = make_feature_frame(train, list(train.columns))
    validation_frame = validation.assign(temperature__missing=0.0)
    transformer = build_preprocessor(meta)
    transformed_train = transformer.fit_transform(train_frame)
    transformed_validation = transformer.transform(validation_frame)

    encoder = transformer.named_transformers_["cat"].named_steps["encode"]
    imputer = transformer.named_transformers_["num"].named_steps["impute"]
    assert encoder.categories_[0].tolist() == ["A", "B"]
    assert imputer.statistics_[0] == 38.0
    assert transformed_train.shape[0] == len(train)
    assert transformed_validation.shape[0] == len(validation)
    assert transformer.get_feature_names_out().tolist() == [
        "temperature",
        "site_A",
        "site_B",
        "temperature__missing",
    ]


def test_repeated_fits_have_deterministic_columns_and_preserve_row_order():
    frame = pd.DataFrame(
        {
            "site": ["B", "A", "B"],
            "temperature": [38.0, 36.0, 37.0],
        },
        index=[8, 3, 5],
    )
    _, meta = make_feature_frame(frame, list(frame.columns))
    first = build_preprocessor(meta).fit(frame)
    second = build_preprocessor(meta).fit(frame)

    assert first.get_feature_names_out().tolist() == second.get_feature_names_out().tolist()
    output = first.transform(frame)
    assert output[:, 0].tolist() == [38.0, 36.0, 37.0]
