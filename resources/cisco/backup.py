from enum import Enum
from logging import getLogger

from . import telnet
from ..config import search_name, load_device_settings

__all__ = ['Backup']


class Backup(object):
    logger = getLogger('ciscocli:backup')

    protocols = Enum('ConnectThrough', {
        'telnet': lambda inst, **kwargs: inst.backup_through_telnet(**kwargs),
        'ssh': lambda inst, **kwargs: inst.backup_through_ssh(**kwargs)
    })

    def __call__(self, config, args):
        if args.name is not None:
            names = args.name.split(',')
        else:
            names = config.devices.keys()

        for raw_name in names:
            name = search_name(config, raw_name)
            if name is None:
                self.logger.warning("Name '{}' not in config. Skip.".format(raw_name))
                continue

            self.backup_device(name, config)

    def backup_device(self, name, config):
        self.logger.info(">>> Start Backup '{}' <<<".format(name))
        ctx = load_device_settings(config, name)

        target = config.backup.get('address')
        target = target[:-1] if target[-1] == "/" else target

        if not hasattr(self.protocols, ctx.get('protocol')):
            raise ValueError("Bad protocol name: '{}'".format(ctx.get('protocol')))

        fn = getattr(self.protocols, ctx.pop('protocol'))
        fn(self, name=name, target=target, **ctx)

    def backup_through_telnet(self, address, name, user, password, target):
        runner = telnet.connect(address, user, password)
        telnet.set_admin_mode(runner, password)
        telnet.copy_config(runner, "/".join([target, str(name)]))
        telnet.save_running_configuration(runner)
        telnet.disconnect(runner)

    def backup_through_ssh(self, address, name, user, password, target):
        raise NotImplementedError
