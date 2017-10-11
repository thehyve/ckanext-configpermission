from __future__ import absolute_import, print_function, unicode_literals

import logging

from sqlalchemy import Column, ForeignKey, types, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from ckan.lib.base import model
from ckan.model import meta

from ckanext.configpermission import default_roles

Base = declarative_base()
log = logging.getLogger(__name__)
AUTH_TABLE_NAME = 'ckanext_configpermission_model'
ROLE_TABLE_NAME = 'ckanext_configpermission_role'
MEMBER_TABLE_NAME = 'ckanext_configpermission_member'


class AuthBase(object):
    id = Column(types.INTEGER, primary_key=True)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        meta.Session.add(instance)
        meta.Session.commit()
        return instance

    @classmethod
    def all(cls):
        query = meta.Session.query(cls).autoflush(False)
        return query.all()

    def save(self):
        meta.Session.commit()


class AuthNamedBase(AuthBase):
    name = Column(types.UnicodeText, unique=True)

    @classmethod
    def get(cls, name):
        query = meta.Session.query(cls).autoflush(False)
        query = query.filter(cls.name == name)
        return query.first()

    @classmethod
    def delete(cls, name):
        if cls.get(name) is not None:
            c = meta.Session.query(cls).filter(cls.name == name).delete()
            return True
        else:
            return False


class AuthRole(AuthNamedBase, Base):
    """
    Used to store a (user defined) role.
    """
    __tablename__ = ROLE_TABLE_NAME

    rank = Column(types.INTEGER, autoincrement=False)
    org_member = Column(types.Boolean, default=False)
    is_registered = Column(types.BOOLEAN, default=True)
    editable = Column(types.BOOLEAN, default=False)
    display_name = Column(types.STRINGTYPE, unique=True)

    def __repr__(self):
        return "AuthRole(id={}, name={}, rank={}, org_member={})".format(self.id, self.name, self.rank, self.org_member)

    @classmethod
    def delete(cls, name):
        role = cls.get(name)
        if role == None:
            raise NameError("Role not known")

        lower_roles = [x for x in AuthRole.all() if x.rank < role.rank]
        lower_roles.sort(key=lambda x: x.rank, reverse=True)
        new_role = lower_roles[0]

        for member in AuthMember.by_role_id(role.id):
            member.role = new_role
            member.save()
        super(AuthRole, cls).delete(name)


class AuthModel(AuthNamedBase, Base):
    """
    Used to store the permission settings for a single action
    """
    __tablename__ = AUTH_TABLE_NAME

    display_name = Column(types.STRINGTYPE, nullable=False)
    min_role_id = Column(ForeignKey("{}.id".format(ROLE_TABLE_NAME), onupdate="CASCADE", ondelete="SET NULL"), nullable=True)
    min_role = relationship("AuthRole", order_by="{}.id".format("AuthRole"))

    def __repr__(self):
        return "AuthModel(id={}, name={}, min_role={})".format(self.id, self.name, self.min_role_id)


class AuthMember(AuthBase, Base):
    __tablename__ = MEMBER_TABLE_NAME

    role_id = Column(ForeignKey("{}.id".format(ROLE_TABLE_NAME), onupdate="CASCADE", ondelete="SET NULL"), nullable=True)
    role = relationship("AuthRole", order_by="{}.id".format("AuthRole"))

    user_id = Column(types.UnicodeText)

    group_id = Column(types.UnicodeText)

    __table_args__ = (UniqueConstraint('user_id', 'group_id', name='user_group_const'), )

    def __repr__(self):
        return "AuthMember(id={}, user_id={}, role={}, group_id={})".format(self.id, self.user_id, self.role, self.group_id)

    @classmethod
    def by_user_id(cls, user_id):
        query = meta.Session.query(cls).autoflush(False)
        query = query.filter(cls.user_id == user_id)
        return query.all()

    @classmethod
    def by_role_id(cls, role_id):
        query = meta.Session.query(cls).autoflush(False)
        query = query.filter(cls.role_id == role_id)
        return query.all()

    @classmethod
    def by_group_id(cls, group_id):
        query = meta.Session.query(cls).autoflush(False)
        query = query.filter(cls.group_id == group_id)
        return query.all()

    @classmethod
    def by_group_and_user_id(cls, group_id, user_id):
        query = meta.Session.query(cls).autoflush(False)
        query = query.filter(cls.group_id == group_id).filter(cls.user_id == user_id)
        return query.first()

    @classmethod
    def delete(cls, group_id, user_id):
        if cls.by_group_and_user_id(group_id, user_id) is not None:
            c = meta.Session.query(cls).filter(cls.group_id == group_id).filter(cls.user_id == user_id).delete()
            return True
        else:
            return False


def create_tables():
    Base.metadata.create_all(model.meta.engine )


def create_default_data(permissions, roles=default_roles.all_roles, overwrite=False):
    auth_roles = {}
    for role in roles:
        role_model = AuthRole.get(role['name'])
        if role_model is None:
            role_model = AuthRole.create(**role)
        elif overwrite and role_model.rank != role['rank']:
            role_model.rank = role['rank']
            role_model.save()
        auth_roles[role['name']] = role_model

    for permission in permissions:
        auth_model = AuthModel.get(name=permission['name'])
        if auth_model is None:
            AuthModel.create(name=permission['name'],
                             min_role=auth_roles[permission['role']['name']],
                             display_name=permission['display_name'])


def create_members():
    """
    Create AuthMember objects based on all existing memberships. Assumes create_default_data has been run and all default roles are created already
    """
    query = meta.Session.query(model.Member).autoflush(False)

    for member in query.all():
        if not member.group.is_organization or member.table_name != 'user':
            continue
        role = AuthRole.get(member.capacity)
        group_id = member.group.id
        user_id = member.table_id

        authmember = AuthMember.by_group_and_user_id(group_id=group_id, user_id=user_id)
        if authmember is None:
            AuthMember.create(user_id=user_id, role=role, group_id=group_id)

