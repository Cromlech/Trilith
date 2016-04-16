# -*- coding: utf-8 -*-

from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, Text, ForeignKey, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """User
    """
    __tablename__ = 'users'
    
    id = Column(String(128), primary_key=True)
    common_name = Column(String(128))
    function = Column(String(128))


class Client(Base):
    """Client : may be linked to a User or stand alone.
    """
    __tablename__ = 'clients'
    
    id = Column(String(40), primary_key=True)
    name = Column(String(40), unique=True)
    type = Enum('public', 'confidential')
    secret = Column(String(55))
    user_id = Column(ForeignKey(User.id), nullable=True)
    redirections = Column(Text)
    default_target_scopes = Column(Text)

    # Relationships
    user = relationship('User')

    @property
    def redirect_uris(self):
        if self.redirections:
            return self.redirections.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self.default_target_scopes:
            return self.default_target_scopes.split()
        return []


class Grant(Base):
    __tablename__ = 'grants'
    
    # Identity
    id = Column(Integer, primary_key=True)

    # Affiliation
    client_id = Column(String(40), ForeignKey(Client.id))
    user_id = Column(
        String(128), ForeignKey(User.id, ondelete='CASCADE'), nullable=True)

    # Destination
    redirect_uri = Column(String(255))

    # Restrictions
    code = Column(String(255), index=True, nullable=True)
    expires = Column(DateTime)
    allowed_scopes = Column(Text)

    # relationships
    client = relationship('Client')
    user = relationship('User')

    @property
    def scopes(self):
        if self.allowed_scopes:
            return self.allowed_scopes.split()
        return []


class Token(Base):
    __tablename__ = 'tokens'
    
    # Identity
    id = Column(Integer, primary_key=True)
    type = Enum('Bearer', 'MAC')
    access_token = Column(String(255), unique=True)
    refresh_token = Column(String(255), unique=True)

    # Affiliation
    client_id = Column(String(40), ForeignKey(Client.id))
    user_id = Column(String(128), ForeignKey(User.id), nullable=True)

    # Restrictions
    expires = Column(DateTime)
    allowed_scopes = Column(Text)

    # relationships
    client = relationship('Client')
    user = relationship('User')

    @property
    def scopes(self):
        if self.allowed_scopes:
            return self.allowed_scopes.split()
        return []
