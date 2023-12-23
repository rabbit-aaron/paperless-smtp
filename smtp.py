import asyncio
import logging
from email.message import MIMEPart, EmailMessage
from email.parser import Parser
from email.policy import SMTPUTF8
from typing import Generator, cast

from aiosmtpd.smtp import SMTP, Session, Envelope

from paperless_client import PaperlessClient

logger = logging.getLogger("paperless_smtp")
parser = Parser(_class=EmailMessage, policy=SMTPUTF8)


def _mail_attachments(message: EmailMessage) -> Generator[MIMEPart, None, None]:
    for part in message.walk():
        if part.is_attachment():
            yield part


class PaperlessHandler:
    def __init__(self, tag_mappings: dict):
        self.tag_mappings = tag_mappings

    async def handle_DATA(self, server: SMTP, session: Session, envelope: Envelope):
        message = cast(EmailMessage, parser.parsestr(envelope.content.decode("utf-8")))
        logger.info("Message incoming, rcpt_tos: %r", envelope.rcpt_tos)
        await self.send_message_to_paperless(message, envelope.rcpt_tos)
        return "250 Message accepted for delivery"

    def rcpt_to_tag_pks(self, rcpt_tos: list[str]) -> Generator[str, None, None]:
        for rcpt in rcpt_tos:
            tags_dotted = rcpt.removesuffix("@local")
            for tag in tags_dotted.split("."):
                try:
                    yield self.tag_mappings[tag]
                except KeyError:
                    pass

    async def send_file_to_paperless(self, file: MIMEPart, rcpt_tos: list[str]):
        content_bytes = file.get_content()
        file_name = file.get_filename()
        content_type = file.get_content_type()

        tag_pks = list(set(self.rcpt_to_tag_pks(rcpt_tos)))

        async with PaperlessClient() as client:
            logger.info("Sending file to paperless for processing: %r, tags: %r", file_name, tag_pks)
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
