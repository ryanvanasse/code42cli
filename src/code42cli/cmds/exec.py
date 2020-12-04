import click

from code42cli.options import sdk_options

command_argument = click.argument("cmd")

@click.command("exec")
@sdk_options(hidden=True)
@command_argument
def _exec(state, cmd):
    """Execute arbitrary py42 code."""

    sdk = state.sdk
    # Assume used below
    exec(cmd)
