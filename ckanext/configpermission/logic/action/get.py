from ckanext.configpermission.model import AuthRole


def member_roles_list(context, data_dict):
    return [{'text': x.display_name, 'value': x.name} for x in AuthRole.all()]