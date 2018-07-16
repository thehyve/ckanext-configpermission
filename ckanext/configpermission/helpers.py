from ckanext.configpermission.model import AuthMember
from ckan.model import User, Group, Resource, Package, meta
from jinja2.runtime import Undefined
from ckan import logic

get_action = logic.get_action


def get_role(user_id, group_id):
    if type(user_id) == Undefined:
        user_id = None
    if type(group_id) == Undefined:
        group_id = None
    member = AuthMember.by_group_and_user_id(group_id=group_id, user_id=user_id)
    if member is None or member.role is None:
        return 'N/A'
    return member.role.display_name


def get_role_selected(user_id, group_id):
    if type(user_id) == Undefined:
        user_id = None
    if type(group_id) == Undefined:
        group_id = None

    member = AuthMember.by_group_and_user_id(group_id=group_id, user_id=user_id)
    if member is None or member.role is None:
        return ''
    else:
        return member.role.name


def get_package_count(c, organization):
    user = User.get(c.user)

    member = AuthMember.by_group_and_user_id(group_id=organization['id'], user_id=user.id)

    if (member is None or member.role is None) and not user.sysadmin:
        return meta.Session.query(Package).filter_by(owner_org=organization['id'], state='active', private=False).count()
    else:
        return meta.Session.query(Package).filter_by(owner_org=organization['id'], state='active').count()


def get_resource_count():
    stats = get_site_extra_statistics()
    total = 0
    for org, data in stats.iteritems():
        total += data[1]
    return total


def get_asset_count():
    stats = get_site_extra_statistics()
    total = 0
    for org, data in stats.iteritems():
        total += data[0]
    return total


def get_org_count():
    stats = get_site_extra_statistics()
    total = 0
    for org, data in stats.iteritems():
        total += 1
    return total


def get_site_extra_statistics():
    orgs = Group.all("organization")
    org_data = {}
    all_assets = list(meta.Session.query(Package).all())
    for org in orgs:
        org_data[org.display_name] = {}
        # assets = [x for x in all_assets if (x.owner_org == org.id) and (x.state == 'active')]
        assets = meta.Session.query(Package).filter_by(owner_org=org.id, state='active').all()
        asset_count = 0
        resource_count = 0
        for asset in assets:
            asset_count += 1
            resource_count += len(asset.resources)

        org_data[org.display_name] = (asset_count, resource_count)

    return org_data

