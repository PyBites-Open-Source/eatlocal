from summing import sum_numbers


def test_sum_numbers_default_args():
    assert sum_numbers() == 5050
    assert sum_numbers(numbers=None) == 5050


def test_sum_numbers_various_inputs():
    assert sum_numbers(range(1, 11)) == 55
    assert sum_numbers([1, 2, 3]) == 6
    assert sum_numbers((1, 2, 3)) == 6
    assert sum_numbers([]) == 0  # !! [] not the same as None