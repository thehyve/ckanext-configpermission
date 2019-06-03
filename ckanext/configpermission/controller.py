import json
import re

from ckan.lib.base import BaseController, render, abort
from ckan.common import request, _
from ckan import model as ckan_model

from ckanext.configpermission import model
from ckanext.configpermission.model import AuthModel, AuthRole
from ckanext.configpermission.default_permissions import permissions


class PermissionController(BaseController):

    def check_sysadmin(self):
        """
        Checks if a user is a sysadmin, throws 404 error if not
        :return:
        """
        user_name = request.remote_user

        if user_name is None:
            return abort(401, _('No user logged in'))
        user = ckan_model.User.get(user_name)
        if user is None:
            return abort(401, _('Only logged in sysadmin can do this'))
        if not user.sysadmin:
            return abort(403, _('Only sysadmin can do this'))

    def management_view(self):
        self.check_sysadmin()
        roles = AuthRole.all()
        roles.sort(key=lambda x: x.rank, reverse=True)

        models = AuthModel.all()
        # Only show the models selected via the ckan config option.
        models = [x for x in models if x.name in [y['name'] for y in permissions]]
        models.sort(key=lambda x: x.name)

        return render("configpermission/configpermission_management.html",
                      extra_vars={'models': models, 'roles': roles})

    def update_roles(self):
        """
            PUT /users/id: Update an existing item.
            @param role_data the role data to be updated
        """
        roles = json.loads(request.POST['data'])
        self.check_sysadmin()
        new_roles = [x['name'] for x in roles]

        for role in model.AuthRole.all():
            if role.name not in new_roles:

                model.AuthRole.delete(name=role.name)

        new_roles = [x for x in roles if x['name'] == 'not_set']
        old_roles = [x for x in roles if x['name'] != 'not_set']

        for role in old_roles:
            old_role = model.AuthRole.get(name=role['name'])
            if not old_role or not old_role.editable:
                continue
            else:
                old_role.rank = role['rank']
            old_role.save()

        for role in new_roles:
            role['name'] = clean_str(role['display_name'])
            role['org_member'] = True
            role['editable'] = True

            new_role = model.AuthRole.create(**role)

        return {}

    def auth_update(self):
        self.check_sysadmin()
        for auth_model, auth_role in request.POST.items():
            auth = model.AuthModel.get(name=auth_model)
            role = model.AuthRole.get(name=auth_role)

            auth.min_role = role
            auth.save()
        return


def clean_str(string):
    """
        Tokenization/string cleaning
        Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    string = re.sub(r" ", "_", string)
    return string.strip().lower()