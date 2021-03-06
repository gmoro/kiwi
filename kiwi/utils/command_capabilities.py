# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of kiwi.
#
# kiwi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi.  If not, see <http://www.gnu.org/licenses/>
#
import re

# project
from kiwi.command import Command
from kiwi.logger import log
from kiwi.exceptions import KiwiCommandCapabilitiesError


class CommandCapabilities(object):
    """
    Performs commands calls and parses the output
    so it can look specific flags on help message, check
    command version, etc.
    """
    @classmethod
    def has_option_in_help(
        self, call, flag, help_flags=['--help'],
        root=None, raise_on_error=True
    ):
        """
        Checks if the given flag is present in the help output
        of the given command.

        :param string call: the command the check
        :param string flag: the flag or substring to find in stdout
        :param list help_flags: a list with the required command arguments.
        :param string root: root directory of the env to validate

        :return: True if the flag is found, False in any other case
        :rtype: boolean
        """
        if root:
            arguments = ['chroot', root, call] + help_flags
        else:
            arguments = [call] + help_flags
        try:
            command = Command.run(arguments)
            for line in command.output.splitlines():
                if flag in line:
                    return True
            for line in command.error.splitlines():
                if flag in line:
                    return True
        except Exception:
            message = 'Could not parse {} output'.format(call)
            if raise_on_error:
                raise KiwiCommandCapabilitiesError(message)
            log.warning(message)
        return False

    @classmethod
    def check_version(
        self, call, version_waterline, version_flags=['--version'],
        root=None, raise_on_error=True
    ):
        """
        Checks if the given command version is equal or higher than
        the given version tuple.

        :param string call: the command the check
        :param tuple version_waterline: minimum desired version of the command
        :param list version_flags: a list with the required command arguments.
        :param string root: root directory of the env to validate

        :return: True if the current command version is equal or higher to
        version_waterline
        :rtype: boolean
        """
        if root:
            arguments = ['chroot', root, call] + version_flags
        else:
            arguments = [call] + version_flags
        version_info = None
        try:
            command = Command.run(arguments)
            for line in command.output.splitlines():
                match = re.search('[0-9]+(\.[0-9]+)*', line)
                if match:
                    version_info = tuple(
                        int(elt) for elt in match.group(0).split('.')
                    )
                    break
            if version_info is None:
                raise Exception
        except Exception:
            message = 'Could not parse {0} version'.format(call)
            if raise_on_error:
                raise KiwiCommandCapabilitiesError(message)
            log.warning(message)
            return False
        return version_info >= version_waterline
