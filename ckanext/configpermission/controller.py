from ckan.lib.base import BaseController, render
from ckanext.configpermission.model import AuthModel, AuthRole
from ckan.common import request, _
from ckan import model as ckan_model
from ckan.lib.base import abort
from ckanext.configpermission import model
import json
import re


class PermissionController(BaseController):

    def management_view(self):
        roles = AuthRole.all()
        roles.sort(key=lambda x: x.rank, reverse=True)
        return render("configpermission/management.html",
                      extra_vars={'models': AuthModel.all(), 'roles': roles})

    def update_roles(self):
        """PUT /users/id: Update an existing item.
           @param role_data the role data to be updated
        """
        roles = json.loads(request.POST['data'])
        user_name = request.remote_user

        if user_name is None:
            return abort(404, _('No user found'))
        user = ckan_model.User.get(user_name)
        if user is None or not user.sysadmin:
            return abort(404, _('Only sysadmin may do this'))

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
    return string.strip().lower()