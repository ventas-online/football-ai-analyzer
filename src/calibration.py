import numpy as np


def normalize_1x2(home, draw, away):
    values = np.array([home, draw, away], dtype=float)
    values = np.clip(values, 1e-9, None)
    values /= values.sum()
    return tuple(float(x) for x in values)


def shrink_probability(probability, sample_size, prior=0.5, strength=30):
    """Conservative shrinkage for small samples."""
    weight = sample_size / (sample_size + strength)
    return float(weight * probability + (1 - weight) * prior)
