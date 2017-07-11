from ckanext.configpermission.model import AuthRole


def member_roles_list(context, data_dict):
    return [x.name for x in AuthRole.all()]