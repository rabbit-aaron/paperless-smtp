import os
import logging
import sys

try:
    PAPERLESS_USERNAME = os.environ["PAPERLESS_USERNAME"]
    PAPERLESS_PASSWORD = os.environ["PAPERLESS_PASSWORD"]
    PAPERLESS_URL = os.environ["PAPERLESS_URL"]
    EMAIL_DOMAIN = os.environ["EMAIL_DOMAIN"]
except KeyError as e:
    sys.stderr.write(
        """Failed to initialize configuration from environment variables, these are the required variables:
PAPERLESS_USERNAME: Your Paperless-ngx username
PAPERLESS_PASSWORD: Your Paperless-ngx password
PAPERLESS_URL: The URL where Paperless-ngx is hosted, include http:// or https:// at the beginning
EMAIL_DOMAIN: Email domain to be processed, email that did not match with the domain will not be processed

These are the optional variables:
SMTP_HOST: The host for SMTP server to bind to, the default is "0.0.0.0"
SMTP_PORT: The port for SMTP server to bind to, the default is "25"
LOG_LEVEL: Logging level for the application, the default is "INFO"
"""
    )
    raise SystemExit from e

SMTP_HOST = os.environ.get("SMTP_HOST", "0.0.0.0")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "25"))
LOG_LEVEL = getattr(logging, os.environ.get("LOG_LEVEL", "INFO"))
