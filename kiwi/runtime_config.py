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
import os
import yaml

# project
from .logger import log
from .defaults import Defaults
from .utils.size import StringToSize
from .exceptions import (
    KiwiRuntimeConfigFormatError
)


class RuntimeConfig(object):
    """
    Implements reading of runtime configuration file:

    * ~/.config/kiwi/config.yml

    The KIWI runtime configuration file is a yaml formatted file
    containing information to control the behavior of the tools
    used by KIWI.
    """
    def __init__(self):
        self.config_data = None

        config_file = os.sep.join(
            [self._home_path(), '.config', 'kiwi', 'config.yml']
        )
        if os.path.exists(config_file):
            log.info('Reading runtime config file: {0}'.format(config_file))
            with open(config_file, 'r') as config:
                self.config_data = yaml.load(config)

    def get_obs_download_server_url(self):
        """
        Return URL of buildservice download server in:

        obs:
          - download_url: ...

        if no configuration exists the downloadserver from
        the Defaults class is returned

        :rtype: string
        """
        obs_download_server_url = self._get_attribute(
            element='obs', attribute='download_url'
        )
        return obs_download_server_url if obs_download_server_url else \
            Defaults.get_obs_download_server_url()

    def is_obs_public(self):
        """
        Check if the buildservice configuration is public or private in:

        obs:
          - public: true|false

        if no configuration exists we assume to be public

        :rtype: bool
        """
        obs_public = self._get_attribute(element='obs', attribute='public')
        if obs_public is None:
            # if the privacy attribute is not set we assume to be public
            obs_public = True
        return bool(obs_public)

    def get_xz_options(self):
        """
        Return list of XZ compression options in:

        xz:
          - options: ...

        if no configuration exists None is returned

        :rtype: list
        """
        xz_options = self._get_attribute(element='xz', attribute='options')
        return xz_options.split() if xz_options else None

    def get_iso_tool_category(self):
        """
        Return tool category which should be used to build iso images

        iso:
          - tool_category: cdrtools|xorriso

        if no or invalid configuration exists the default tool category
        from the Defaults class is returned

        :rtype: string
        """
        iso_tool_category = self._get_attribute(
            element='iso', attribute='tool_category'
        )
        if not iso_tool_category:
            return Defaults.get_iso_tool_category()
        elif 'cdrtools' in iso_tool_category or 'xorriso' in iso_tool_category:
            return iso_tool_category
        else:
            log.warning(
                'Skipping invalid iso tool category: {0}'.format(
                    iso_tool_category
                )
            )
            return Defaults.get_iso_tool_category()

    def get_max_size_constraint(self):
        """
        Returns the maximum allowed size of the built image. The value is
        returned in bytes and it is specified in build_constraints element
        with the max_size attribute. The value can be specified in bytes or
        it can be specified with m=MB or g=GB.

        build_constraints:
          - max_size: 700m

        if no configuration exists None is returned

        :rtype: list
        """
        max_size = self._get_attribute(
            element='build_constraints', attribute='max_size'
        )
        return StringToSize.to_bytes(max_size) if max_size else None

    def _get_attribute(self, element, attribute):
        if self.config_data:
            try:
                if element in self.config_data:
                    for attribute_dict in self.config_data[element]:
                        if attribute in attribute_dict:
                            return attribute_dict[attribute]
            except Exception as e:
                raise KiwiRuntimeConfigFormatError(
                    '{error_type}: {error_text}'.format(
                        error_type=type(e).__name__, error_text=format(e)
                    )
                )

    def _home_path(self):
        return os.environ['HOME']
