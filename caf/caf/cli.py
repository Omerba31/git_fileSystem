import argparse
import sys

import caf.cli_commands as cli_commands


def cli():
    parser = argparse.ArgumentParser(description="CAF Command Line Interface")
    commands_sub = parser.add_subparsers(title='command', dest='command',
                                         help='available commands')

    # Dictionary to map command names to their functions and descriptions
    commands = {
        'init': {
            'func': cli_commands.init,
            'args': {
                'working_dir_path': {
                    'type': str,
                    'help': 'path to the working directory of the repository',
                    'default': '.'
                },
                'repo_path': {
                    'type': str,
                    'help': 'name of the repository directory',
                    'default': '.caf'
                }
            },
            'help': 'initialize a new CAF repository'
        },
    }

    # # Register commands
    for command_name, command_info in commands.items():
        command_sub = commands_sub.add_parser(command_name, help=command_info['help'])
        for arg_name, arg_info in command_info['args'].items():
            arg_type = arg_info['type']
            arg_help = arg_info['help']
            arg_default = arg_info['default']

            if arg_default:
                command_sub.add_argument(f'--{arg_name}', type=arg_type,
                                         help=f'{arg_help} (default: %(default)s)',
                                         default=arg_default)
            else:
                command_sub.add_argument(arg_name, type=arg_type, help=arg_help)

    command_args = parser.parse_args()
    if command_args.command is None:
        parser.print_help()
    else:
        # Call the function associated with the command and exit with its return code
        command_info = commands[command_args.command]
        command_func = command_info['func']

        code = command_func(**command_args.__dict__)
        sys.exit(code)

    if __name__ == "__main__":
        cli()
