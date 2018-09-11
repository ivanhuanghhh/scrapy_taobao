# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from scrapytaobao.items import ProductItem

class TaobaoSpider(Spider):
    name = 'taobao'
    allowed_domains = ['www.taobao.com']
    base_url = 'https://s.taobao.com/search'

    def start_requests(self):
        for key in self.settings.get('KEYWORDS'):
            for page in range(1, self.settings.get('MAX_PAGE') + 1):
                url = self.get_url(page, key)
                yield Request(url, callback=self.parse, meta={'page': page})

    def get_url(self, page, keyword):
        product_count_per_page = 44
        start = (page - 1) * product_count_per_page
        return f'{self.base_url}?q={keyword}&s={start}'

    def parse(self, response):
        products = response.xpath(
            '//div[@id="mainsrp-itemlist"]//div[@class="items"][1]//div[contains(@class, "item")]')
        for product in products:
            item = ProductItem()
            item['price'] = product.css('.price strong::text').extract_first()
            item['title'] = ''.join(product.xpath('.//div[contains(@class, "title")]//text()').extract()).strip()
            item['shop'] = product.css('.shop .shopname > span:nth-child(2)::text').extract_first()
            item['image'] = ''.join(product.xpath('.//div[@class="pic"]//img[contains(@class, "img")]/@data-src').extract()).strip()
            item['deal'] = product.xpath('.//div[contains(@class, "deal-cnt")]//text()').extract_first()
            item['location'] = product.xpath('.//div[contains(@class, "location")]//text()').extract_first()
            yield item
