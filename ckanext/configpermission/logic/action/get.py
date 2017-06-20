from ckanext.configpermission.model import AuthRole


def member_roles_list():
    return [x.name for x in AuthRole.all()]