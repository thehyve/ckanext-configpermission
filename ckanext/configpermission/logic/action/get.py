from ckanext.configpermission.model import AuthRole, AuthModel, AuthMember

import logging

import sqlalchemy

import ckan.lib.dictization
import ckan.logic as logic
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.navl.dictization_functions
import ckan.authz as authz

log = logging.getLogger('ckan.logic')

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_validate = ckan.lib.navl.dictization_functions.validate
_table_dictize = ckan.lib.dictization.table_dictize
_check_access = logic.check_access
NotFound = logic.NotFound
ValidationError = logic.ValidationError
_get_or_bust = logic.get_or_bust

_select = sqlalchemy.sql.select
_aliased = sqlalchemy.orm.aliased
_or_ = sqlalchemy.or_
_and_ = sqlalchemy.and_
_func = sqlalchemy.func
_desc = sqlalchemy.desc
_case = sqlalchemy.case
_text = sqlalchemy.text


def member_roles_list(context, data_dict):
    return [{'text': x.display_name, 'value': x.name} for x in AuthRole.all() if x.org_member]


def organization_list_for_user(context, data_dict):
    '''Return the organizations that the user has a given permission for.

    By default this returns the list of organizations that the currently
    authorized user can edit, i.e. the list of organizations that the user is an
    admin of.

    Specifically it returns the list of organizations that the currently
    authorized user has a given permission (for example: "manage_group") against.

    When a user becomes a member of an organization in CKAN they're given a
    "capacity" (sometimes called a "role"), for example "member", "editor" or
    "admin".

    Each of these roles has certain permissions associated with it. For example
    the admin role has the "admin" permission (which means they have permission
    to do anything). The editor role has permissions like "create_dataset",
    "update_dataset" and "delete_dataset".  The member role has the "read"
    permission.

    This function returns the list of organizations that the authorized user
    has a given permission for. For example the list of organizations that the
    user is an admin of, or the list of organizations that the user can create
    datasets in. This takes account of when permissions cascade down an
    organization hierarchy.

    :param permission: the permission the user has against the
        returned organizations, for example ``"read"`` or ``"create_dataset"``
        (optional, default: ``"edit_group"``)
    :type permission: string

    :returns: list of organizations that the user has the given permission for
    :rtype: list of dicts

    '''
    model = context['model']
    user = context['user']

    _check_access('organization_list_for_user', context, data_dict)
    sysadmin = authz.is_sysadmin(user)

    orgs_q = model.Session.query(model.Group) \
        .filter(model.Group.is_organization == True) \
        .filter(model.Group.state == 'active')

    if not sysadmin:
        # for non-Sysadmins check they have the required permission

        # NB 'edit_group' doesn't exist so by default this action returns just
        # orgs with admin role
        permission = data_dict.get('permission', 'edit_group')

        roles = AuthRole.get_role_with_permission(permission)

        if not roles:
            return []
        user_id = authz.get_user_id_for_username(user, allow_none=True)
        if not user_id:
            return []

        memberships = [x for x in AuthMember.by_user_id(user_id=user_id) if x.role in roles]
        group_ids = [x.group_id for x in memberships]
        #
        # q = model.Session.query(model.Member, model.Group) \
        #     .filter(model.Member.table_name == 'user') \
        #     .filter(model.Member.capacity.in_(roles)) \
        #     .filter(model.Member.table_id == user_id) \
        #     .filter(model.Member.state == 'active') \
        #     .join(model.Group)
        #
        # group_ids = set()
        # roles_that_cascade = \
        #     authz.check_config_permission('roles_that_cascade_to_sub_groups')
        # for member, group in q.all():
        #     if member.capacity in roles_that_cascade:
        #         group_ids |= set([
        #             grp_tuple[0] for grp_tuple
        #             in group.get_children_group_hierarchy(type='organization')
        #             ])
        #     group_ids.add(group.id)
        #
        # if not group_ids:
        #     return []

        orgs_q = orgs_q.filter(model.Group.id.in_(group_ids))

    orgs_list = model_dictize.group_list_dictize(orgs_q.all(), context)
    return orgs_list