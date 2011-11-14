from serverzen_fabric.runner import Runner


class UbuntuSupport(object):

    runner_factory = Runner
    apacheinitd = '/etc/init.d/apache2'

    def __init__(self):
        self.runner = self.runner_factory(sudo_user='root')

    def install_pkgs(self, pkgs):
        if isinstance(pkgs, basestring):
            pkgs = [pkgs]

        self.runner.run('apt-get install -q -y %s' % ' '.join(pkgs))
