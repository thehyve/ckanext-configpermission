SYSADMIN = {'name': 'sysadmin', 'rank': 10, 'org_member': True, 'is_registered': True}
EDITOR   = {'name': 'editor', 'rank': 5, 'org_member': True, 'is_registered': True}
MEMBER   = {'name': 'member', 'rank': 4, 'org_member': True, 'is_registered': True}
ADMIN    = {'name': 'admin', 'rank': 6, 'org_member': True, 'is_registered': True}
REG_USER = {'name': 'reg_user', 'rank': 1, 'org_member': False, 'is_registered': True}
ANON_USER= {'name': 'anon_user', 'rank': 0, 'org_member': False, 'is_registered': False}

all_roles = [SYSADMIN, EDITOR, MEMBER, ADMIN, REG_USER, ANON_USER]