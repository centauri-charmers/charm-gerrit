# Copyright 2020 Centauri Solutions
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module containing base class for implementing Gerrit charm tests."""

import logging
import unittest

import zaza.charm_lifecycle.utils as lifecycle_utils
import zaza.model as model


class GerritBaseTests(unittest.TestCase):

    run_resource_cleanup = False

    @classmethod
    def resource_cleanup(cls):
        """Cleanup any resources created during the test run.

        Override this method with a method which removes any resources
        which were created during the test run. If the test sets
        "self.run_resource_cleanup = True" then cleanup will be
        performed.
        """
        pass

    @classmethod
    def tearDown(cls):
        """Run teardown for test class."""
        if cls.run_resource_cleanup:
            logging.info('Running resource cleanup')
            cls.resource_cleanup()

    @classmethod
    def setUpClass(cls, application_name=None, model_alias=None):
        """Run setup for test class to create common resources."""
        cls.model_aliases = model.get_juju_model_aliases()
        if model_alias:
            cls.model_name = cls.model_aliases[model_alias]
        else:
            cls.model_name = model.get_juju_model()
        cls.test_config = lifecycle_utils.get_charm_config(fatal=False)
        if application_name:
            cls.application_name = application_name
        else:
            cls.application_name = cls.test_config['charm_name']
        cls.lead_unit = model.get_lead_unit_name(
            cls.application_name,
            model_name=cls.model_name)
        logging.debug('Leader unit is {}'.format(cls.lead_unit))


class GerritTests(GerritBaseTests):
    """Encapsulate testing of Gerrit."""

    def test_gerrit_is_listening(self):
        pass
