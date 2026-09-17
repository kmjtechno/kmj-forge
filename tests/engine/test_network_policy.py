import pytest

from kmj_forge.engine.network_policy import NetworkPolicy


def test_network_is_denied_by_default():
    policy = NetworkPolicy()
    assert policy.allows("https", "api.example.com", 443) is False


def test_allowlisted_destination_requires_explicit_approval():
    with pytest.raises(ValueError, match="explicit approval"):
        NetworkPolicy(allowed_hosts=("api.example.com",))


def test_approved_allowlist_is_exact_and_https_only_by_default():
    policy = NetworkPolicy(explicit_approval=True, allowed_hosts=("api.example.com",))
    assert policy.allows("https", "api.example.com", 443) is True
    assert policy.allows("http", "api.example.com", 80) is False
    assert policy.allows("https", "evil.example.com", 443) is False
    assert policy.allows("https", "api.example.com.evil.test", 443) is False


def test_local_and_metadata_targets_fail_closed_even_if_allowlisted():
    policy = NetworkPolicy(
        explicit_approval=True,
        allowed_hosts=("localhost", "127.0.0.1", "169.254.169.254"),
    )
    assert policy.allows("https", "localhost", 443) is False
    assert policy.allows("https", "127.0.0.1", 443) is False
    assert policy.allows("https", "169.254.169.254", 443) is False


def test_invalid_host_entries_are_rejected():
    with pytest.raises(ValueError, match="host"):
        NetworkPolicy(explicit_approval=True, allowed_hosts=("https://api.example.com/path",))
