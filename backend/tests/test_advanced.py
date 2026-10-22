import pandas as pd
import pytest

from app.advanced import (
    bayesian_ab, sequential_ab, propensity_score_matching,
    difference_in_differences, synthetic_control, adjust_pvalues,
)


def test_bayesian_probability_moves_with_strong_treatment_signal():
    result = bayesian_ab(20, 500, 100, 500, draws=10000, seed=3)
    assert result["probability_treatment_better"] > 0.99
    assert result["risk_difference_credible_interval_95"][0] > 0


def test_sequential_uses_prespecified_per_look_alpha():
    result = sequential_ab(42, 500, 58, 500, alpha=0.05, looks=5, current_look=1)
    assert result["per_look_alpha"] == pytest.approx(0.01)
    assert result["planned_looks"] == 5


def test_multiple_testing_rejects_invalid_p_values():
    with pytest.raises(ValueError):
        adjust_pvalues([0.01, 1.5])


def test_did_recovers_known_two_by_two_effect():
    data = pd.DataFrame({
        "treated": [0,0,0,0,1,1,1,1],
        "post":    [0,0,1,1,0,0,1,1],
        "outcome": [10,12,12,14,10,12,17,19],
    })
    result = difference_in_differences(data, "treated", "post", "outcome")
    assert result["effect_estimate"] == pytest.approx(5.0)


def test_matching_requires_binary_treatment():
    data = pd.DataFrame({"t":[0,0,0,0,0,0,0,0,0,0], "y":range(10), "x":range(10)})
    with pytest.raises(ValueError):
        propensity_score_matching(data, "t", "y", ["x"])


def test_synthetic_control_requires_pre_and_post_periods():
    data = pd.DataFrame({"unit":["a","a","b","b"], "time":[0,1,0,1], "y":[1,2,1,2]})
    with pytest.raises(ValueError):
        synthetic_control(data, "unit", "time", "y", "a", 0)
