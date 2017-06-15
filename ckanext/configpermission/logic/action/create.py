from ckan import logic
from ckan.common import _
import ckan
import ckan.lib.dictization.model_dictize as model_dictize
from ckanext.configpermission.model import AuthMember, AuthRole

NotFound = logic.NotFound
_get_or_bust = logic.get_or_bust
_check_access = logic.check_access


def member_create(context, data_dict=None):
    '''Make an object (e.g. a user, dataset or group) a member of a group.

    If the object is already a member of the group then the capacity of the
    membership will be updated.

    You must be authorized to edit the group.

    :param id: the id or name of the group to add the object to
    :type id: string
    :param object: the id or name of the object to add
    :type object: string
    :param object_type: the type of the object being added, e.g. ``'package'``
        or ``'user'``
    :type object_type: string
    :param capacity: the capacity of the membership
    :type capacity: string

    :returns: the newly created (or updated) membership
    :rtype: dictionary

    '''
    model = context['model']
    user = context['user']

    rev = model.repo.new_revision()
    rev.author = user
    if 'message' in context:
        rev.message = context['message']
    else:
        rev.message = _(u'REST API: Create member object %s') \
            % data_dict.get('name', '')

    group_id, obj_id, obj_type, capacity = \
        _get_or_bust(data_dict, ['id', 'object', 'object_type', 'capacity'])

    group = model.Group.get(group_id)
    if not group:
        raise NotFound('Group was not found.')

    obj_class = ckan.logic.model_name_to_class(model, obj_type)
    obj = obj_class.get(obj_id)
    if not obj:
        raise NotFound('%s was not found.' % obj_type.title())

    _check_access('member_create', context, data_dict)

    # Look up existing, in case it exists
    member = model.Session.query(model.Member).\
        filter(model.Member.table_name == obj_type).\
        filter(model.Member.table_id == obj.id).\
        filter(model.Member.group_id == group.id).\
        filter(model.Member.state == 'active').first()
    if not member:
        member = model.Member(table_name=obj_type,
                              table_id=obj.id,
                              group_id=group.id,
                              state='active')

    member.capacity = capacity

    model.Session.add(member)
    model.repo.commit()

    # New code to add AuthMember objects
    if obj_type == 'user':
        roles = [x for x in AuthRole.all() if x.org_member]
        roles.sort(key=lambda x: x.rank)
        lowest_role = roles[0]

        AuthMember.create(group_id=group.id, user_id=obj_id, role=lowest_role)

    return model_dictize.member_dictize(member, context)