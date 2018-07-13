import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.logic import schema
from ckan import authz as ckan_authz


from ckanext.configpermission.auth_manager import AuthManager
from ckanext.configpermission.logic.action.create import member_create
from ckanext.configpermission.logic.action.get import member_roles_list, organization_list_for_user
from ckanext.configpermission.logic.action.delete import member_delete
from ckanext.configpermission.logic.action.search import package_search
from ckanext.configpermission.helpers import get_role, get_role_selected, get_package_count, get_site_extra_statistics, get_resource_count
from ckanext.configpermission.logic.schema import member_schema

schema.member_schema = member_schema
controller_name = 'ckanext.configpermission.controller:PermissionController'
controller_view_action = 'management_view'
controller_update_roles_action = 'update_roles'
controller_auth_update_action = 'auth_update'


class ConfigpermissionPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IRoutes)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITemplateHelpers)

    auth_manager = None

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'configpermission')
        toolkit.add_ckan_admin_tab(config_, 'management_view', 'Permissions')

    # IAuthFunctions
    def get_auth_functions(self):
        from ckanext.configpermission.default_permissions import permissions

        # Get the default_permissions we're overwriting and return to the main CKAN site
        auth_data = {}
        self.auth_manager = AuthManager(permissions)
        for permission in [x['name'] for x in permissions]:
            auth_data[permission] = getattr(self.auth_manager, permission)

        ckan_authz.has_user_permission_for_group_or_org = self.auth_manager.has_user_permission_for_group_or_org
        return auth_data

    # IRoutes #
    def before_map(self, m):
        controller = controller_name

        m.connect('management_view', '/permissions', action=controller_view_action,
                  controller=controller)

        m.connect('roles_update', '/permissions/update_roles', action=controller_update_roles_action,
                  controller=controller)

        m.connect('auth_update', '/permissions/auth_update', action=controller_auth_update_action,
                  controller=controller)

        return m

    def after_map(self, m):
        return m

    # IActions #
    def get_actions(self):
        # Overwrite the CKAN member_create function with our own, so we can hook into member creation.
        # Overwrite the member_roles get function as well, so it returns the new roles
        return {'member_create': member_create,
                'member_roles_list': member_roles_list,
                'member_delete': member_delete,
                'organization_list_for_user': organization_list_for_user,
                'package_search': package_search}

    #ITemplateHelpers
    def get_helpers(self):
        '''Register the most_popular_groups() function above as a template
        helper function.

        '''
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        return {'get_role': get_role,
                'get_role_name': get_role_selected,
                'get_package_count': get_package_count,
                'get_site_extra_statistics': get_site_extra_statistics,
                'get_resource_count': get_resource_count}
