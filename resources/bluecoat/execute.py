from enum import Enum
from logging import getLogger

from . import ssh
from ..config import load_device_settings

__all__ = ['Execute']


class Execute(object):
    name = "bluecoat"
    logger = getLogger('bluecoat:exec')

    protocols = Enum('ConnectThrough', {
        'telnet': lambda inst, *args, **kwargs: inst.enter_through_telnet(*args, **kwargs),
        'ssh': lambda inst, *args, **kwargs: inst.enter_through_ssh(*args, **kwargs)
    })

    def __call__(self, config, args):
        return self.run_command(config, " ".join(args.command))

    def run_command(self, config, command, address=None):
        ctx = load_device_settings(config, self.name)

        if not hasattr(self.protocols, ctx.get('protocol')):
            raise ValueError("Bad protocol name: '{}'".format(ctx.get('protocol')))

        fn = getattr(self.protocols, ctx.pop('protocol'))
        ctx.update({'address': address}) if 'address' not in ctx else None
        fn(self, command=command, **ctx)

    def enter_through_ssh(self, command, address, user, password, admin_password=None):
        admin_password = admin_password if isinstance(admin_password, str) else password

        runner = ssh.connect(address, user, password)
        ssh.set_admin_mode(runner, admin_password)
        ssh.run_command(runner, command)
        ssh.disconnect(runner)

    def enter_through_telnet(self, *args, **kwargs):
        raise NotImplementedError
