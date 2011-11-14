import os
from lazy import lazy
from distutils import version as distversion
from serverzen_fabric.runner import Runner


class Archive(object):

    exts = {}
    runner_factory = staticmethod(Runner)

    def __init__(self, filename):
        self.filename = filename
        self._runner = None

    @property
    def runner(self):
        if self._runner is None:
            self._runner = self.runner_factory()
        return self._runner

    def _get_extractor(self):
        extractor = None
        for x in self.exts:
            if self.filename.endswith(x):
                extractor = self.exts[x]
                break
        return extractor

    @lazy
    def extractor(self):
        extractor = self._get_extractor()
        if extractor is None:
            raise ValueError('Filename must end with one of: %s' % self.exts)
        return extractor

    def is_acceptable(self):
        return self._get_extractor() is not None

    _marker = object()

    def extractall(self, tdir, sudo_user=_marker, run_local=_marker):
        runner = self.runner.clone()
        if sudo_user is not self._marker:
            runner.sudo_user = sudo_user
        if run_local is not self._marker:
            runner.run_local = run_local
        with runner.cd(tdir):
            runner.run(self.extractor + ' ' + self.filename)

    exts.update({'.tar.gz': 'tar zxf',
                 '.tar.bz2': 'tar jxf',
                 '.tar': 'tar xf',
                 '.tgz': 'tar zxf',
                 '.zip': 'unzip x'})


class Dist(object):

    def __init__(self, name, version, filename=None):
        self.name = name
        self.version = version
        self.filename = filename

    @classmethod
    def parse_from_filename(cls, fname):
        ext = None
        for x in Archive.exts:
            if fname.endswith(x):
                ext = x
                break
        if ext is None:
            raise TypeError('File does not end with known '
                            'extensions: %s' % Archive.exts)
        dname = fname[:-1 * len(ext)]

        dashpos = dname.rfind('-')
        ver = dname[dashpos + 1:]
        dname = dname[:-1 * len(ver) - 1]
        ver = distversion.StrictVersion(ver)
        return cls(dname, ver, fname)

    def __repr__(self):
        return '<%s: %s-%s>' % (self.__class__.__name__,
                                self.name,
                                self.version)

    def __cmp__(self, x):
        if not isinstance(x, Dist):
            return -1
        if self.name != x.name:
            return cmp(self.name, x.name)
        return cmp(self.version, x.version)


def find_latest(dist_name, location='.'):
    match = dist_name + '-'
    latest = None
    for x in os.listdir(location):
        if x.startswith(match) and Archive(x).is_acceptable():
            xdist = Dist.parse_from_filename(os.path.join(location, x))
            if latest is None or xdist > latest:
                latest = xdist
    return latest
