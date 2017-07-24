from .shell import Shell
from .backup import Backup


def backup_commands(parser):
    parser.set_defaults(func=Backup())
    parser.add_argument("-n", "--name", type=str, required=False, help="Device Names")


def shell_commands(parser):
    parser.set_defaults(func=Shell())
    parser.add_argument("-n", "--name", type=str, required=True, help="Device Name")


def register(parser):
    subparsers = parser.add_subparsers(title="Commands", metavar='')
    backup_commands(subparsers.add_parser("backup", help="Backup Cisco Devices configuration"))
    shell_commands(subparsers.add_parser("shell", help="Connect to Cisco Shell"))
