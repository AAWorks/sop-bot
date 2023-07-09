import tensorflow as tf
import numpy as np

from utils.parse import Dataset

TRAINING_SET_FRACTION = 0.90


def main(argv):
    raw = Dataset("mls")
    data = raw.aggregate_data(10)
    raw.close_db()

    train_results_len = int(TRAINING_SET_FRACTION * len(data))
    train_results = data[:train_results_len]
    test_results = data[train_results_len:]

