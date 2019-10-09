from sqlalchemy import create_engine, Table, Column, Integer, String, ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
Base = declarative_base()
metadata = MetaData()

pages = Table('pages', metadata,
              Column('id', String(36), primary_key=True),
              Column('url', String),
              Column('request_depth', Integer)
              )

relations = Table('relations', metadata,
                  Column('from_page_id', String(36), ForeignKey("pages.id")),
                  Column('link_id', String(36), ForeignKey("pages.id")))


def on_start_db():
    engine = create_engine("sqlite:///crawl.db")
    metadata.create_all(engine)
    session = sessionmaker()
    session.configure(bind=engine)
    return engine, session