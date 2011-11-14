import fabric.api
import types


def all_maker(ns):
    return tuple([k for k, v in ns.items()
                  if not k.startswith('_') \
                      and type(v) != types.ModuleType])


class LoggerMixin(object):

    def log(self, s, cmd=''):
        m = '[local]'
        if hasattr(self, 'runner'):
            run_local = self.runner.run_local
        else:
            run_local = self.run_local

        if not run_local:
            m = '[%s]' % fabric.api.env.host_string
        m += ' '
        if cmd:
            m += cmd + ': '
        m += s
        print(m)
