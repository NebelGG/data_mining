# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from pymongo import MongoClient


class GbParsePipeline:
    def __init__(self):
        self.db = MongoClient()['parse_13']

    def process_item(self, item, spider):
        # collection = self.db[spider.name]
        # collection.insert_one(item)
        return item

    def item_completed(self, results, item, info):
        # item['img'] = [itm[1] for itm in results]
        print(results)
        print(item)
        print(info)

        return item