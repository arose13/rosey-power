import pytest
from rich import print
from scipy import stats
from rosey_power import ExactPowerAnalysis, difference_in_means


@pytest.mark.parametrize('treatment_effect_size', ([0, 1, 5, 25, 50]))
def test_power_analysis_generally_working(treatment_effect_size):
    control = stats.norm(100, 15).rvs(1000)
    treatment = stats.norm(100 + treatment_effect_size, 15).rvs(100)

    test_stat = difference_in_means(treatment, control)

    # No sweep (PostHoc test)
    analysis_1_tail, analysis_2_tail = [ExactPowerAnalysis(treatment, control, is_two_tail=t) for t in (True, False)]

    analysis_1_tail.run(n_iter=int(10e3))
    analysis_2_tail.run(n_iter=int(10e3))

    p_value_1, p_value_2 = [(a._null_dists[0] > test_stat).mean() for a in (analysis_1_tail, analysis_2_tail)]
    p_value_theory = stats.ttest_ind(control, treatment, equal_var=False)[1] / 2  # Results are 2 tailed by default

    print()
    print(f'Exact p  = {p_value_1:.5}')
    print(f'Theory p = {p_value_theory:.5}')

    if treatment_effect_size < 3:
        assert p_value_1 > 0.05
        assert p_value_2 > 0.1
    else:
        assert p_value_1 < 0.05
        assert p_value_2 < 0.1
