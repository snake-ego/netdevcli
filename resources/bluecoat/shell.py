from enum import Enum
from logging import getLogger

from . import ssh
from ..config import load_device_settings

__all__ = ['Shell']


class Shell(object):
    name = "bluecoat"
    logger = getLogger('ciscocli:shell')

    protocols = Enum('ConnectThrough', {
        'telnet': lambda inst, **kwargs: inst.enter_through_telnet(**kwargs),
        'ssh': lambda inst, **kwargs: inst.enter_through_ssh(**kwargs)
    })

    def __call__(self, config, args):
        return self.enter_shell(config)

    def enter_shell(self, config, address=None):
        ctx = load_device_settings(config, self.name)

        if not hasattr(self.protocols, ctx.get('protocol')):
            raise ValueError("Bad protocol name: '{}'".format(ctx.get('protocol')))

        fn = getattr(self.protocols, ctx.pop('protocol'))
        ctx.update({'address': address}) if 'address' not in ctx else None
        fn(self, **ctx)

    def enter_through_ssh(self, address, user, password, admin_password=None, **ctx):
        admin_password = admin_password if isinstance(admin_password, str) else password

        runner = ssh.connect(address, user, password)
        ssh.set_admin_mode(runner, admin_password)
        ssh.enter_interactive_session(runner)
        ssh.disconnect(runner)

    def enter_through_telnet(self, *args, **kwargs):
        raise NotImplementedError
