from ckanext.configpermission.logic.validators import role_exists
from ckan.logic.validators import not_missing, group_id_or_name_exists, user_id_or_name_exists


def member_schema():
    schema = {
        'id': [not_missing, group_id_or_name_exists, unicode],
        'username': [not_missing, user_id_or_name_exists, unicode],
        'role': [not_missing, role_exists, unicode],
    }
    return schema
