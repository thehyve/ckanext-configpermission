from ckanext.configpermission.model import AuthMember
from ckan.model import User, Group
from jinja2.runtime import Undefined
from ckan import logic

get_action = logic.get_action


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


def get_package_count(c, organization):
    user = User.get(c.user)
    org = Group.get(organization['name'])

    return get_action('package_search')({'user_id': user.id, 'with_private': False, 'auth_user_obj': user},
                                        {'fq': 'owner_org:"{}"'.format(org.id), 'include_private': False}).get('count', 0)
