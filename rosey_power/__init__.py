import numpy as np
import pandas as pd
from tqdm import tqdm


__version__ = '0.20201211'


#######################################################################################################################
# Score Functions
#######################################################################################################################
def _make_test_two_tailed(score, two_tail):
    return abs(score) if two_tail else score


def difference_in_means(group_treatment: np.ndarray, group_control: np.ndarray, two_tail=False):
    return _make_test_two_tailed(
        group_treatment.mean() - group_control.mean(),
        two_tail
    )


def difference_in_var(group_treatment: np.ndarray, group_control: np.ndarray, two_tail=False):
    return _make_test_two_tailed(
        group_treatment.std() - group_control.std(),
        two_tail
    )


#######################################################################################################################
# Power Analysis
#######################################################################################################################
class PowerAnalysis:
    def __init__(self, group_treatment: np.ndarray, group_control: np.ndarray, lift_sweep=None):
        self.group_treatment = group_treatment
        self.group_control = group_control

        if lift_sweep is None:
            lift_sweep = np.linspace(0.01, 1.0)
        self.lift_sweep = lift_sweep

        self.results = None
        self._null_dists = []
        self._alt_dists = []

    def run(self, func=difference_in_means, alpha=0.05, n_iter=1000, verbose=False):
        """
        `func` must be some function that can be used to compare Group A & Group B that also returns a number

        :param func: callable(group_treatment, group_control) -> float
        :param alpha:
        :param n_iter:
        :param verbose:
        :return:
        """
        power_given_lift = []
        self._null_dists = []
        self._alt_dists = []
        progressor = tqdm(self.lift_sweep) if verbose else self.lift_sweep
        # TODO (10-Dec-20) technically, since the only that changes on the parameter sweep is the treatment shift then a lot of this duplication is not necessary
        # TODO (10-Dec-20) therefore, it is probably best to swap the inner and outer loops
        for lift_i in progressor:
            null_dist, alt_dist = [], []
            group_pooled = np.hstack([self.group_treatment, self.group_control])
            group_control = self.group_control.copy()
            for j in range(n_iter):
                group_treatment = self.group_treatment.copy() * (1+lift_i)

                # Permute for null distribution
                shuffled_indices = np.random.choice(
                    np.arange(group_pooled.shape[0]),
                    group_pooled.shape[0],
                    replace=False
                )
                null_treatment = group_pooled[shuffled_indices[:len(group_treatment)]]
                null_control = group_pooled[shuffled_indices[len(group_control):]]
                null_dist.append(func(null_treatment, null_control))

                # Resample for alternate distribution
                resampled_indicies_a = np.random.choice(
                    np.arange(len(group_treatment)),
                    len(group_treatment),
                    replace=True
                )
                resampled_indicies_b = np.random.choice(
                    np.arange(len(group_control)),
                    len(group_control),
                    replace=True
                )
                alt_treatment = group_treatment[resampled_indicies_a]
                alt_control = group_control[resampled_indicies_b]
                alt_dist.append(func(alt_treatment, alt_control))

            # Compute all important relevant stats
            null_dist = np.array(null_dist)
            alt_dist = np.array(alt_dist)
            critical_value = np.percentile(null_dist, 100 - alpha * 100)
            power = 1 - (alt_dist <= critical_value).mean()

            # Save info
            power_given_lift.append(power)
            self._null_dists.append(null_dist)
            self._alt_dists.append(alt_dist)

        # Finally check power given lift
        power_given_lift = np.array(power_given_lift)
        self.results = pd.DataFrame(power_given_lift, columns=['power'])
        self.results['lift'] = self.lift_sweep
