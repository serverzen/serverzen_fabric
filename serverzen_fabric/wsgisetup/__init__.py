import fabric.api
import shutil
import os
import tempfile
from lazy import lazy
import pkg_resources
from fabric.api import settings, hide
from serverzen_fabric import ve
from serverzen_fabric.services import ApacheService
from serverzen_fabric import utils, _internal


class WSGIHelper(utils.RunnerMixin):

    wsgiapps_dir = '/usr/local/wsgiapps'
    pythonapps_dir = '/usr/local/pythonapps'
    ve_script = pythonapps_dir + '/virtualenv/virtualenv.py'

    def __init__(self):
        self.apache_service = ApacheService()
        self.apache_service._runner = self.runner

    def setup_base(self):
        r = self.runner.clone(sudo_user='root')
        r.run('mkdir -p ' + self.wsgiapps_dir)
        r.run('chown www-data:www-data -R ' + self.wsgiapps_dir)

    @lazy
    def wsgi_script(self):
        return pkg_resources.resource_string(__name__, 'wsgi_script.tmpl')

    @lazy
    def apache_conf(self):
        return pkg_resources.resource_string(__name__, 'apache_conf.tmpl')

    def setup_wsgiapp(self,
                      webapp_name,
                      public_host,
                      app_factory,
                      develop_eggs=None,
                      remove_if_exists=False,
                      webapp_owner='www-data',
                      extraapache='',
                      extraapachevh='',
                      upgrade_eggs=False):

        self.setup_base()

        r = self.runner.clone(sudo_user=webapp_owner)

        loc = '%s/%s' % (self.wsgiapps_dir, webapp_name)
        with settings(hide('warnings'), warn_only=True):
            if remove_if_exists:
                print('Removing previous virtualenv: %s' % loc)
                r.run('rm -Rf %s' % loc)
            if not r.run('test -e %s/bin/python' % loc).succeeded:
                s = ve.VirtualEnvSetup(self.ve_script)
                s._runner = r
                s.createve(loc)

        env = ve.VirtualEnv(loc)
        env._runner = r

        local = r.clone(sudo_user=None, run_local=True)
        d = tempfile.mkdtemp()
        paths = []

        for item in develop_eggs:
            if isinstance(item, basestring):
                item = [item]

            with fabric.api.settings(fabric.api.hide('stdout', 'stderr')):
                for x in item:
                    full = os.path.abspath(x)
                    with local.cd(full):
                        print('Setting up: ' + full)
                        local.run('python setup.py sdist --dist-dir %s' % d)
                for x in os.listdir(d):
                    f = os.path.join(d, x)
                    r.put(f, '/tmp/' + x)
                    paths.append('/tmp/' + x)
            shutil.rmtree(d)
            env.install(paths, upgrade_eggs=upgrade_eggs)

        server_name = public_host
        wsgi_file = env.loc + '/' + server_name + '.wsgi'
        params = dict(
            server_name=server_name,
            wsgi_file=wsgi_file,
            site_packages=env.site_packages,
            app_loader=app_factory % {'virtualenv': env.loc},
            extraapache=extraapache,
            extraapachevh=extraapachevh,
            process_name=webapp_name.replace('.', '-')
            )
        r.createfile(wsgi_file, self.wsgi_script % params)

        vhost_file = env.loc + '/apache-vhost.conf'
        r.createfile(vhost_file, self.apache_conf % params)

        r.clone(sudo_user='root') \
            .symlink(vhost_file,
                     '/etc/apache2/sites-enabled/100-' + server_name + '.conf',
                     True)

        self.apache_service.reload()

__all__ = _internal.all_maker(globals())
