import asyncio
import logging
from email.message import MIMEPart, EmailMessage
from email.parser import Parser
from email.policy import SMTPUTF8
from typing import Generator, cast

from aiosmtpd.smtp import SMTP, Session, Envelope

import settings
from paperless_client import PaperlessClient

logger = logging.getLogger("paperless_smtp")
parser = Parser(_class=EmailMessage, policy=SMTPUTF8)


def _mail_attachments(message: EmailMessage) -> Generator[MIMEPart, None, None]:
    return (part for part in message.walk() if part.is_attachment())


class PaperlessHandler:
    def __init__(self):
        self.tag_mappings = {}

    async def refresh_tag_mappings(self) -> None:
        async with PaperlessClient() as client:
            response = await client.list_tags(params={"page_size": 10000})
            if response.status_code != 200:
                logger.error(
                    "Something went wrong while trying to fetch tags from Paperless-ngx, status code %r, reason: %r",
                    response.status_code,
                    response.text,
                )
                raise SystemExit
            results = response.json()["results"]
            logger.info("Refreshing tag mappings from Paperless-ngx")
            self.tag_mappings = {i["slug"]: str(i["id"]) for i in results}
            logger.info("Tag mappings updated, %r", self.tag_mappings)

    async def create_tag(self, name: str) -> dict:
        async with PaperlessClient() as client:
            logger.info("Creating tag %r", name)
            response = await client.create_tag(
                json={"name": name, "slug": name, "matching_algorithm": 0}
            )
            if response.status_code != 201:
                logger.error(
                    "Error creating tag %r, response code %r, reason: %r",
                    name,
                    response.status_code,
                    response.text,
                )
            return response.json()

    async def handle_DATA(self, server: SMTP, session: Session, envelope: Envelope):
        message = cast(EmailMessage, parser.parsestr(envelope.content.decode("utf-8")))
        logger.info("Message incoming, rcpt_tos: %r", envelope.rcpt_tos)
        await self.send_message_to_paperless(message, envelope.rcpt_tos)
        return "250 Message accepted for delivery"

    def rcpt_to_tags(self, rcpt_tos: list[str]) -> Generator[str, None, None]:
        suffix = f"@{settings.EMAIL_DOMAIN}"
        for rcpt in rcpt_tos:
            if not rcpt.endswith(suffix):
                logger.warning("%r email domain mismatch, ignored", rcpt)
                continue

            tags_dotted = rcpt.removesuffix(suffix)
            for tag in tags_dotted.split("."):
                yield tag

    async def send_file_to_paperless(self, file: MIMEPart, rcpt_tos: list[str]):
        content_bytes = file.get_content()
        file_name = file.get_filename()
        content_type = file.get_content_type()

        if not self.tag_mappings:
            await self.refresh_tag_mappings()

        tags = list(self.rcpt_to_tags(rcpt_tos))
        tag_creation_tasks = [
            self.create_tag(tag) for tag in tags if tag not in self.tag_mappings
        ]

        if tag_creation_tasks:
            await asyncio.gather(*tag_creation_tasks)
            await self.refresh_tag_mappings()

        tag_pks = list(set(self.tag_mappings[tag] for tag in tags if tag in self.tag_mappings))

        async with PaperlessClient() as client:
            logger.info(
                "Sending file to paperless for processing: %r, tags: %r",
                file_name,
                tag_pks,
            )
            response = await client.create_document(
                data={"tags": tag_pks},
                files={"document": (file_name, content_bytes, content_type)},
            )

            if response.status_code == 200:
                logger.info("Success")
            else:
                logger.error(
                    "Something went wrong attempting to send document to Paperless. Status code [%d], error: %s",
                    response.status_code,
                    response.content,
                )

    async def send_message_to_paperless(
        self, message: EmailMessage, rcpt_tos: list[str]
    ):
        tasks = (
            self.send_file_to_paperless(attachment, rcpt_tos)
            for attachment in _mail_attachments(message)
        )
        await asyncio.gather(*tasks)
