from ckanext.configpermission.model import AuthMember


def get_role(user_id, group_id):
    member = AuthMember.by_group_and_user_id(group_id=group_id, user_id=user_id)
    return member.role.display_name
