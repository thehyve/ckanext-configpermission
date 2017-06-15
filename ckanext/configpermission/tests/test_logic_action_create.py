import unittest
import nose

from ckan import model as ckan_model
from ckan.tests import factories
import ckan.tests.helpers as helpers
import ckan

from ckanext.configpermission import model

assert_equals = nose.tools.assert_equals


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
        for member in model.AuthMember.all():
            member.delete(member.group_id, member.user_id)

    @classmethod
    def teardown_class(cls):
        '''Nose runs this method once after all the test methods in our class
        have been run.

        '''
        # We have to unload the plugin we loaded, so it doesn't affect any
        # tests that run after ours.
        ckan.plugins.unload('configpermission')

    def test_group_member_creation(self):
        """
        Based on the tests in CKAN's test_create
        """
        user = factories.User()
        group = factories.Group()

        new_membership = helpers.call_action(
            'group_member_create',
            id=group['id'],
            username=user['name'],
            role='member',
        )

        assert_equals(new_membership['group_id'], group['id'])
        assert_equals(new_membership['table_name'], 'user')
        assert_equals(new_membership['table_id'], user['id'])
        assert_equals(new_membership['capacity'], 'member')

        # Check AuthMember object is created.
        auth_member = model.AuthMember.by_group_and_user_id(group_id=group['id'], user_id=user['id'])
        assert auth_member is not None
        assert auth_member.role.name == 'member'

    def test_organization_member_creation(self):
        """
        Based on the tests in CKAN's test_create
        """
        self.teardown()
        user = factories.User()
        organization = factories.Organization()

        new_membership = helpers.call_action(
            'organization_member_create',
            id=organization['id'],
            username=user['name'],
            role='member',
        )

        assert_equals(new_membership['group_id'], organization['id'])
        assert_equals(new_membership['table_name'], 'user')
        assert_equals(new_membership['table_id'], user['id'])
        assert_equals(new_membership['capacity'], 'member')

        # Check AuthMember object is created.
        auth_member = model.AuthMember.by_group_and_user_id(group_id=organization['id'], user_id=user['id'])
        assert auth_member is not None
        assert auth_member.role.name == 'member'