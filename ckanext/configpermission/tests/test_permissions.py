from ckanext.configpermission import default_roles

permissions = [{'display_name': 'Group Create', 'name': 'group_create', 'role': default_roles.SYSADMIN},
               {'display_name': 'Resource Update', 'name': 'resource_update', 'role': default_roles.MEMBER},
               {'display_name': 'Member Create', 'name': 'member_create', 'role': default_roles.EDITOR},
               {'display_name': 'Package Show', 'name': 'package_show', 'role': default_roles.ANON_USER},
               {'display_name': 'Show Resource', 'name': 'resource_show', 'role': default_roles.ANON_USER},

               ]
