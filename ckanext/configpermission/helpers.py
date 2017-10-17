from ckanext.configpermission.model import AuthMember
from ckan.logic import check_access as ckan_check_access, NotAuthorized

def get_role(user_id, group_id):
    member = AuthMember.by_group_and_user_id(group_id=group_id, user_id=user_id)
    return member.role.display_name

#
# def check_access(context, data_dict):
#     try:
#         result = ckan_check_access(context=context, data_dict=data_dict)
#     except NotAuthorized:
#         return False
#     else:
#         return result