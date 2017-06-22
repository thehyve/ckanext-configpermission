import unittest

from ckanext.configpermission.tests.test_permissions import permissions
from ckanext.configpermission import model

import ckan
from ckan.tests import factories
from ckan import model as ckan_model

model.create_tables()

org1_name = 'configpermission_test_org'
org2_name = 'configpermission_test_org2'
user1_name = 'configpermission_test_user1'


class TestAuthManager(unittest.TestCase):
    '''Tests for the ckanext.configpermission.model module.

    Specifically tests that overriding parent auth functions will cause
    child auth functions to use the overridden version.
    '''
    @classmethod
    def setup_class(cls):
        '''Nose runs this method once to setup our test class.'''
        # Test code should use CKAN's plugins.load() function to load plugins
        # to be tested.
        # Use the testpermissions instead of the default
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

    def clear_data(self):
        for auth in model.AuthModel.all():
            auth.delete(auth.name)
        for role in model.AuthRole.all():
            role.delete(role.name)
        for member in model.AuthMember.all():
            member.delete(member.group_id, member.user_id)

    def add_test_data(self):
        self.clear_data()
        model.create_default_data(permissions=permissions)
        # Creates the data we use in the tests.
        org1 = ckan_model.Group.get(org1_name)
        user1 = ckan_model.User.get(user1_name )
        if org1 is None:
            if user1 is None:
                user1 = factories.User(name=user1_name)
            factories.Organization(name=org1_name, users=[user1])
            org1 = ckan_model.Group.get(org1_name)

    def test_AuthRoleAuthModel(self):
        self.add_test_data()
        model.AuthRole.delete('test_role')
        assert model.AuthRole.get('test_role') is None
        model.AuthRole.create(name='test_role', rank=1000)
        auth_role = model.AuthRole.get(name='test_role')
        assert auth_role is not None
        assert auth_role.name == 'test_role'
        assert auth_role.rank == 1000

        auth_role.rank = 2000
        auth_role.save()
        role_check = model.AuthRole.get(name='test_role')
        assert role_check is not None
        assert role_check.name == 'test_role'
        assert role_check.rank == 2000

        model.AuthModel.delete('test_model')
        model.AuthModel.delete('test_model2')
        assert model.AuthModel.get('test_model') is None

        model.AuthModel.create(name='test_model', min_role=role_check, display_name='Test Model')
        auth_model = model.AuthModel.get(name='test_model')
        assert auth_model is not None
        assert auth_model.name == 'test_model'
        assert auth_model.min_role == role_check

        auth_model.name = 'test_model2'
        auth_model.save()
        model_check = model.AuthModel.get('test_model2')
        assert model_check is not None
        assert model_check.min_role == role_check
        assert model_check.id == auth_model.id

        user1 = ckan_model.User.get(user1_name)
        org1 = ckan_model.Group.get(org1_name)
        model.AuthMember.delete(group_id=org1.id, user_id=user1.id)
        assert model.AuthMember.by_user_id(user_id=user1.id) == []
        assert len(model.AuthMember.by_group_id(group_id=org1.id)) == 0

        model.AuthMember.create(user_id=user1.id, group_id=org1.id, role=auth_role)
        member = model.AuthMember.by_group_and_user_id(group_id=org1.id, user_id=user1.id)
        assert member is not None
        assert member.group_id == org1.id
        assert member.user_id == user1.id

        model.AuthMember.delete(group_id=org1.id, user_id=user1.id)
        assert model.AuthMember.by_group_and_user_id(group_id=org1.id, user_id=user1.id) is None

        all = set([x.name for x in model.AuthModel.all()])
        default = set([x['name'] for x in permissions])
        default.add('test_model2')
        assert all == default

