from ckanext.configpermission.model import AuthMember
from ckan.logic import check_access as ckan_check_access, NotAuthorized


def get_role(user_id, group_id):
    member = AuthMember.by_group_and_user_id(group_id=group_id, user_id=user_id)
    if member is None or member.role is None:
        return 'N/A'

    return member.role.display_name
