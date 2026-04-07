from app.core.config import Settings


def test_is_admin_email_by_exact_match() -> None:
    settings = Settings(admin_user_emails='admin@hascelik.com,ops@hascelik.com', admin_user_domains='')
    assert settings.is_admin_email('ops@hascelik.com') is True
    assert settings.is_admin_email('user@hascelik.com') is False


def test_is_admin_email_by_domain() -> None:
    settings = Settings(admin_user_emails='', admin_user_domains='hascelik.com')
    assert settings.is_admin_email('admin@hascelik.com') is True
    assert settings.is_admin_email('guest@other.com') is False
