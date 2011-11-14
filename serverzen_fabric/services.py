from serverzen_fabric import utils, ossupport, _internal


class ApacheService(_internal.LoggerMixin,
                    utils.RunnerMixin, ossupport._OSMixin):

    def _apache(self, cmd):
        self.log('Executing', 'apache.' + cmd)
        self.runner.clone(sudo_user='root') \
            .run(self.os.apacheinitd + ' ' + cmd)

    def start(self):
        self._apache('start')

    def stop(self):
        self._apache('stop')

    def restart(self):
        self._apache('restart')

    def reload(self):
        self._apache('reload')

    def enable_mod(self, *mods):
        root = self.runner.clone(sudo_user='root')
        s = ''
        for mod in mods:
            if len(s) > 0:
                s += '; '
            s += 'a2enmod ' + mod
        root.run(s)

    def disable_mod(self, *mods):
        root = self.runner.clone(sudo_user='root')
        s = ''
        for mod in mods:
            if len(s) > 0:
                s += '; '
            s += 'a2dismod ' + mod
        root.run(s)
