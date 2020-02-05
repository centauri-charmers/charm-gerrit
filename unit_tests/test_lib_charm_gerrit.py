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

import mock

import charms_openstack.test_utils as test_utils

import charm.gerrit as gerrit


class Helper(test_utils.PatchHelper):

    def setUp(self):
        super().setUp()


class TestGerritCharm(Helper):

    @mock.patch.object(gerrit, 'resource_get')
    def test_gerrit_war(self, resource_get):
        gerrit.gerrit_war()
        resource_get.assert_called_once_with('gerrit')

    @mock.patch.object(gerrit.subprocess, 'check_call')
    def test_gerrit_install(self, check_call):
        gerrit.install('/path/to/war', '/path/to/install')
        check_call.assert_called_once_with([
            "sudo", "-u", "gerrit",
            "java", "-jar", "/path/to/war", "init", "-d", "/path/to/install",
            "--batch",
            "--install-all-plugins",
            "--no-auto-start"])
