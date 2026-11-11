from auth import verify_signature

PAYLOAD_BODY = b"Hello, World!"
SECRET_KEY = "It's a Secret to Everybody"
GITHUB_SIGNATURE = "sha256=757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8b043e17"


def test_valid_signature_returns_true():
    result = verify_signature(PAYLOAD_BODY, SECRET_KEY, GITHUB_SIGNATURE)
    assert result is True


def test_tampered_body_returns_false():
    tampered_body = b"Goodbye, World!"
    result = verify_signature(tampered_body, SECRET_KEY, GITHUB_SIGNATURE)
    assert result is False


def test_tampered_signature_returns_false():
    tampered_signature = "sha256=757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8b043e18"
    result = verify_signature(PAYLOAD_BODY, SECRET_KEY, tampered_signature)
    assert result is False


def test_wrong_secret_returns_false():
    wrong_secret = "it's a secret to everybody"
    result = verify_signature(PAYLOAD_BODY, wrong_secret, GITHUB_SIGNATURE)
    assert result is False
