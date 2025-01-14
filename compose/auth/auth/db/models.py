from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import CreatedModel, ModifiedModel

 
class UserModel(CreatedModel, ModifiedModel):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth'}
    
    login = Column(String(64), nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)

    roles = relationship(
        'UserRoleModel',
        back_populates='user',
        cascade='all, delete-orphan')
    login_history = relationship(
        'LoginHistoryModel',
        back_populates='user',
        cascade='all, delete-orphan')


class RoleModel(CreatedModel, ModifiedModel):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'auth'}
    
    name = Column(String(64), nullable=False, unique=True)
    
    users_roles = relationship(
        'UserRoleModel',
        back_populates='role',
        cascade='all, delete-orphan')


class UserRoleModel(CreatedModel):
    __tablename__ = 'users_roles'
    __table_args__ = {'schema': 'auth'}
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('auth.users.id', ondelete='CASCADE'),
        nullable=False)
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey('auth.roles.id', ondelete='CASCADE'),
        nullable=False)
    
    user = relationship('UserModel', back_populates='roles')
    role = relationship('RoleModel', back_populates='users_roles')


class LoginHistoryModel(CreatedModel):
    __tablename__ = 'login_history'
    __table_args__ = {'schema': 'auth'}
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('auth.users.id', ondelete='CASCADE'),
        nullable=False)
    user_agent = Column(Text, nullable=False)
    
    user = relationship('UserModel', back_populates='login_history')