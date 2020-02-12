import pygame
from uuid import uuid4
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base, declared_attr

def new_guid():
    return str(uuid4()).replace('-', '')

class Object(object):
    pass

class Base(Object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    guid = Column(String(32), primary_key=True, default=new_guid)
Base = declarative_base(cls=Base)

def oppose(x):
    return 0 if x else 1

def recursive_defaultdict():
    return defaultdict(recursive_defaultdict)