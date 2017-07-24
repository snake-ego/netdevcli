#!/usr/bin/env python3

import argparse
import logging
from logging.config import dictConfig
from os import path as op
from resources import config, cisco, bluecoat

cfg = config.ConfigYAML(op.splitext(op.basename(__file__))[0])

dictConfig(cfg.logging) if cfg.get('logging') else None
logger = logging.getLogger()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='netdev [-h]')
    devices = parser.add_subparsers(title="Devices", metavar='')
    cisco.register(devices.add_parser("cisco", help="Control Cisco devices"))
    bluecoat.register(devices.add_parser("bluecoat", help="Control Bluecoat devices"))

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(cfg, args)
    else:
        parser.print_help()
