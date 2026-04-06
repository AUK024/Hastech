def extract_domain(email: str) -> str:
    return email.split('@')[-1].lower() if '@' in email else ''
