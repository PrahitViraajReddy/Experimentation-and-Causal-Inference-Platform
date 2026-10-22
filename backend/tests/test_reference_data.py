from app.scripts.generate_reference_data import generate


def test_reference_dataset_is_reproducible():
    first = generate(seed=7, sample_size_per_arm=20)
    second = generate(seed=7, sample_size_per_arm=20)
    assert first.equals(second)


def test_reference_dataset_has_expected_groups_and_columns():
    data = generate(seed=42, sample_size_per_arm=25)
    assert len(data) == 50
    assert set(data["variant"]) == {"control", "treatment"}
    assert set(data["converted"].unique()).issubset({0, 1})
    assert {"user_id", "variant", "converted", "revenue", "seed"} <= set(data.columns)
    assert data["user_id"].is_unique
