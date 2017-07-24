from .shell import Shell
from .execute import Execute

def shell_commands(parser):
    parser.set_defaults(func=Shell())


def exec_commands(parser):
    parser.set_defaults(func=Execute())
    parser.add_argument("command", nargs="+")


def register(parser):
    subparsers = parser.add_subparsers(title="Commands", metavar='')
    shell_commands(subparsers.add_parser("shell", help="Connect to Cisco Shell"))
    exec_commands(subparsers.add_parser("exec", help="Run command"))
