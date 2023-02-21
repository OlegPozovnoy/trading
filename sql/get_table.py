from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/test')


def exec_query(query):
    return engine.execute(query)
