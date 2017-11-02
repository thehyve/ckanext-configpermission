from ckanext.configpermission.logic.validators import role_exists
from ckan.logic.validators import group_id_exists, user_name_exists


def member_schema():
    schema = {
        'id': [group_id_exists, unicode],
        'username': [user_name_exists, unicode],
        'role': [role_exists, unicode],
    }
    return schema