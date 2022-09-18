from fastapi import FastAPI
import json
from sqlalchemy import create_engine
from src.utils.load_method.load_utils import register_load_method
import redis
import pysolr
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


@register_load_method
def fastapi_app() -> FastAPI:
    return FastAPI(title='Fashion Server SSSMarket',
                   description='FastAPI Server for BE.',
                   version='1.0.0'
                   )


@register_load_method
def db_engine(credential_path: str):
    with open(credential_path, 'r') as f:
        args = json.load(f)
    username, password, host, port, dbname, statement_timeout = args['username'], args['password'], args['host'], args['port'], args[
        'dbname'], args['statement_timeout']
    connection_string = f'postgresql://{username}:{password}@{host}:{port}/{dbname}'
    timeout_config_string = '-c statement_timeout=%ss' % statement_timeout
    engine = create_engine(connection_string, pool_size=50, max_overflow=120)
    return engine


@register_load_method
def redis_connection(host: str, port: int) -> redis.Redis:
    return redis.Redis(host=host, port=port)


@register_load_method
def solr_search_client(host, port, core_name):
    solr_str = '{}:{}/solr/{}/'.format(host, port, core_name)

    # init SOLR
    solr = pysolr.Solr(solr_str, search_handler='/search', use_qt_param=False)
    return solr

@register_load_method
def firebase_db_client(cred_path):
    # Fetch the service account key JSON file contents
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    firebase_db = firestore.client()
    return firebase_db