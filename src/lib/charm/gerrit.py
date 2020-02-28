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
import os
import socket
import subprocess
from charmhelpers import core as ch_core
from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import resource_get
from charmhelpers.core.host import mkdir
from urllib.request import urlopen


def gerrit_war():
    """The path to the war file for Gerrit.

    :returns: path to a war file or None
    :rtype: Union[str, None]"""
    res = resource_get('gerrit')
    if res:
        return res
    dest_dir = os.path.join(os.environ.get('CHARM_DIR'), 'fetched')
    if not os.path.exists(dest_dir):
        mkdir(dest_dir, perms=0o755)
    dld_file = os.path.join(dest_dir, "gerrit-3.1.2.war")
    response = urlopen(
        "https://gerrit-releases.storage.googleapis.com/gerrit-3.1.2.war")
    try:
        with open(dld_file, 'wb') as dest_file:
            dest_file.write(response.read())
    except Exception as e:
        if os.path.isfile(dld_file):
            os.unlink(dld_file)
        logging.warn("Error downloading gerrit: {}".format(e))
        return None
    return dld_file


def install(war, location):
    """Install gerrit into thehookenv.configured location.

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



def render_config(fqdn, ssl_enabled=False):
    context = {
        "fqdn": hookenv.config('fqdn') or get_fqdn(),
        'ssl_enabled': ssl_enabled,
        "smtp_from":hookenv.config("smtp_from"),
        "smtp_server":hookenv.config('smtp_host'),
        "smtp_server_port":hookenv.config('smtp_port'),
        "smtp_encryption": "TLS",
        "smtp_user":hookenv.config('smtp_user'),
        "smtp_password":hookenv.config('smtp_pass'),
    }
    return ch_core.templating.render(
        'gerrit.conf.j2',
        context=context,
        target=gerrit_config_path(),
        owner='gerrit',
        group='gerrit',
        perms=0o650,
    )


def gerrit_directory():
    return hookenv.config('gerrit-directory')


def gerrit_config_path():
    return "{}/etc/gerrit.config".format(gerrit_directory())


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
    _fqdn = ''
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
                else:
                    _fqdn = addr[3]
    return fqdn or _fqdn
