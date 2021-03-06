# import subprocess

import charms
import charms.reactive as reactive
# import charms.reactive.relations as relations

import charmhelpers.core as ch_core
from charmhelpers.core import hookenv

import charm.gerrit as gerrit
from charms import layer


@reactive.when_not('apt.installed.openjdk-11-jre-headless')
def install_jre():
    charms.apt.queue_install(['openjdk-11-jre-headless'])


@reactive.when_not('apt.installed.nginx')
def install_nginx():
    charms.apt.queue_install(['nginx'])


@reactive.when_not('user.gerrit.created')
def create_gerrit_user():
    ch_core.host.adduser(
        'gerrit',
        password=ch_core.host.pwgen(),
        home_dir='/home/gerrit')
    reactive.set_flag('user.gerrit.created')


@reactive.when_not('directory.gerrit.created')
@reactive.when('user.gerrit.created')
def create_gerrit_directory():
    ch_core.host.mkdir(
        hookenv.config('gerrit-directory'),
        owner='gerrit',
        group='gerrit',
        perms=0o750,
    )
    reactive.set_flag('directory.gerrit.created')


@reactive.when(
    'directory.gerrit.created')
@reactive.when_not('gerrit.config.ready')
def setup_gerrit_config():
    ch_core.host.mkdir(
        "{}/etc".format(hookenv.config('gerrit-directory')),
        owner='gerrit', group='gerrit',
        perms=0o750,)
    ssl_enabled = True
    fqdn = hookenv.config('fqdn')
    if fqdn is None:
        ssl_enabled = False
        fqdn = gerrit.get_fqdn()
    gerrit.render_config(fqdn, ssl_enabled)
    reactive.set_flag('gerrit.config.ready')

@reactive.when(
    'apt.installed.openjdk-11-jre-headless',
    'gerrit.config.ready')
@reactive.when_not('charm.gerrit.installed')
def install_gerrit():
    gerrit_war = gerrit.gerrit_war()
    if gerrit_war:
        location = hookenv.config('gerrit-directory')
        gerrit.install(gerrit_war, location)
        reactive.set_flag('charm.gerrit.installed')
    else:
        hookenv.log(
            "Gerrit WAR isn't available, ensure that the resource is attached")
        hookenv.status_set('blocked', "Gerrit resource not available")


@reactive.when('charm.gerrit.installed')
@reactive.when_not('charm.gerrit.configured')
def configure_gerrit():
    context = {}
    ch_core.templating.render(
        'gerrit.default',
        context=context,
        target="/etc/default/gerrit",
    )
    ch_core.templating.render(
        'gerrit.service',
        context=context,
        target="/etc/systemd/system/gerrit.service",
    )
    reactive.set_flag('charm.gerrit.configured')


@reactive.when('charm.gerrit.configured')
@reactive.when_not('service.gerrit.enabled')
def enable_and_start_gerrit():
    ch_core.host.service_resume('gerrit')
    hookenv.open_port(29418)
    reactive.set_flag('service.gerrit.enabled')


@reactive.when('nginx.available', 'lets-encrypt.registered')
def configure_nginx_https():
    hookenv.status_set('maintenance', 'Configuring website')
    fqdn = hookenv.config().get('fqdn')
    live = layer.lets_encrypt.live()
    layer.nginx.configure_site('gerrit', 'nginx.conf',
                               key_path=live['privkey'],
                               cert_path=live['fullchain'],
                               fqdn=fqdn, ssl_enabled=True)

    gerrit.render_config(fqdn, ssl_enabled=True)
    if reactive.helpers.any_file_changed(['/etc/nginx/sites-available/gerrit']):
        reactive.set_flag('nginx.reload')
    hookenv.status_set('active', 'Unit is ready: https://%s' % fqdn)
    hookenv.open_port(80)
    hookenv.open_port(443)
    if reactive.helpers.any_file_changed([gerrit.gerrit_config_path()]):
        reactive.set_flag('gerrit.restart')


@reactive.when('nginx.available')
@reactive.when_not('lets-encrypt.registered')
def configure_nginx_http():
    hookenv.status_set('maintenance', 'Configuring website')
    fqdn = gerrit.get_fqdn()
    layer.nginx.configure_site('gerrit', 'nginx.conf',
                               fqdn=fqdn, ssl_enabled=False)
    gerrit.render_config(fqdn, ssl_enabled=False)
    if reactive.helpers.any_file_changed(['/etc/nginx/sites-available/gerrit']):
        reactive.set_flag('nginx.reload')
    hookenv.status_set('active', 'Unit is ready: http://%s' % fqdn)
    hookenv.open_port(80)
    if reactive.helpers.any_file_changed([gerrit.gerrit_config_path()]):
        reactive.set_flag('gerrit.restart')


@reactive.when('gerrit.restart')
def restart_gerrit():
    ch_core.host.service_restart('gerrit')
    hookenv.open_port(29418)
    reactive.clear_flag('gerrit.restart')


@reactive.when('nginx.restart')
def restart_nginx():
    ch_core.host.service_reload('nginx')
    hookenv.open_port(29418)
    reactive.clear_flag('nginx.restart')