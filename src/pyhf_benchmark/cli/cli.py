import logging
import click

from ..version import __version__
from .. import run

logging.basicConfig()
log = logging.getLogger(__name__)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version=__version__)
def pyhf_benchmark():
    pass


pyhf_benchmark.add_command(run.run)
