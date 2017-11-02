from ckanext.configpermission.model import AuthMember
from jinja2.runtime import Undefined


def get_role(user_id, group_id):
    if type(user_id) == Undefined:
        user_id = None
    if type(group_id) == Undefined:
        group_id = None
    member = AuthMember.by_group_and_user_id(group_id=group_id, user_id=user_id)
    if member is None or member.role is None:
        return 'N/A'
    return member.role.display_name


def get_role_selected(user_id, group_id):
    if type(user_id) == Undefined:
        user_id = None
    if type(group_id) == Undefined:
        group_id = None

    member = AuthMember.by_group_and_user_id(group_id=group_id, user_id=user_id)
    if member is None or member.role is None:
        return ''
    else:
        return member.role.name