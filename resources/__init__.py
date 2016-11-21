#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
from os import path as op
from subprocess import PIPE, Popen
from logging import getLogger
from time import sleep


class Lock(object):
    def __init__(self, lock):
        self.lock = lock

    def get(self):
        if op.exists(self.lock):
            return False

        open(self.lock, 'a').close()
        return True

    def release(self):
        os.remove(self.lock)


class Runner(object):

    def __init__(self, shell=None, logger=None):
        self.shell = shell if shell is not None else os.environ['SHELL']
        self.logger = logger if logger is not None else getLogger(self.__class__.__name__)

    def execute(self, command):
        self.logger.debug(u"Command: {0} {1}".format(self.shell, command))
        return Popen([command], stdout=PIPE, stderr=PIPE, shell=True, executable=self.shell)

    def run(self, command, silent=None):
        proc = self.execute(command)
        proc.wait()
        if silent:
            return self.log_output(proc)

        return Result(proc)

    def call(self, command, timeout, silent=None):
        proc = self.execute(command)
        while timeout > 0:
            sleep(1)
            if proc.poll() is not None:
                break
            timeout -= 1

        if timeout == 0:
            self.stop(proc)

        if silent:
            return self.log_output(proc)

        return Result(proc)

    def stop(self, process):
        if process.poll() is None:
            self.logger.warning("Process is freezing. Force quit start. Terminating.")
            process.terminate()

        sleep(5)
        if process.poll() is None:
            self.logger.warning("Process is terminate failed. Killing")
            process.kill()

        sleep(5)
        if process.poll() is None:
            self.logger.warning("Subprocess killing failed. Use 'kill'")
            self.run('kill -9 {0}'.format(process.pid))

    def log_output(self, process):
        stdout = process.stdout.readlines()
        stderr = process.stderr.readlines()

        self.logger.info("\t".join(stdout)) if stdout else None
        self.logger.error("\t".join(stderr)) if stdout else None


class Result(object):
    def __init__(self, process):
        if not isinstance(process, Popen):
            raise AttributeError('Process must be instance of subprocess.Popen class')

        self.stdout = process.stdout.read()
        self.stderr = process.stderr.read()
        self.exit_code = process.returncode
