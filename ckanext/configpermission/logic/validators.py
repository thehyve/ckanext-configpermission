import ckan.lib.navl.dictization_functions as df
from ckan.common import _

from ckanext.configpermission.model import AuthRole


def role_exists(role, context):
    if AuthRole.get(role) is None:
        raise df.Invalid(_('role does not exist.'))
    return role