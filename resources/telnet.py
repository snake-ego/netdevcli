import pexpect
from enum import Enum
from logging import getLogger
# from re import compile

PROMPTS = Enum('DeviceModePrompt', {
    'standart': ".*>",
    'admin': ".*#"
})

logger = getLogger('ciscocli:telnet')


def connect(address, user=None, password=None):
    cli = pexpect.spawn('telnet {}'.format(address))
    if user is not None:
        logger.debug('Send username: {}'.format(user))
        cli.sendline(user)
        if password is not None:
            cli.expect('Password:')
            logger.debug('Send password: {}*****{}'.format(password[:2], password[-2:]))
            cli.sendline("{}".format(password))
    logger.info('Connected to: {}'.format(address))
    return cli


def set_admin_mode(cli, password=None):
    mode = cli.expect([PROMPTS.standart.value, PROMPTS.admin.value])
    if mode == 0:
        logger.debug('Enter in admin mode')
        cli.sendline("enable\n")
        if password is not None:
            cli.expect('Password:')
            logger.debug('Send password: {}*****{}'.format(password[:2], password[-2:]))
            cli.sendline("{}".format(password))
        mode = cli.expect([PROMPTS.standart.value, PROMPTS.admin.value])
        if mode == 0:
            cli.close()
            raise ValueError('Admin mode failed')

    return cli


def copy_config(cli, target):
    logger.info('Copy configuration into "{}"'.format(target))
    cli.sendline("copy running {}/running-config\n\n\n".format(target))
    cli.expect(PROMPTS.admin.value)
    cli.sendline("copy startup {}/startup-config\n\n\n".format(target))
    cli.expect(PROMPTS.admin.value)
    return cli


def save_running_configuration(cli):
    logger.info('Save running configuration to flash')
    cli.sendline("write memory\n")
    cli.expect(PROMPTS.admin.value)
    return cli


def enter_interactive_session(cli):
    cli.sendline("")
    try:
        cli.interact()
    except (KeyboardInterrupt, SystemExit):
        return cli


def disconnect(cli):
    logger.info('Close connection')
    cli.sendline("exit")
    cli.close()
