from ckanext.configpermission import model

from ckan.tests import factories
from ckan import model as ckan_model
model.create_tables()

org1_name = 'configpermission_test_org'
user1_name = 'configpermission_test_user1'


def add_test_data():
    ckan_model.repo.rebuild_db()
    # Creates the data we use in the tests.
    org1 = ckan_model.Group.get(org1_name)
    user1 = ckan_model.User.get(user1_name )
    if org1 is None:
        if user1 is None:
            user1 = factories.User(name=user1_name)
        factories.Organization(name=org1_name, users=[user1])
        org1 = ckan_model.Group.get(org1_name)


def test_AuthRoleAuthModel():
    add_test_data()

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

    model.AuthModel.create(name='test_model', min_role=role_check)
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
    assert model.AuthMember.by_group_id(group_id=org1.id) == []

    model.AuthMember.create(user_id=user1.id, group_id=org1.id, role=auth_role)
    member = model.AuthMember.by_group_and_user_id(group_id=org1.id, user_id=user1.id)
    assert member is not None
    assert member.group_id == org1.id
    assert member.user_id == user1.id

    model.AuthMember.delete(group_id=org1.id, user_id=user1.id)
    assert model.AuthMember.by_group_and_user_id(group_id=org1.id, user_id=user1.id) is None

    all = set([x.name for x in model.AuthModel.all()])

    assert all == {u'package_show', u'resource_create', u'group_create', 'test_model2',
                   u'resource_show', u'member_create', u'resource_update'}

    # Cleanup
    model.AuthModel.delete('test_model')
    model.AuthModel.delete('test_model2')
    model.AuthRole.delete('test_role')