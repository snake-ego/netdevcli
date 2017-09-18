from enum import Enum
from logging import getLogger

from . import telnet
from ..config import search_name, load_device_settings

__all__ = ['Shell']


class Shell(object):
    logger = getLogger('ciscocli:shell')

    protocols = Enum('ConnectThrough', {
        'telnet': lambda inst, **kwargs: inst.enter_through_telnet(**kwargs),
        'ssh': lambda inst, **kwargs: inst.enter_through_ssh(**kwargs)
    })

    def __call__(self, config, args):
        name = search_name(config, args.name)
        address = args.name if name is None else None
        return self.enter_shell(name, config, address)

    def enter_shell(self, name, config, address=None):
        ctx = load_device_settings(config, name)

        if not hasattr(self.protocols, ctx.get('protocol')):
            raise ValueError("Bad protocol name: '{}'".format(ctx.get('protocol')))

        fn = getattr(self.protocols, ctx.pop('protocol'))
        ctx.update({'address': address}) if 'address' not in ctx else None
        fn(self, name=name, **ctx)

    def enter_through_telnet(self, address, name, user, password, **ctx):
        runner = telnet.connect(address, user, password)
        telnet.set_admin_mode(runner, password)
        telnet.enter_interactive_session(runner)
        telnet.disconnect(runner)

    def enter_through_ssh(self, address, name, user, password, **ctx):
        raise NotImplementedError
