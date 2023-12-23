import asyncio
import logging
import signal
from contextlib import suppress
from functools import partial

from aiosmtpd.smtp import SMTP
from smtp import SMTPHandler

_verbosity_to_log_level = {
    0: logging.CRITICAL,
    1: logging.ERROR,
    2: logging.WARNING,
    3: logging.INFO,
}


def main(host, port, loglevel=logging.ERROR):
    factory = partial(
        SMTP,
        SMTPHandler(),
    )

    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger("aiosmtpd.log")
    loop = asyncio.new_event_loop()

    logger.setLevel(loglevel)
    logger.debug("Attempting to start server on %s:%s", host, port)

    try:
        server = loop.create_server(factory, host=host, port=port)
        server_loop = loop.run_until_complete(server)
    except RuntimeError:  # pragma: nocover
        raise

    logger.debug(f"server_loop = {server_loop}")
    logger.info("Server is listening on %s:%s", host, port)

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
    main("127.0.0.1", 1025, logging.DEBUG)
