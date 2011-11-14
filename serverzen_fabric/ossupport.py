import pkg_resources
from serverzen_fabric import _internal
from lazy import lazy


def lookup_os(dotted_name_or_obj):
    if isinstance(dotted_name_or_obj, basestring):
        for x in pkg_resources.iter_entry_points('serverzen_fabric_os',
                                                 dotted_name_or_obj):
            return x.load()
        return None
    return dotted_name_or_obj


class _OSMixin(object):

    osname = None

    @lazy
    def os(self):
        return lookup_os(self.osname or 'ubuntu')()


def install_os_pkgs(pkgs, os):
    lookup_os(os)().install_pkgs(pkgs)

__all__ = _internal.all_maker(globals())
