import json

from utils.connectors import FactoryConnection


with FactoryConnection().get_connection('es')() as es_conn:
    if not es_conn.indices.exists(index='products'):
        with open('es_index.json', 'r') as file:
            data = json.load(file)
        es_conn.indices.create(index='products',
                               settings=data.get('settings'),
                               mappings=data.get('mappings'))

    data = es_conn.indices.get(index='products')
