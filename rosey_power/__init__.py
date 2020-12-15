import numpy as np
import pandas as pd
from tqdm import tqdm


__version__ = '0.20201215'


#######################################################################################################################
# Score Functions
#######################################################################################################################
def _make_test_two_tailed(func):
    def two_tail_func(group_treatment: np.ndarray, group_control: np.ndarray):
        return abs(func(group_treatment, group_control))
    return two_tail_func


def difference_in_means(group_treatment: np.ndarray, group_control: np.ndarray):
    return group_treatment.mean() - group_control.mean()


def difference_in_var(group_treatment: np.ndarray, group_control: np.ndarray):
    return group_treatment.std() - group_control.std()


#######################################################################################################################
# Power Analysis
#######################################################################################################################
class ExactPowerAnalysis:
    def __init__(
            self,
            treatment: np.ndarray, control: np.ndarray,
            lift_effect_size_sweep=None, absolute_effect_size_sweep=None,
            is_two_tail=False
    ):
        self.group_treatment = treatment
        self.group_control = control
        self.is_two_tail = is_two_tail

        if lift_effect_size_sweep is not None and absolute_effect_size_sweep is not None:
            raise ValueError('Both lift and absolute effect sizes cannot be simultaneously set')
        self.lift_effect_size_sweep = lift_effect_size_sweep
        self.absolute_effect_size_sweep = absolute_effect_size_sweep

        self.results = None
        self._null_dists = []
        self._alt_dists = []

    def run(self, n_iter=1000, alpha=0.05, func=difference_in_means, verbose=False):
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
        func = _make_test_two_tailed(func) if self.is_two_tail else func

        # Select kind of sweep if any
        if self.lift_effect_size_sweep is None and self.absolute_effect_size_sweep is None:
            sweep = [0]
        elif self.lift_effect_size_sweep is not None:
            sweep = self.lift_effect_size_sweep
        elif self.absolute_effect_size_sweep is not None:
            sweep = self.absolute_effect_size_sweep
        else:
            raise ValueError('Check lift_effect_size_sweep and absolute_effect_size_sweep')  # not the great error

        progressor = tqdm(sweep) if verbose else sweep
        # TODO (10-Dec-20) technically, since the only that changes on the parameter sweep is the treatment shift then a lot of this duplication is not necessary
        # TODO (10-Dec-20) therefore, it is probably best to swap the inner and outer loops
        for effect_size in progressor:
            null_dist, alt_dist = [], []
            for j in range(n_iter):
                if self.lift_effect_size_sweep is not None:
                    group_treatment = self.group_treatment.copy() * (1+effect_size)
                else:
                    group_treatment = self.group_treatment.copy() + effect_size
                group_control = self.group_control.copy()
                group_pooled = np.hstack([group_treatment, group_control])

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
        self.results['added_lift' if self.lift_effect_size_sweep is not None else 'added_effect_size'] = sweep
