# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from logging import getLogger
from scrapy.exceptions import DropItem

class BaseMongoPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_db = mongo_db
        self.mongo_uri = mongo_uri

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        self.db[item.collection].insert(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()

class MongoPipeline(BaseMongoPipeline):
    def process_item(self, item, spider):
        self.db[item.collection].insert(dict(item))
        return item

class DupProductPipeline(BaseMongoPipeline):
    def __init__(self, mongo_uri, mongo_db):
         BaseMongoPipeline.__init__(self, mongo_uri, mongo_db)
         self.logger = getLogger(__name__)

    def process_item(self, item, spider):
        # 商品名称，店铺，价格一致视为同一商品
        condition = {
            'title': item['title'],
            'shop': item['shop'],
            'price': item['price']
        }
        if self.db[item.collection].find_one(condition):
            self.logger.debug(f'已存在：{item["title"]}')
            raise DropItem(f'已存储该商品: {item["title"]}')
        else:
            return item

