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
