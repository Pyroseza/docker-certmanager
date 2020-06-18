import logging
import logging.config

import click

from pygluu.containerlib import get_manager

from settings import LOGGING_CONFIG
# from settings import SELF_GENERATE
from settings import SERVICE_NAMES
# from settings import SOURCE_TYPES
from oxauth_handler import OxauthHandler
from oxd_handler import OxdHandler
from oxshibboleth_handler import OxshibbolethHandler
from web_handler import WebHandler

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("certman")

# ============
# CLI commands
# ============

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@cli.command()
@click.argument(
    "service",
    type=click.Choice(SERVICE_NAMES),
)
@click.option(
    "--dry-run",
    help="Generate save certs and/or crypto keys only without saving it to external backends.",
    is_flag=True,
)
@click.option(
    "--opts",
    help="Options for targeted service (can be set multiple times).",
    multiple=True,
    metavar="KEY:VALUE",
)
def patch(service, dry_run, opts):
    """Patch cert and/or crypto keys for the targeted service.
    """
    manager = get_manager()

    if dry_run:
        logger.warning("Dry-run mode is enabled!")

    callback_classes = {
        "web": WebHandler,
        "oxshibboleth": OxshibbolethHandler,
        "oxauth": OxauthHandler,
        "oxd": OxdHandler,
    }

    logger.info(f"Processing updates for service {service}")

    _opts = {}
    for opt in opts:
        try:
            k, v = opt.split(":", 1)
            _opts[k] = v
        except ValueError:
            k = opt
            v = ""

    callback_cls = callback_classes[service]
    callback_cls(manager, dry_run, **_opts).patch()


if __name__ == "__main__":
    cli(prog_name="certman")
