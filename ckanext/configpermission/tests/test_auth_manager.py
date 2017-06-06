from ckanext.configpermission.auth_manager import AuthManager
from ckanext.configpermission import model, default_roles
from ckanext.configpermission.tests.test_permissions import permissions

import ckan
from ckan.logic import check_access, NotAuthorized
from ckan import model as ckan_model
from ckan.tests import factories
import unittest

manager = AuthManager(permissions)

auth_test_sysadmin = 'auth_test_sysadmin'
auth_test_normal   = 'auth_test_normal'
auth_test_editor   = 'auth_test_editor'

auth_test_resource = 'auth_test_resource'
auth_test_dataset  = 'auth_test_dataset'
auth_test_org      = 'auth_test_org'


class TestAuthManager(unittest.TestCase):
    '''Tests for the ckanext.example_iauthfunctions.plugin module.

    Specifically tests that overriding parent auth functions will cause
    child auth functions to use the overridden version.
    '''
    @classmethod
    def setup_class(cls):
        '''Nose runs this method once to setup our test class.'''
        # Test code should use CKAN's plugins.load() function to load plugins
        # to be tested.
        # Use the testpermissions instead of the default
        from ckanext.configpermission import plugin
        plugin.permissions = permissions
        ckan.plugins.load('configpermission')

    def teardown(self):
        '''Nose runs this method after each test method in our test class.'''
        # Rebuild CKAN's database after each test method, so that each test
        # method runs with a clean slate.
        ckan_model.repo.rebuild_db()

    @classmethod
    def teardown_class(cls):
        '''Nose runs this method once after all the test methods in our class
        have been run.

        '''
        # We have to unload the plugin we loaded, so it doesn't affect any
        # tests that run after ours.
        ckan.plugins.unload('configpermission')

    def create_test_data(self):
        ckan_model.repo.rebuild_db()
        model.create_tables()
        model.create_default_data(permissions=permissions)

        org = factories.Organization(name=auth_test_org)

        pkg = factories.Dataset(name=auth_test_dataset, owner_org=org.get('id'))
        resource = factories.Resource(package_name=pkg.get('id'), name=auth_test_resource, owner_org=org.get('id'))

        normal_user = factories.User(name=auth_test_normal, sysadmin=False)
        role = model.AuthRole.get(name=default_roles.MEMBER['name'])
        model.AuthMember.create(user_id=normal_user['id'], group_id=org['id'], role=role)

        editor_user = factories.User(name=auth_test_editor, sysadmin=False)
        role = model.AuthRole.get(name=default_roles.EDITOR['name'])
        model.AuthMember.create(user_id=editor_user['id'], group_id=org['id'], role=role)

        factories.User(name=auth_test_sysadmin, sysadmin=True)

    def test_sysadmin_role(self):
        self.create_test_data()
        context = {'model': ckan_model,
                   'user': auth_test_sysadmin}
        assert check_access(action='group_create', context=context, data_dict={})

    def test_basic_role(self):
        self.create_test_data()
        context = {'model': ckan_model, 'user': auth_test_normal, 'resource': ckan_model.Resource.get(auth_test_resource)}

        assert check_access(action='resource_show', context=context, data_dict={})

        context = {'model': ckan_model, 'user': None,
                   'resource': ckan_model.Resource.get(auth_test_resource)}

        # We removed the user so this should throw a not authorized error.
        self.assertRaises(NotAuthorized, check_access, action='resource_update', context=context, data_dict={})

    def test_anon_user(self):
        self.create_test_data()

        context = {'model': ckan_model, 'user': None}
        # Package show should be accesible to anon users.
        assert check_access(action='package_show', context=context, data_dict={})

    def test_editoronly_access(self):
        self.create_test_data()
        group = ckan_model.Group.get(auth_test_org)
        context = {'model': ckan_model, 'user': auth_test_editor, 'group': group}

        assert check_access(action='member_create', context=context, data_dict={})

        context = {'model': ckan_model, 'user': auth_test_normal, 'group': group}

        self.assertRaises(NotAuthorized, check_access, action='member_create', context=context, data_dict={})