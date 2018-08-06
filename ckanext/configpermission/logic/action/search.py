from ckan.logic.action.get import package_search as ckan_package_search
import ckan.model as ckan_model
from ckanext.configpermission.model import AuthMember
from ckan.lib import helpers as h


def package_search(context, data_dict):
    # import pdb; pdb.set_trace()
    if h.check_access('list_packages', data_dict=data_dict):
        user = context.get('auth_user_obj', None)
        if user is not None:
            context['ignore_capacity_check'] = True
            if user.sysadmin:
                data_dict['fq'] = ' +capacity:("private" OR "public")'
            else:
                memberships = AuthMember.by_user_id(user.id)
                org_names = [ckan_model.Group.get(x.group_id).name for x in memberships if x.role.org_member == True]

                org_filters = ['OR filter(capacity:"private" AND organization:{})'.format(x) for x in org_names]

                filters = " ".join(org_filters)
                data_dict['fq'] += '(capacity:"public" {})'.format(filters)

        results = ckan_package_search(context=context, data_dict=data_dict)
    else:
        results = {}
        results['count'] = 0
        results['results'] = []
        results['facets'] = {}
        results['search_facets'] = {}
        results['sort'] = ''

    return results