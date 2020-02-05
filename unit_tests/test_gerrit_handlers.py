# Copyright 2020 Centauri Solutions
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import print_function

import reactive.gerrit as handlers

import charms_openstack.test_utils as test_utils


class TestRegisteredHooks(test_utils.TestRegisteredHooks):

    def test_hooks(self):
        defaults = [
        ]
        hook_set = {
            'when': {
                'create_gerrit_directory': ('user.gerrit.created',),
                'setup_gerrit_config': ('directory.gerrit.created',),
                'install_gerrit': (
                    'apt.installed.openjdk-11-jre-headless',
                    'gerrit.config.ready',
                ),
                'configure_gerrit': ('charm.gerrit.installed',),
                'enable_and_start_gerrit': ("charm.gerrit.configured",),
                'configure_nginx_https': (
                    'nginx.available',
                    'lets-encrypt.registered',),
                'configure_nginx_http': ('nginx.available',),
            },
            'when_not': {
                'create_gerrit_user': ('user.gerrit.created',),
                'create_gerrit_directory': ('directory.gerrit.created',),
                'setup_gerrit_config': ('gerrit.config.ready',),
                'install_gerrit': ('charm.gerrit.installed',),
                'configure_gerrit': ('charm.gerrit.configured',),
                'enable_and_start_gerrit': ("service.gerrit.enabled",),
                'install_jre': ('apt.installed.openjdk-11-jre-headless',),
                'install_nginx': ('apt.installed.nginx',),
                'configure_nginx_http': ('lets-encrypt.registered',),
            },
            # 'when_all': {
            #     'configure_ganesha': ('config.rendered',
            #                           'ceph.pools.available',),
            # }
        }
        # test that the hooks were registered via the
        # reactive.gerrit_handlers
        self.registered_hooks_test_helper(handlers, hook_set, defaults)
