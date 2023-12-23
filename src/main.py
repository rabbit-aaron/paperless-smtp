import asyncio
import logging
import signal
from contextlib import suppress
from functools import partial

from aiosmtpd.smtp import SMTP

import settings
from paperless_client import PaperlessClient
from smtp import PaperlessHandler

logger = logging.getLogger("paperless_smtp")


async def get_tag_mappings():
    async with PaperlessClient() as client:
        response = await client.list_tags(params={"page_size": 10000})
        results = response.json()["results"]
        return {i["slug"]: i["id"] for i in results}


def main():
    tag_mappings = asyncio.run(get_tag_mappings())
    factory = partial(
        SMTP,
        PaperlessHandler(tag_mappings=tag_mappings),
    )

    logging.basicConfig(level=logging.ERROR)
    loop = asyncio.new_event_loop()

    logger.setLevel(settings.LOG_LEVEL)
    logger.debug(
        "Attempting to start server on %s:%s", settings.SMTP_HOST, settings.SMTP_PORT
    )

    server = loop.create_server(
        factory, host=settings.SMTP_HOST, port=settings.SMTP_PORT
    )
    server_loop = loop.run_until_complete(server)

    logger.debug(f"server_loop = {server_loop}")
    logger.info("Server is listening on %s:%s", settings.SMTP_HOST, settings.SMTP_PORT)

    # Signal handlers are only supported on *nix, so just ignore the failure
    # to set this on Windows.
    with suppress(NotImplementedError):
        loop.add_signal_handler(signal.SIGINT, loop.stop)

    logger.debug("Starting asyncio loop")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server_loop.close()
    logger.debug("Completed asyncio loop")
    loop.run_until_complete(server_loop.wait_closed())
    loop.close()


if __name__ == "__main__":
    main()
