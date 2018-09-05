from ckan.logic.action.get import package_search as ckan_package_search
import ckan.model as ckan_model
from ckanext.configpermission.model import AuthMember
from ckan.lib import helpers as h
from logging import getLogger
log = getLogger(__name__)


def package_search(context, data_dict):
    log.debug("context: {}".format(context))
    log.debug("data_dict: {}".format(data_dict))

    user = context.get('auth_user_obj', None)
    if user is None:
        user_name = context.get('user', '')
        user = ckan_model.User.get(user_name)

    if h.check_access('list_packages', data_dict=data_dict):
        if user is not None:
            context['ignore_capacity_check'] = True

            if data_dict.get('q', '') != '':
                q_split = data_dict['q'].split(' ')

                query = " ".join([x for x in q_split if ':' not in x])
                rest = " ".join([x for x in q_split if ':' in x])
                data_dict['fq'] += rest
                data_dict['q'] = query
            if user.sysadmin:
                data_dict['fq'] += ' +capacity:("private" OR "public")'
            else:
                memberships = AuthMember.by_user_id(user.id)
                org_names = [ckan_model.Group.get(x.group_id).name for x in memberships if x.role.org_member == True]

                org_filters = ['OR filter(capacity:"private" AND organization:{})'.format(x) for x in org_names]

                filters = " ".join(org_filters)
                data_dict['fq'] += '(capacity:"public" {})'.format(filters)

        log.debug("User fq: {}".format(data_dict['fq']))
        results = ckan_package_search(context=context, data_dict=data_dict)
    else:
        results = {}
        results['count'] = 0
        results['results'] = []
        results['facets'] = {}
        results['search_facets'] = {}
        results['sort'] = ''

    return results