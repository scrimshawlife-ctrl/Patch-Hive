"""generation_seed must fit Postgres signed INTEGER."""

from core.naming import hash_string_to_seed


def test_hash_string_to_seed_signed_31bit():
    for s in ("rack-1-10", "a" * 200, "Hermes catalog place-loop smoke"):
        v = hash_string_to_seed(s)
        assert 0 <= v <= 0x7FFFFFFF
