SYSADMIN = {'display_name': 'Sysadmin', 'name': 'sysadmin', 'rank': 10, 'org_member': True, 'is_registered': True, 'editable': False}
EDITOR   = {'display_name': 'Org Editor', 'name': 'editor', 'rank': 5, 'org_member': True, 'is_registered': True, 'editable': True,}
MEMBER   = {'display_name': 'Org Member', 'name': 'member', 'rank': 4, 'org_member': True, 'is_registered': True, 'editable': True,}
ADMIN    = {'display_name': 'Org Admin', 'name': 'admin', 'rank': 6, 'org_member': True, 'is_registered': True, 'editable': True,}
REG_USER = {'display_name': 'Registered User', 'name': 'reg_user', 'rank': 1, 'org_member': False, 'is_registered': True, 'editable': False}
ANON_USER= {'display_name': 'Anonymous User', 'name': 'anon_user', 'rank': 0, 'org_member': False, 'is_registered': False, 'editable': False}

all_roles = [SYSADMIN, EDITOR, MEMBER, ADMIN, REG_USER, ANON_USER]