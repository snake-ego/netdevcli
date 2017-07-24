import pexpect
from enum import Enum
from logging import getLogger

PROMPTS = Enum('DeviceModePrompt', {
    'standart': ".*>",
    'admin': ".*#"
})

logger = getLogger('ciscocli:ssh')


def connect(address, user=None, password=None):
    if user is not None:
        cli = pexpect.spawn('ssh {}@{}'.format(user, address))
    else:
        cli = pexpect.spawn('ssh {}'.format(user, address))

    if password is not None:
        cli.expect('.* password:')
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


def enter_interactive_session(cli):
    cli.sendline("")
    try:
        cli.interact()
    except (KeyboardInterrupt, SystemExit):
        return cli


def run_command(cli, command):
    cli.sendline("")
    cli.expect([PROMPTS.standart.value, PROMPTS.admin.value])
    cli.sendline(command)
    return cli


def disconnect(cli):
    logger.info('Close connection')
    cli.sendline("exit")
    cli.close()
