from ckan.lib.base import BaseController, render
from ckanext.configpermission.model import AuthModel, AuthRole


class PermissionController(BaseController):

    def management_view(self):

        return render("configpermission/management.html",
                      extra_vars={'models': AuthModel.all(), 'roles': AuthRole.all()})