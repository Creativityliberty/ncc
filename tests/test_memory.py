from ncc.memory import exponential_kernel, hybrid_kernel, power_kernel


def test_kernels_decrease():
    assert exponential_kernel(0) > exponential_kernel(10)
    assert power_kernel(0) > power_kernel(10)
    assert hybrid_kernel(0) > hybrid_kernel(10)
