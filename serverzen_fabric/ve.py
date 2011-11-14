import fabric.api
import urlparse
import os
from serverzen_fabric.runner import Runner
from serverzen_fabric import _internal, utils
from serverzen_fabric.archive import Archive, find_latest

VE_DOWNLOAD = ('http://pypi.python.org/packages/source/v/virtualenv/'
               'virtualenv-1.6.4.tar.gz')


class _VirtualEnvHelper(object):

    runner_factory = staticmethod(Runner)
    find_latest = staticmethod(find_latest)

    def installve(self, location, sudo_user=None, run_local=False):
        '''Install latest virtualenv.

          :param location: base directory to install virtualenv
          :param sudo_user: user to sudo as (assumes run_local=False)

          :param run_local: run commands locally (False by default)
        '''

        runner = self.runner_factory(sudo_user=sudo_user,
                                     run_local=run_local)

        url = VE_DOWNLOAD
        parts = urlparse.urlparse(url)
        name = os.path.basename(parts.path)
        with runner.cd('/tmp'):
            runner.run('wget %s -O %s' % (url, name))

        archive = Archive('/tmp/' + name)
        archive._runner = runner
        archive.extractall(location)

        newdir = location + '/' + name
        if newdir.endswith('.tar.gz'):
            newdir = newdir[:-7]
        elif newdir.endswith('.tar.bz2'):
            newdir = newdir[:8]
        else:
            s = newdir.rsplit('.', 1)
            if len(s) > 1:
                newdir = s[0]

        runner.run('rm -f %s/virtualenv' % location)
        runner.run('ln -s %s %s/virtualenv' % (newdir, location))

installve = _VirtualEnvHelper().installve


class VirtualEnvSetup(utils.RunnerMixin):

    def __init__(self, veloc, pythonexec=None):
        self.veloc = veloc
        self._pythonexec = pythonexec

    @property
    def pythonexec(self):
        return self._pythonexec or 'python'

    _marker = object()

    def createve(self, location, sudo_user=_marker, run_local=_marker):
        runner = self.runner.clone()
        if sudo_user is not self._marker:
            runner.sudo_user = sudo_user
        if run_local is not self._marker:
            runner.run_local = run_local
        runner.run('%s %s %s' % (self.pythonexec, self.veloc, location))


class VirtualEnv(utils.RunnerMixin, _internal.LoggerMixin):

    def __init__(self, loc):
        self.loc = loc

    def install(self, pkgs, upgrade_eggs=False):
        if isinstance(pkgs, basestring):
            pkgs = [pkgs]

        extra = ''
        if upgrade_eggs:
            extra = '-U'

        self.log('Installing %r, upgrade_eggs=%s' % (pkgs, upgrade_eggs),
                 'virtualenv.install')
        self.runner.run('%s/bin/pip install %s %s' % (self.loc,
                                                      extra,
                                                      ' '.join(pkgs)))

    def install_reqs(self, filename):
        self.runner.run('%s/bin/pip install -r %s' % (self.loc,
                                                      filename))

    @property
    def site_packages(self):
        # find the pythonX dir
        lib = os.path.join(self.loc, 'lib')
        if self.runner.run_local:
            pdir = os.path.join(lib,
                                os.listdir(lib)[0])
        else:
            with fabric.api.settings(fabric.api.hide('stdout', 'stderr')):
                ls = self.runner.run('ls -1 %s' % lib)
            pdir = os.path.join(lib, ls.strip().split('\n')[0].strip())

        return os.path.join(pdir, 'site-packages')

__all__ = _internal.all_maker(globals())
