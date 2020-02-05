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

import logging
import socket
import subprocess
from charmhelpers.core.hookenv import resource_get


def gerrit_war():
    """The path to the war file for Gerrit.

    :returns: path to a war file or None
    :rtype: Union[str, None]"""
    return resource_get('gerrit')


def install(war, location):
    """Install gerrit into the configured location.

    :param war: The location of the war file for Gerrit
    :type war: str
    :param location: Where to isntall Gerrit
    :type location: str
    """
    res = subprocess.check_call([
        "sudo", "-u", "gerrit",
        "java", "-jar", war,
        "init", "-d", location,
        "--batch",
        "--install-all-plugins",
        "--no-auto-start"])
    logging.debug(res)


def get_fqdn(name=None):
    """Get the official FQDN of the host
    The implementation of ``socket.getfqdn()`` in the standard Python
    library does not exhaust all methods of getting the official name
    of a host ref Python issue https://bugs.python.org/issue5004
    This function mimics the behaviour of a call to ``hostname -f`` to
    get the official FQDN but returns an empty string if it is
    unsuccessful.
    :param name: Shortname to get FQDN on
    :type name: Optional[str]
    :returns: The official FQDN for host or empty string ('')
    :rtype: str
    """
    name = name or socket.gethostname()
    fqdn = ''

    try:
        addrs = socket.getaddrinfo(
            name, None, 0, socket.SOCK_DGRAM, 0, socket.AI_CANONNAME)
    except OSError:
        pass
    else:
        for addr in addrs:
            if addr[3]:
                if '.' in addr[3]:
                    fqdn = addr[3]
                break
    return fqdn
