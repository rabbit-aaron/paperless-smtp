import asyncio
import base64
from email.message import MIMEPart, EmailMessage
from email.parser import Parser
from email.policy import SMTPUTF8
from typing import Generator, cast

import httpx
from aiosmtpd.smtp import SMTP, Session, Envelope

import settings

parser = Parser(_class=EmailMessage, policy=SMTPUTF8)


def mail_attachments(message: EmailMessage) -> Generator[MIMEPart, None, None]:
    for part in message.walk():
        if part.is_attachment():
            yield part


async def send_file_to_paperless(file: MIMEPart):
    content_bytes = file.get_content()
    file_name = file.get_filename()
    content_type = file.get_content_type()
    async with httpx.AsyncClient() as client:
        basic_header = base64.b64encode(f"{settings.PAPERLESS_USERNAME}:{settings.PAPERLESS_PASSWORD}")
        response = await client.post(
            f"{settings.PAPERLESS_URL}/api/documents/post_document/",
            headers={"Authorization": f"Basic {basic_header}"},
            files={"document": (file_name, content_bytes, content_type)}
        )
        print(response.status_code)
        print(response.json())


async def send_to_paperless(message: EmailMessage):
    tasks = (send_file_to_paperless(attachment) for attachment in mail_attachments(message))
    await asyncio.gather(*tasks)


class SMTPHandler:
    async def handle_DATA(self, server: SMTP, session: Session, envelope: Envelope):
        message = cast(EmailMessage, parser.parsestr(envelope.content))
        await send_to_paperless(message)
        return "250 Message accepted for delivery"
