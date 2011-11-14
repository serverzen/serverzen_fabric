import abc
from fabric.api import hide, settings, local, sudo, run, cd, lcd
import logging

logger = logging.getLogger('clue_script')


class VCSHandler(abc.ABCMeta):

    vcsuser = None
    vcspassword = None
    hide_output = True
    run_local = False
    sudo_user = None

    def __init__(self, **kwargs):
        self.change(**kwargs)

    def change(self, **kwargs):
        self.__dict__.update(kwargs)
        return self

    @abc.abstractmethod
    def checkout(self, url, location):
        pass

    @abc.abstractmethod
    def update(self, location):
        pass


class SubversionHandler(VCSHandler):

    def checkout(self, url, location):
        cmd = 'svn co'
        if self.vcsuser:
            cmd += ' --non-interactive --username %s' % self.vcsuser
        if self.vcspassword:
            cmd += ' --password %s' % self.vcspassword

        cmd += ' ' + url
        cmd += ' ' + location

        with settings(hide('running')):
            if self.run_local:
                local(cmd)
            elif self.sudo_user:
                sudo(cmd, user=self.sudo_user)
            else:
                run(cmd)

    def update(self, location):
        cmd = 'svn up'
        if self.vcsuser:
            cmd += ' --non-interactive --username %s' % self.vcsuser
        if self.vcspassword:
            cmd += ' --password %s' % self.vcspassword

        with settings(hide('running')):
            if self.run_local:
                with lcd(location):
                    local(cmd)
            elif self.sudo_user:
                with cd(location):
                    sudo(cmd, user=self.sudo_user)
            else:
                with cd(location):
                    run(cmd)


class GitHandler(VCSHandler):

    def checkout(self, url, location):
        cmd = 'git clone'

        self.check_params()

        cmd += ' ' + url
        cmd += ' ' + location

        with settings(hide('running')):
            if self.run_local:
                local(cmd)
            elif self.sudo_user:
                sudo(cmd, user=self.sudo_user)
            else:
                run(cmd)

    def check_params(self):
        if self.vcsuser:
            logger.warning('vcsuser param not supported '
                           'with Git handler at this time')
        if self.vcspassword:
            logger.warning('vcspassword param not supported '
                           'with Git handler at this time')

    def update(self, location):
        self.check_params()

        cmd = 'git pull'

        with settings(hide('running')):
            if self.run_local:
                with lcd(location):
                    local(cmd)
            elif self.sudo_user:
                with cd(location):
                    sudo(cmd, user=self.sudo_user)
            else:
                with cd(location):
                    run(cmd)


vcs_types = {
    None: SubversionHandler,  # default
    'svn': SubversionHandler,
    'git': GitHandler,
}
