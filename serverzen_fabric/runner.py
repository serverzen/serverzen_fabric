import os
import tempfile
import fabric.api
from serverzen_fabric import _internal


class Runner(_internal.LoggerMixin):

    cur_dir = None

    _fabric_local = staticmethod(fabric.api.local)
    _fabric_run = staticmethod(fabric.api.run)
    _fabric_sudo = staticmethod(fabric.api.sudo)
    _fabric_put = staticmethod(fabric.api.put)

    def __init__(self, sudo_user=None, run_local=False):
        self.sudo_user = sudo_user
        self.run_local = run_local

    def clone(self, **kwargs):
        runner = self.__class__()
        runner.__dict__.update(**self.__dict__)
        runner.__dict__.update(**kwargs)
        return runner

    def run(self, *args, **kwargs):
        args = list(args)
        kwargs = dict(kwargs)
        func = self._fabric_run

        if self.run_local:
            func = self._fabric_local

        if self.sudo_user:
            kwargs.setdefault('user', self.sudo_user)
            func = self._fabric_sudo

        return func(*args, **kwargs)

    def cd(self, path):
        if self.run_local:
            return fabric.api.lcd(path)
        return fabric.api.cd(path)

    def put(self, filename, location):
        if self.run_local:
            self.run('cp %s %s' % (filename, location))
        elif not self.sudo_user:
            self._fabric_put(filename, location)
        else:
            import uuid
            tempname = str(uuid.uuid4())
            cur = fabric.api.env.get('cwd')
            fabric.api.env['cwd'] = None
            self._fabric_put(filename, tempname)
            self._fabric_sudo('cp %s %s' % (tempname, location),
                              user=self.sudo_user)
            self._fabric_sudo('rm %s' % tempname)
            fabric.api.env['cwd'] = cur

    def createfile(self, filename, text):
        f = tempfile.NamedTemporaryFile(mode='wt')
        try:
            f.write(text)
            f.flush()
            self.put(f.name, filename)
        finally:
            f.close()

    def symlink(self, source, target, remove_if_exists=False):
        if remove_if_exists:
            self.log('removing existing link -> %s' % target, 'symlink')
            self.run('rm -f %s' % target)
        self.log('%s -> %s' % (source, target), 'symlink')
        self.run('ln -s %s %s' % (source, target))

__all__ = _internal.all_maker(globals())
