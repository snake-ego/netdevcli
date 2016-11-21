import yaml
import os
from os import path as op
from inspect import ismethod

DEFAULT_CONFIG = "../data/configuration.yaml"


class ConfigYAML(object):

    def __new__(cls, config=None, uppercase=None, section=None):
        config = cls.find_config(config)
        uppercase = uppercase if isinstance(uppercase, bool) else False

        properties = {
            '_baseclass': property(lambda self: cls),
            'section': property(lambda self: section),
            'uppercase': property(lambda self: uppercase),
            'config': property(lambda self: config)
        }
        properties.update({'_exclude_attr': property(lambda self: tuple(properties.keys()))})
        Config = type("Config", (cls, ), properties)
        obj = super(cls, Config).__new__(Config)
        obj.reload()
        return obj

    @staticmethod
    def find_config(config=None):
        config = config if isinstance(config, str) else DEFAULT_CONFIG
        rules = (
            '{0}',
            '/etc/{0}/config.yaml',
            '{HOME}/.config/{0}.yaml',
            '../data/{0}.yaml',
            '{0}.yaml'
        )

        for rule in rules:
            configpath = rule.format(config, **os.environ)
            if op.exists(configpath):
                return configpath

        for rule in rules:
            configpath = rule.format(DEFAULT_CONFIG, **os.environ)
            if op.exists(configpath):
                return configpath

        return configpath

    def reload(self):
        if self.config.find('\n') == -1:
            with open(self.config, 'r') as f:
                cfg = yaml.load(f)
        else:
            cfg = yaml.load(self.config)

        if self.section is not None:
            for subsection in self.section.split('.'):
                cfg = cfg.get(subsection, dict())

            if not cfg:
                raise ConfigError("Can't find section '{}' in file".format(self.section))

        if isinstance(cfg, dict):
            [setattr(self, self.case(k), v) for k, v in cfg.items()]

    def get(self, key, default=None):
        return getattr(self, self.case(key), default)

    def getall(self, prefix=None):
        return {item: getattr(self, item) for item in dir(self) if self._is_allowed(item, prefix)}

    def _is_allowed(self, item, allow_prefix=None):
        allow_prefix = '' if allow_prefix is None else allow_prefix

        if ismethod(getattr(self, item)):
            return False

        if item in self._exclude_attr:
            return False

        if item.find('_', 0) == 0:
            return False

        if self.case(allow_prefix) == item:
            return True

        if item.find(self.case(allow_prefix), 0) == 0:
            return True

        return False

    def case(self, key):
        if self.uppercase:
            return key.upper()
        else:
            return key

    def extract(self, section):
        if not isinstance(section, str):
            return self

        if self.section is not None:
            section = ".".join([self.section, section])

        return self._baseclass(section=section, config=self.config, uppercase=self.uppercase)


class ConfigError(Exception):
    pass


def first(items):
    return (lambda x: len(x) > 0 and x[0] or None)(items)


def search_name(config, name):
    if name in config.devices:
        return name

    for key, item in config.devices.items():
        if name in item.get('alias', list()) or name == item.get('address'):
            return key

    return None


def load_device_settings(config, name):
    out = config.defaults.copy()
    out.update(config.devices.get(name, dict()))
    out.pop('alias', None)
    return out
