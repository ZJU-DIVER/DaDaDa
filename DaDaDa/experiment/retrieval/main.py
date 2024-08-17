from elasticsearch import Elasticsearch, helpers

class Engine:
    def __init__(self) -> None:
        self.es = Elasticsearch("http://localhost:9200")
        if self.es.ping():
            print("Connected to Elasticsearch")
        else:
            print("Could not connect to Elasticsearch")
        pass

    def load_index(self,index_file,schema_file,name):
        import csv,json
        index_name = name
        if self.es.indices.exists(index=index_name):
            self.es.indices.delete(index=index_name)
        if not self.es.indices.exists(index=index_name):
            
            with open(schema_file,'r',encoding='utf-8') as sf:
                schema:dict = json.load(sf)

            self.es.indices.create(
                index=index_name,
                body=schema
            )
            print("Index created!")
        items = []
        from util import handle_row
        with open(index_file,'r',encoding='utf-8') as inf:
            reader = csv.DictReader(inf)
            for row in reader:
                items.append(handle_row(row))
        actions = [
            {
                "_index": index_name,
                "_source": doc
            }
            for doc in items
        ]
        helpers.bulk(self.es, actions)
        

    def delete_doc(self,index_name):
        delete_query = {
            "query": {
                "match_all": {}
            }
        }
        self.es.delete_by_query(index=index_name, body=delete_query)
es = Engine()
# es.delete_doc('data_market')
es.load_index('../../data/final_data.csv','./index_schema.json','data_market')