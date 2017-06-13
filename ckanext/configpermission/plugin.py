import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.configpermission import default_roles
from ckanext.configpermission.auth_manager import AuthManager

permissions = [{'name': 'group_create', 'role': default_roles.SYSADMIN}]

controller_name = 'ckanext.configpermission.controller:PermissionController'
controller_view_action = 'management_view'
controller_update_roles_action = 'update_roles'
controller_auth_update_action = 'auth_update'


class ConfigpermissionPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IRoutes)

    auth_manager = None

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'configpermission')

    # IAuthFunctions
    def get_auth_functions(self):
        # Get the permissions we're overwriting and return to the main CKAN site
        auth_data = {}
        self.auth_manager = AuthManager(permissions)
        for permission in [x['name'] for x in permissions]:
            auth_data[permission] = getattr(self.auth_manager, permission)
        return auth_data

    # IRoutes #
    def before_map(self, m):
        controller = controller_name

        m.connect('management_view', '/permissions/', action=controller_view_action,
                  controller=controller)

        m.connect('roles_update', '/permissions/update_roles', action=controller_update_roles_action,
                  controller=controller)

        m.connect('auth_update', '/permissions/auth_update', action=controller_auth_update_action,
                  controller=controller)

        return m

    def after_map(self, m):
        return m
