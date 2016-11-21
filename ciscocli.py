#!/usr/bin/env python3
import argparse
import logging
from logging.config import dictConfig
from os import path as op
from resources import config, backup, shell

cfg = config.ConfigYAML(op.splitext(op.basename(__file__))[0])

dictConfig(cfg.logging) if cfg.get('logging') else None
logger = logging.getLogger()


def backup_commands(parser):
    parser.set_defaults(func=backup.backup)
    parser.add_argument("--name", type=str, required=False, help="Device Names")


def shell_commands(parser):
    parser.set_defaults(func=shell.shell)
    parser.add_argument("-n", "--name", type=str, required=True, help="Device Name")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='ciscocli [-h]')
    subparsers = parser.add_subparsers(title="Commands", metavar='')

    backup_commands(subparsers.add_parser("backup", help="Backup Cisco Devices configuration"))
    shell_commands(subparsers.add_parser("shell", help="Connect to Cisco Shell"))

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(cfg, args)
    else:
        parser.print_help()
