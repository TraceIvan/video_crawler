import scrapy
import pandas as pd
import json
import logging
import re
import os
from tqdm import tqdm, trange
import numpy as np
from bilibili_spider.items import BilibiliSpiderVideoRelatedItem

class VideoRelatedSpider(scrapy.Spider):
    #最多获取40条推荐视频
    name = 'video_related'
    allowed_domains = [
        'api.bilibili.com',
        #'api.bilibili.com/x/web-interface/archive/related'
    ]
    keywords = ['肖申克的救赎']
    search_video_save_dir = 'bilibili_search_video_res/'
    custom_settings = {
        "ITEM_PIPELINES": {
            'bilibili_spider.pipelines.BilibiliSpiderVideoRelatedPipeline': 300
        }
    }
    save_dir = 'bilibili_video_related_res/'
    start_urls = []
    logHandSt = logging.StreamHandler()
    logHandSt.setLevel(logging.INFO)
    StreamHandler_formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
    logHandSt.setFormatter(StreamHandler_formatter)
    def __init__(self, **kwargs):
        logging.root.addHandler(self.logHandSt)
        super().__init__(**kwargs)

    def start_requests(self):
        keywords_file='tconst_title.csv'
        tot_data=pd.read_csv(keywords_file,index_col=False).values.tolist()
        for i in tqdm(range(len(tot_data)), desc='Getting start urls:'):
            if (i + 1) % 100 == 0:
                logging.info('Getting start urls: {}/{}'.format(i + 1, len(tot_data)))
            cur_data=tot_data[i]
            cur_keyword=cur_data[0]
            imdb_tt_id=cur_data[1]
            file = self.search_video_save_dir + imdb_tt_id + '.csv'
            if os.path.exists(file):
                data = pd.read_csv(file, sep='\t')
                data = data.drop_duplicates(['aid'])
                sub_data = data[['aid', 'bvid']].values.tolist()
                for cur_video in sub_data:
                    new_url = 'http://api.bilibili.com/x/web-interface/archive/related?aid={}&bvid={}'.format(cur_video[0], cur_video[1])
                    save_file = self.save_dir + str(cur_video[0]) + '.json'
                    if not os.path.exists(save_file):
                        yield scrapy.Request(new_url, callback=self.parse)

    def parse(self, response,**kwargs):
        response_json = json.loads(response.text)
        logging.info("爬取网页：{}, code:{}, request_priority:{}, request_depth:{},response_depth:{}".format(response.url, response_json['code'],response.request.priority,response.request.meta['depth'],response.meta['depth']))
        aid = re.search("aid=(\S+?)&", response.url).groups()[0]
        bvid = re.search("bvid=(\S+)", response.url).groups()[0]

        cur_item=BilibiliSpiderVideoRelatedItem()
        cur_item['save_name']=aid
        cur_item['aid'] = aid
        cur_item['bvid'] = bvid
        if 'data' not in response_json.keys():
            cur_item['dict_data']=[]
            logging.error("no data key: {}".format(response_json))
        else:
            cur_item['dict_data']=response_json['data']
        yield cur_item
