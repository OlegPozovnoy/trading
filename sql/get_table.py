from sqlalchemy import create_engine
import logging

engine = create_engine('postgresql://postgres:postgres@localhost:5432/test')
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def exec_query(query):
    #print("engine:", id(engine))
    return engine.execute(query)
