import hashlib
import hmac
import secrets

PBKDF2_ITERATIONS = 100_000
PBKDF2_DIGEST = 'sha256'


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        PBKDF2_DIGEST,
        password.encode('utf-8'),
        salt.encode('utf-8'),
        PBKDF2_ITERATIONS,
    ).hex()
    return f'pbkdf2_{PBKDF2_DIGEST}${PBKDF2_ITERATIONS}${salt}${digest}'


def verify_password(password: str, stored_hash: str) -> bool:
    if not password or not stored_hash:
        return False

    try:
        algorithm, iterations_raw, salt, expected_digest = stored_hash.split('$', 3)
        if algorithm != f'pbkdf2_{PBKDF2_DIGEST}':
            return False
        iterations = int(iterations_raw)
    except (ValueError, TypeError):
        return False

    candidate_digest = hashlib.pbkdf2_hmac(
        PBKDF2_DIGEST,
        password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations,
    ).hex()
    return hmac.compare_digest(candidate_digest, expected_digest)
