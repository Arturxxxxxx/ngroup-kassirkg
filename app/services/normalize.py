import re

def norm_email(email: str | None) -> str | None:
    if not email:
        return None
    e = email.strip().lower()
    return e or None

def norm_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    digits = re.sub(r"\D+", "", phone)
    return digits or None