from src.modeling import _base_estimator, make_pipeline
from src.preprocessing import FeatureMeta


def test_regularized_model_variants_are_explicit():
    assert _base_estimator("logreg_c0.1", 42).C == 0.1
    assert _base_estimator("logreg_c2.0", 42).C == 2.0
    assert _base_estimator("extra_trees_leaf5", 42).min_samples_leaf == 5


def test_logistic_variant_still_scales_numeric_features():
    pipeline = make_pipeline(
        "logreg_c0.1",
        FeatureMeta(numeric_cols=["x"]),
        random_state=42,
    )

    numeric = pipeline.named_steps["pre"].transformers[0][1]
    assert "scale" in numeric.named_steps
