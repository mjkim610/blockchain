from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()

engine = create_engine('sqlite://mychain.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = scoped_session(sessionmaker(bind=engine))
session = DBSession()


def init():
    Base.metadata.create_all(engine)


def insert(obj):
    session.add(obj)
    session.commit()


def insert_or_update(obj, **kwargs):
    if session.query(obj.__class__).filter_by(**kwargs).first():
        pass
    else:
        session.add(obj)
        session.commit()


def get_all(clz):
    return session.query(clz).all()