from serverzen_fabric.runner import Runner
from serverzen_fabric import _internal


class RunnerMixin(object):
    runner_factory = staticmethod(Runner)

    @property
    def runner(self):
        if not hasattr(self, '_runner'):
            self._runner = self.runner_factory()
        return self._runner


def makebool(v):
    if isinstance(v, bool):
        return v

    if isinstance(v, int):
        return bool(v)

    v = str(v).lower().strip()
    if v in ('true', '1'):
        return True

    return False

__all__ = _internal.all_maker(globals())
