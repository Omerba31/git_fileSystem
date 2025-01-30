import argparse
import sys
from libcaf.constants import DEFAULT_REPO_DIR

import caf.cli_commands as cli_commands

_repo_args = {
    'working_dir_path': {
        'type': str,
        'help': 'path to the working directory of the repository',
        'default': '.'
    },
    'repo_dir': {
        'type': str,
        'help': 'name of the repository directory',
        'default': str(DEFAULT_REPO_DIR)
    }
}

def cli():
    parser = argparse.ArgumentParser(description="CAF Command Line Interface")
    commands_sub = parser.add_subparsers(title='command', dest='command',
                                         help='available commands')

    # Dictionary to map command names to their functions and descriptions
    commands = {
        'init': {
            'func': cli_commands.init,
            'args': {
                **_repo_args,
                'default_branch': {
                    'type': str,
                    'help': 'name of the default branch (default: "main")',
                    'default': 'main'
                }
            },
            'help': 'initialize a new CAF repository'
        },

        'delete_repo': {
            'func': cli_commands.delete_repo,
            'args': {
                **_repo_args
            },
            'help': 'delete the repository'
        },

        'commit': {
            'func': cli_commands.commit,
            'args': {
                **_repo_args,
                'author': {
                    'type': str,
                    'help': 'Name of the commit author'
                },
                'message': {
                    'type': str,
                    'help': 'Commit message'
                }
            },
            'help': 'Create a new commit'
        },

        'hash_file': {
            'func': cli_commands.hash_file,
            'args': {
                'path': {
                    'type': str,
                    'help': 'path of the file to hash'
                },
                **_repo_args,
                'write': {
                    'type': None,
                    'help': 'save the file to the repository',
                    'default': False,
                    'flag': True,
                    'short_flag': 'w'
                }
            },
            'help': 'print the hash of the file and optionally save it to the repository'
        },

        'add_branch': {
            'func': cli_commands.add_branch,
            'args': {
                **_repo_args,
                'branch_name': {
                    'type': str,
                    'help': 'Name of the branch to add'
                }
            },
            'help': 'Add a new branch'
        },

        'delete_branch': {
            'func': cli_commands.delete_branch,
            'args': {
                **_repo_args,
                'branch_name': {
                    'type': str,
                    'help': 'Name of the branch to remove'
                }
            },
            'help': 'Remove an existing branch'
        },

        'branch_exists': {
            'func': cli_commands.branch_exists,
            'args': {
                **_repo_args,
                'branch_name': {
                    'type': str,
                    'help': 'Name of the branch to check'
                }
            },
            'help': 'Check if a branch exists'
        },

        'branch': {
            'func': cli_commands.branch,
            'args': {
                **_repo_args
            },
            'help': 'List all branches'
        }
    }

    # Register commands
    for command_name, command_info in commands.items():
        command_sub = commands_sub.add_parser(command_name, help=command_info['help'])
        for arg_name, arg_info in command_info['args'].items():
            arg_type = arg_info['type']
            arg_help = arg_info['help']
            arg_default = arg_info.get('default')
            arg_flag = arg_info.get('flag', False)

            if arg_flag:
                arg_short_flag = arg_info['short_flag']
                command_sub.add_argument(f'-{arg_short_flag}', f'--{arg_name}', help=arg_help, action='store_true',
                                         default=arg_default)
            elif arg_default is not None:
                command_sub.add_argument(f'--{arg_name}', type=arg_type, help=f'{arg_help} (default: %(default)s)',
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
