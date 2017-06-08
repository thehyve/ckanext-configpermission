from ckan.lib.base import BaseController, render
from ckanext.configpermission.model import AuthModel, AuthRole


class PermissionController(BaseController):

    def management_view(self):
        roles = AuthRole.all()
        roles.sort(key=lambda x: x.rank, reverse=True)
        return render("configpermission/management.html",
                      extra_vars={'models': AuthModel.all(), 'roles': roles})