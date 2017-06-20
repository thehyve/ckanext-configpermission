import unittest
import ckan
from ckanext.configpermission.logic.action import get

class TestAuthManager(unittest.TestCase):
    '''Tests for the ckanext.configpermission.logic.action.get module.

    Specifically tests that overriding parent auth functions will cause
    child auth functions to use the overridden version.
    '''
    @classmethod
    def setup_class(cls):
        '''Nose runs this method once to setup our test class.'''
        # Test code should use CKAN's plugins.load() function to load plugins
        # to be tested.
        ckan.plugins.load('configpermission')

    def teardown(self):
        '''Nose runs this method after each test method in our test class.'''
        # Rebuild CKAN's database after each test method, so that each test
        # method runs with a clean slate.
        ckan.model.repo.rebuild_db()

    @classmethod
    def teardown_class(cls):
        '''Nose runs this method once after all the test methods in our class
        have been run.

        '''
        # We have to unload the plugin we loaded, so it doesn't affect any
        # tests that run after ours.
        ckan.plugins.unload('configpermission')

    def test_member_role(self):
        assert set(get.member_roles_list()) == {u'test_role', u'sysadmin', u'editor', u'member', u'admin', u'reg_user', u'anon_user'}