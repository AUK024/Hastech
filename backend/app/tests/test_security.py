from app.core.security import hash_password, verify_password


def test_hash_password_round_trip() -> None:
    password = 'StrongPass123!'
    stored_hash = hash_password(password)
    assert stored_hash
    assert verify_password(password, stored_hash) is True


def test_verify_password_rejects_wrong_password() -> None:
    stored_hash = hash_password('StrongPass123!')
    assert verify_password('WrongPass123!', stored_hash) is False
