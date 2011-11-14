import unittest


class RunnerTests(unittest.TestCase):

    def setUp(self):
        self.runner = IsolatedRunner()

    def test_remote(self):
        self.runner.run('echo foo')
        self.assertEqual(self.runner._fabric_run.recorded,
                         [(('echo foo',), {})])

    def test_remote_sudo(self):
        self.runner.clone(sudo_user='user1').run('echo foo')
        self.assertEqual(self.runner._fabric_sudo.recorded,
                         [(('echo foo',), {'user': 'user1'})])

    def test_cd(self):
        from fabric.state import env
        with self.runner.cd('foo'):
            self.assertEquals(env['cwd'], 'foo')
        with self.runner.clone(run_local=True).cd('foo'):
            self.assertEquals(env['lcwd'], 'foo')


class TempMixin(object):

    def mkdtemp(self, extra=''):
        if extra:
            extra += '-'
        import tempfile
        d = tempfile.mkdtemp('', 'serverzen_fabric-' + extra)
        self.tempdirs.append(d)
        return d

    def newfile(self, filename, content=''):
        import os
        d = self.mkdtemp(filename)
        full = os.path.join(d, filename)
        f = open(full, 'w')
        f.write(content)
        f.close()
        return full

    def setUp(self):
        self.tempdirs = []

    def tearDown(self):
        import shutil
        while len(self.tempdirs) > 0:
            shutil.rmtree(self.tempdirs.pop())


class ArchiveIntegrationTests(unittest.TestCase, TempMixin):

    def setUp(self):
        TempMixin.setUp(self)

    def tearDown(self):
        TempMixin.tearDown(self)

    def _test_archive(self, archivename, type_):
        from applib import sh
        from serverzen_fabric.archive import Archive
        import os

        name1 = 'hellworld.txt'
        text1 = 'random text'
        fname = self.newfile(name1, text1)
        tempdir1 = self.mkdtemp('tempdir1-' + archivename)
        tarball = os.path.join(tempdir1, archivename)
        sh.pack_archive(tarball,
                        [fname],
                        os.path.dirname(fname),
                        type_)

        tempdir2 = self.mkdtemp('tempdir2-' + archivename)
        arc = Archive(tarball)
        arc.extractall(tempdir2, run_local=True)
        self.assertTrue(name1 in os.listdir(tempdir2),
                        'File not extracted properly')
        self.assertEqual(text1,
                         open(os.path.join(tempdir2, name1)).read())

    def test_tgz(self):
        self._test_archive('archive.tar.gz', 'tgz')

    def test_tbz2(self):
        self._test_archive('archive.tar.bz2', 'bz2')

    # TODO: find working applib that can easily construct zipfiles
    #def test_zip(self):
    #    self._test_archive('archive.zip', 'zip')

    def test_extractor(self):
        from serverzen_fabric.archive import Archive

        arc = Archive('foo.zip')
        self.assertEqual(arc.extractor, 'unzip x')

        arc = Archive('foo.bar')
        self.assertRaises(ValueError, lambda: arc.extractor)


class DistTests(unittest.TestCase):

    def test_parse_from_filename(self):
        from serverzen_fabric.archive import Dist
        dist = Dist.parse_from_filename('Foo-1.0.tar.gz')
        self.assertEqual(dist.name, 'Foo')

        self.assertRaises(TypeError, Dist.parse_from_filename, 'Foo-1.0.bar')

    def test_repr(self):
        from serverzen_fabric.archive import Dist
        dist = Dist.parse_from_filename('Foo-1.0.tar.gz')
        self.assertEqual(repr(dist), '<Dist: Foo-1.0>')

    def test_cmp(self):
        from serverzen_fabric.archive import Dist
        parse = Dist.parse_from_filename

        self.assertEqual(cmp(parse('Foo-1.0.tar.gz'),
                             parse('Foo-1.0.tar.gz')), 0)

        self.assertEqual(cmp(parse('Foo-1.0.tar.gz'), ''), -1)

        self.assertEqual(cmp(parse('Foo-1.0.tar.gz'),
                             parse('Bar-1.0.tar.gz')), 1)


class RunnerHelperTests(unittest.TestCase):

    def test_installve(self):
        from serverzen_fabric import _RunnerHelper
        helper = _RunnerHelper()
        helper.runner_factory = IsolatedRunner
        helper.find_latest = lambda x: Mock(filename='foo-1.0.tar.gz', version='1.0')
        helper.installve('foo')


from serverzen_fabric.runner import Runner


class NamedCallback(object):

    def __init__(self, name, callback=None):
        self.name = name
        self.callback = callback
        self.recorded = []

    def __call__(self, *args, **kwargs):
        self.recorded.append((args, kwargs))
        if self.callback is not None: return self.callback(*args, **kwargs)


class IsolatedRunner(Runner):
    def __init__(self, *args, **kwargs):
        super(IsolatedRunner, self).__init__(*args, **kwargs)

        self._fabric_local = NamedCallback('local')
        self._fabric_run = NamedCallback('run')
        self._fabric_sudo = NamedCallback('sudo')
        self._fabric_put = NamedCallback('put')


class Mock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
