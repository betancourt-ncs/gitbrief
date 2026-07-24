import hmac
import hashlib


# HMAC signature verification

def verify_signature(payload_body: bytes, secret_key: str, github_signature: str):
    # Converting secret key into bytes
    key_bytes = secret_key.encode("utf-8")

    # Computing HMAC using SHA256
    computed_hmac = "sha256=" + \
        hmac.new(key_bytes, payload_body, hashlib.sha256).hexdigest()

    # Comparing digests to mitigate timing attacks
    result = hmac.compare_digest(computed_hmac, github_signature)

    return result


# Test
if __name__ == "__main__":
    import secrets
    fake_body = b' {"test": "data"}'
    fake_secret = secrets.token_hex(32)
    fake_secret_bytes = fake_secret.encode("utf-8")
    test_hmac = "sha256=" + \
        hmac.new(fake_secret_bytes, fake_body, hashlib.sha256).hexdigest()

    # Correct signature
    result = verify_signature(fake_body, fake_secret, test_hmac)
    print("Correct signature test:", result)

    # Incorrect signature
    incorrect_result = verify_signature(
        fake_body, fake_secret, test_hmac + "monkey")
    print("Incorrect signature test:", incorrect_result)
