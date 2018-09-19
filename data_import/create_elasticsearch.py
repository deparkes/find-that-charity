import argparse
from elasticsearch import Elasticsearch
import os


INDEXES = [
    {
        "name": "charitysearch",
        "mapping": {
            "organisation": {
                "properties": {
                    "complete_names": {
                        "type": "completion",
                        "contexts": [
                            {
                                "name": "place_type",
                                "type": "category",
                                "path": "organisationType"
                            }
                        ]
                    }
                }
            }
        }
    }
]


def main():

    parser = argparse.ArgumentParser(description='Setup elasticsearch indexes.')
    parser.add_argument('--reset', action='store_true',
                        help='If set, any existing indexes will be deleted and recreated.')

    # elasticsearch options
    parser.add_argument('--es-host', default="localhost", help='host for the elasticsearch instance')
    parser.add_argument('--es-port', default=9200, help='port for the elasticsearch instance')
    parser.add_argument('--es-url-prefix', default='', help='Elasticsearch url prefix')
    parser.add_argument('--es-use-ssl', action='store_true', help='Use ssl to connect to elasticsearch')
    parser.add_argument('--es-index', default='charitysearch', help='index used to store charity data')

    args = parser.parse_args()

    es = Elasticsearch(host=args.es_host, port=args.es_port, url_prefix=args.es_url_prefix, use_ssl=args.es_use_ssl)

    potential_env_vars = [
        "ELASTICSEARCH_URL",
        "ES_URL",
        "BONSAI_URL"
    ]
    for e_v in potential_env_vars:
        if os.environ.get(e_v):
            es = Elasticsearch(os.environ.get(e_v))
            break

    INDEXES[0]["name"] = args.es_index

    for i in INDEXES:
        if es.indices.exists(i["name"]) and args.reset:
            print("[elasticsearch] deleting '%s' index..." % (i["name"]))
            res = es.indices.delete(index=i["name"])
            print("[elasticsearch] response: '%s'" % (res))
        if not es.indices.exists(i["name"]):
            print("[elasticsearch] creating '%s' index..." % (i["name"]))
            res = es.indices.create(index=i["name"])

        if "mapping" in i:
            for es_type, mapping in i["mapping"].items():
                res = es.indices.put_mapping(es_type, mapping, index=i["name"])
                print("[elasticsearch] set mapping on {} index (type: {})".format(i["name"], es_type))

if __name__ == '__main__':
    main()
