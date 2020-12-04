import click

from code42cli.options import sdk_options

command_argument = click.argument("cmd")

@click.command("exec")
@sdk_options(hidden=True)
@command_argument
def _exec(state, cmd):
    """Execute arbitrary py42 code. Create a script using `sdk` 
    as the py42 sdk to use your CLI connections in scripts easier.
    
    For example, in script.py:
    
        users_gen = sdk.users.get_all()
        for page in users_gen:
	        print(page)
    
    Then, using the CLI:
    
        code42 exec "$(cat script.py)"

    """
    
    # Assume sdk var used during exec()
    sdk = state.sdk
    exec(cmd)
