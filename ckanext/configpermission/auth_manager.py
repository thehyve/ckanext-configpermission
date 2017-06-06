from ckanext.configpermission import model as auth_model
from ckanext.configpermission import default_roles

from ckan.logic import auth as logic_auth

from logging import getLogger
log = getLogger(__name__)

allowed = {'success': True}
not_allowed = {'success': False}


class AuthManager(object):

    def __init__(self, permissions):
        self.permissions = [x['name'] for x in permissions]
        # Dynamically assign permission functions to the class
        # All these functions are just a wrapper around check_access

        for permission in permissions:
            name = permission['name']
            role = permission['role']

            setattr(self, name, self.make_access_func(name))
            if not role['is_registered']:
                setattr(getattr(self, name), 'auth_allow_anonymous_access', True)

    def make_access_func(self, name):
        return lambda context, data_dict: self.check_access(context, data_dict, action=name)

    def check_access(self, context, data_dict, action=None):
        """
        Method used to see if someone has access. Looks up the rules and roles in the database based on the context and
        datadict and return the result. The CKAN level check_access method calls this method to check for access for all
        overwritten permissions. It also gives access to everything to sysadmins, so if a user is a sysadmin this function
        won't be called.

        :param context:
        :param data_dict:
        :param action:
        :return:
        """
        auth = auth_model.AuthModel.get(action)
        user = context.get('auth_user_obj', None)

        membership = None
        owner_org = None
        log.debug('Checking access for {} with context {}'.format(action, context))

        # If anonymous users can access, everyone can.
        if not auth.min_role.is_registered:
            return allowed

        # Check the context so we find the relevant org
        if 'resource' in context and 'resource' in action:
            resource = context['resource']
            owner_org = resource.extras.get('owner_org', None)
            if owner_org is None:
                owner_org = resource.package.owner_org
        elif 'group' in context:
            owner_org = logic_auth.get_group_object(context, data_dict).id

        # If no org set at all, data is visible.
        if owner_org is None:
            return allowed
        else:
            membership = auth_model.AuthMember.by_group_and_user_id(group_id=owner_org, user_id=user.id)

        # If the user is a member of the org, check if he has the right rank
        if membership is not None:
            if auth.min_role.rank <= membership.role.rank:
                return allowed
            else:
                return not_allowed
        else:
            # If the user isn't a member, check if it is open to nonmembers and user is registered.
            if not auth.min_role.org_member and user is not None:
                return allowed
            else:
                return not_allowed
