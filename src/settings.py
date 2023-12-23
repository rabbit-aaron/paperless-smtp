import os
import logging

PAPERLESS_USERNAME = os.environ["PAPERLESS_USERNAME"]
PAPERLESS_PASSWORD = os.environ["PAPERLESS_PASSWORD"]
PAPERLESS_URL = os.environ["PAPERLESS_URL"]
SMTP_HOST = os.environ["SMTP_HOST"]
SMTP_PORT = int(os.environ["SMTP_PORT"])
LOG_LEVEL = getattr(logging, os.environ.get("LOG_LEVEL", "INFO"))
