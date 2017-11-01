from ckan.logic.action.get import package_search as ckan_package_search
from ckan.lib import helpers as h


def package_search(context, data_dict):
    if h.check_access('list_packages', data_dict=data_dict):
        results = ckan_package_search(context=context, data_dict=data_dict)
    else:
        results = {}
        results['count'] = 0
        results['results'] = []
        results['facets'] = {}
        results['search_facets'] = {}
        results['sort'] = ''

    return results