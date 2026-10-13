from auth import verify_signature

payload_body = b"Hello, World!"
secret_key = "It's a Secret to Everybody"
github_signature = "sha256=757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8b043e17"


def test_valid_signature_returns_true():
    result = verify_signature(payload_body, secret_key, github_signature)
    assert result is True


def test_tampered_body_returns_false():
    tampered_body = b"Goodbye, World!"
    result = verify_signature(tampered_body, secret_key, github_signature)
    assert result is False


def test_tampered_signature_returns_false():
    tampered_signature = "sha256=757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8b043e18"
    result = verify_signature(payload_body, secret_key, tampered_signature)
    assert result is False


def test_wrong_secret_returns_false():
    wrong_secret = "it's a secret to everybody"
    result = verify_signature(payload_body, wrong_secret, github_signature)
    assert result is False
