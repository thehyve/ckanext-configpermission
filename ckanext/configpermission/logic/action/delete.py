from ckan.logic.action.delete import member_delete as ckan_member_delete
from ckanext.configpermission.model import AuthMember


def member_delete(context, data_dict):
    user_id = data_dict.get('object', None)
    group_id = data_dict.get('id', None)
    plugin_membership = AuthMember.by_group_and_user_id(group_id=group_id, user_id=user_id)
    if plugin_membership is not None:
        AuthMember.delete(group_id=group_id, user_id=user_id)
    # Remove from CKAN system aswell
    ckan_member_delete(context=context, data_dict=data_dict)
