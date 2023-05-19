import scrapy
import os
import json
import pandas as pd
import logging
import numpy as np
from tqdm import tqdm, trange
from bilibili_spider.items import BilibiliSpiderUserItem

class GetUserInfoSpider(scrapy.Spider):
    name = 'get_user_info'
    allowed_domains = ['api.bilibili.com']
    start_urls = []
    search_video_save_dir = 'bilibili_search_video_res/'
    video_view_save_dir='bilibili_video_view_res/'
    save_dir = 'bilibili_user_res/'
    custom_settings = {
        "ITEM_PIPELINES": {
            'bilibili_spider.pipelines.BilibiliSpiderUserPipeline': 300,
        },
    }
    logHandSt = logging.StreamHandler()
    logHandSt.setLevel(logging.INFO)
    StreamHandler_formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
    logHandSt.setFormatter(StreamHandler_formatter)

    def __init__(self, **kwargs):
        logging.root.addHandler(self.logHandSt)
        super().__init__(**kwargs)


    def start_requests(self):
        for cur_video in list(os.listdir(self.search_video_save_dir)):
            search_video_file = self.search_video_save_dir +cur_video
            if os.path.exists(search_video_file) and os.path.isfile(search_video_file):
                data = pd.read_csv(search_video_file, sep='\t')
                data = data.drop_duplicates(['mid'])
                sub_data = list(np.array(data[['mid']]).tolist())
                for i in tqdm(range(len(sub_data)), desc='Getting start urls:'):
                    if (i+1)%100==0:
                        logging.info('Getting start urls: {}/{}'.format(i+1,len(sub_data)))
                    cur_user=sub_data[i]
                    new_url = 'http://api.bilibili.com/x/space/acc/info?mid={}'.format(cur_user[0])
                    save_file = self.save_dir + str(cur_user[0]) + '.json'
                    if not os.path.exists(save_file):
                        yield scrapy.Request(new_url, callback=self.parse,meta={"mid":cur_user[0]})

    def parse(self, response, **kwargs):
        response_json = json.loads(response.text)
        logging.info("爬取网页：{}, code:{}, request_priority:{}, request_depth:{},response_depth:{}".format(response.url, response_json['code'], response.request.priority, response.request.meta['depth'],
                                                                                                        response.meta['depth']))
        mid=response.meta["mid"]
        new_item=BilibiliSpiderUserItem()
        new_item["save_name"]=str(mid)
        new_item["mid"] = str(mid)
        if 'data' not in response_json.keys():
            logging.error("no data key: {}".format(response_json))
            new_item["dict_data"]={}
            yield new_item
        else:
            new_item["dict_data"]=response_json["data"]

            new_url = 'http://api.bilibili.com/x/web-interface/card?mid={}'.format(mid)
            yield scrapy.Request(new_url, callback=self.parse_card, meta={"item": new_item},priority=100)

    def parse_card(self, response, **kwargs):
        response_json = json.loads(response.text)
        logging.info("爬取网页：{}, code:{}, request_priority:{}, request_depth:{},response_depth:{}".format(response.url, response_json['code'], response.request.priority, response.request.meta['depth'],
                                                                                                        response.meta['depth']))

        item=response.meta["item"]
        if 'data' in response_json.keys() and 'card' in response_json['data'].keys():
            item["dict_data"]["card"]=response_json['data']["card"]
        yield item


