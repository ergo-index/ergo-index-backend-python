import re


def clean_email(email_address: str) -> str:
    """
    Standardizes input given for an email address field.
    """
    return re.sub('([^[A-z0-9.@]]*|\^)', '', email_address).strip().lower()
