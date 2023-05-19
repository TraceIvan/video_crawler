import scrapy
import pandas as pd
import json
import logging
import re
import os
import numpy as np
from tqdm import tqdm, trange
from bilibili_spider.items import BilibiliSpiderVideoReplyItem
class VideoReplySpider(scrapy.Spider):
    name = 'video_reply'
    allowed_domains = [
        'api.bilibili.com',
        #'api.bilibili.com/x/v2/reply/main'
    ]
    keywords = ['肖申克的救赎']
    search_video_save_dir = 'bilibili_search_video_res/'
    custom_settings = {
        "ITEM_PIPELINES": {
            'bilibili_spider.pipelines.BilibiliSpiderVideoReplyPipeline': 300
        }
    }
    save_dir = 'bilibili_video_reply_res/'
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
        logging.info("data preview:")
        logging.info(tot_data[:10])
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
                    new_url = 'https://api.bilibili.com/x/v2/reply/main?oid={}&type=1&mode=2&next=0'.format(cur_video[0])
                    save_file = self.save_dir + str(cur_video[0]) + '.json'
                    if not os.path.exists(save_file):
                        yield scrapy.Request(new_url, callback=self.parse)

    def parse(self, response, **kwargs):
        response_json = json.loads(response.text)
        logging.info("爬取网页：{}, code:{}, request_priority:{}, request_depth:{},response_depth:{}".format(response.url, response_json['code'],response.request.priority,response.request.meta['depth'],response.meta['depth']))

        oid = re.search("oid=(\S+?)&", response.url).groups()[0]
        new_item=BilibiliSpiderVideoReplyItem()
        new_item['save_name'] = oid
        new_item['oid'] = oid
        if 'data' not in response_json.keys():
            logging.error("no data key: {}".format(response_json))
            new_item['replies'] =[]
            yield new_item
        else:
            new_item['mid'] = response_json['data']['upper']['mid']
            new_item['replies']=response_json['data']['replies']
            new_url=re.search("(^\S+)&next",response.url).groups()[0]
            next_id=response_json['data']['cursor']['next']
            new_url=new_url+'&next={}'.format(next_id)
            if not bool(response_json['data']['cursor']['is_end']):
                yield scrapy.Request(new_url, callback=self.next_parse,meta=new_item,priority=100)
            else:
                yield new_item


    def next_parse(self,response,**kwargs):
        cur_item=response.meta
        response_json = json.loads(response.text)
        logging.info("爬取网页：{}, code:{}, request_priority:{}, request_depth:{},response_depth:{}".format(response.url, response_json['code'],response.request.priority,response.request.meta['depth'],response.meta['depth']))
        cur_item['replies'].extend(response_json['data']['replies'])
        new_url = re.search("(^\S+)&next", response.url).groups()[0]
        next_id = response_json['data']['cursor']['next']
        new_url = new_url + '&next={}'.format(next_id)
        if not bool(response_json['data']['cursor']['is_end']):
            yield scrapy.Request(new_url, callback=self.next_parse, meta=cur_item,priority=200)
        else:
            yield cur_item

