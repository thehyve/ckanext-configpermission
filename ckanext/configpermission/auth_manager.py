from ckanext.configpermission import model as auth_model
from ckanext.configpermission import default_roles

from ckan.authz import has_user_permission_for_group_or_org as ckan_has_user_permission_for_group_or_org
from ckan import model as ckan_model
from ckan.logic import auth as logic_auth, ValidationError, NotFound
from ckan.logic.auth import get as auth_get

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

            setattr(self, name, self._make_access_func(name))
            if not role['is_registered']:
                setattr(getattr(self, name), 'auth_allow_anonymous_access', True)

    def _make_access_func(self, name):
        # Needs to be it's own function to give every function it's own scope (so name gets passed correctly)
        return lambda context, data_dict: self.check_access(context, data_dict, action=name)

    def _get_owner_org(self, context, data_dict, action):
        owner_org = None

        # Check the context so we find the relevant org
        if 'resource' in context and 'resource' in action:
            resource = context['resource']
            owner_org = resource.extras.get('owner_org', None)
            if owner_org is None:
                owner_org = resource.package.owner_org
        elif 'group' in context:
            owner_org = logic_auth.get_group_object(context, data_dict).id
        elif 'owner_org' in data_dict:
            owner_org = data_dict.get('owner_org')
        elif 'package' in context and 'package' in action:
            package = context['package']
            owner_org = package.owner_org
        elif 'org_data' in data_dict:
            org_data = data_dict['org_data']
            owner_org = org_data.get('id', None)
        else:
            try:
                package = logic_auth.get_package_object(context, data_dict)
            except (ValidationError, NotFound):
                package = None

            if package is None:
                try:
                    owner_org = logic_auth.get_group_object(context, data_dict).id
                except (ValidationError, NotFound):
                    owner_org = None
            else:
                owner_org = package.owner_org

        return owner_org

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

        # Done like this instead of as default value because python behaves weirdly when you do that.
        # See: https://python-guide-pt-br.readthedocs.io/en/latest/writing/gotchas/#mutable-default-arguments
        if data_dict is None:
            data_dict = {}
        if context is None:
            context = {}
        auth = auth_model.AuthModel.get(action)
        user = context.get('auth_user_obj', None)

        membership = None
        owner_org = None
        log.debug('Checking access for {} with context {}'.format(action, context))

        # If anonymous users can access, everyone can.
        if not auth.min_role.is_registered:
            log.debug('{} allowed'.format(action))
            if action == 'dataset_privacy_edit':
                import pdb;
                pdb.set_trace()
            return allowed
        elif user is None:
            log.debug("{} action not allowed without user account".format(action))
            return not_allowed

        owner_org = self._get_owner_org(context, data_dict, action)

        # If no org and no id set at all, data is visible.
        if owner_org is None and 'id' not in data_dict:
            if not auth.min_role.org_member:
                log.debug('{} allowed'.format(action))

                return allowed
            else:
                memberships = auth_model.AuthMember.by_user_id(user_id=user.id)
                if len(memberships) > 0:
                    log.debug('{} allowed'.format(action))
                    if action == 'dataset_privacy_edit':
                        import pdb;
                        pdb.set_trace()
                    return allowed
                else:
                    log.debug('{} not allowed, not a group member'.format(action))
                    return not_allowed
        elif 'id' in data_dict:
            # Use ckan methods to check if user follows this object.
            if 'followee' in action:
                return auth_get._followee_list(context, data_dict)

        # 'Owned' packages can still be edited
        if 'package' in context and 'package' in action:
            package = context.get('package')
            if package.creator_user_id == user.id:
                return allowed
        elif 'package' in data_dict:
            package_dict = data_dict.get('package')
            package_creator = package_dict.get('creator_user_id', None)
            if package_creator == user.id:
                return allowed

        membership = auth_model.AuthMember.by_group_and_user_id(group_id=owner_org, user_id=user.id)
        # If the user is a member of the org, check if he has the right rank
        if membership is not None:
            if auth.min_role.rank <= membership.role.rank:
                log.debug('{} allowed'.format(action))
                if action == 'dataset_privacy_edit':
                    import pdb;
                    pdb.set_trace()
                return allowed
            else:
                log.debug('{} not allowed min role required: {}, user role: {}'.format(action, auth.min_role, membership.role))
                return not_allowed
        else:
            # If the user isn't a member, check if it is open to nonmembers and user is registered.
            if not auth.min_role.org_member and user is not None:
                log.debug('{} allowed'.format(action))
                if action == 'dataset_privacy_edit':
                    import pdb;
                    pdb.set_trace()
                return allowed
            else:
                log.debug('{} not allowed, membership required but not there.'.format(action))
                return not_allowed

    def has_user_permission_for_group_or_org(self, group_id, user_name, permission):
        if permission in self.permissions:
            context = {'user': user_name, 'owner_org': group_id}
            data_dict = {}
            return self.check_access(context, data_dict, action=permission)
        else:
            return ckan_has_user_permission_for_group_or_org(group_id, user_name, permission)