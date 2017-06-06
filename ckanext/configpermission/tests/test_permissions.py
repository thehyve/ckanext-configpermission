from ckanext.configpermission import default_roles

permissions = [{'name': 'group_create', 'role': default_roles.SYSADMIN},
               {'name': 'resource_update', 'role': default_roles.MEMBER},
               {'name': 'member_create', 'role': default_roles.EDITOR},
               {'name': 'package_show', 'role': default_roles.ANON_USER}]
