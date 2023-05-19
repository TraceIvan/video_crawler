import scrapy
import pandas as pd
import json
import logging
import re
import os
import numpy as np
from tqdm import tqdm, trange
from bilibili_spider.items import BilibiliSpiderEachVideoViewItem

class GetVideoSpider(scrapy.Spider):
    name = 'get_video'
    allowed_domains = [
                        'api.bilibili.com',
                        #'api.bilibili.com/x/player/pagelist',
                       #'api.bilibili.com/x/web-interface/view'
                       ]
    start_urls = []
    keywords = ['肖申克的救赎']
    search_video_save_dir = 'bilibili_search_video_res/'
    custom_settings = {
        "ITEM_PIPELINES": {
            'bilibili_spider.pipelines.BilibiliSpiderVideoViewPipeline': 300
        }
    }
    save_dir='bilibili_video_view_res/'
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
                    new_url = 'http://api.bilibili.com/x/player/pagelist?aid={}&bvid={}'.format(cur_video[0], cur_video[1])
                    save_file = self.save_dir + str(cur_video[0]) + '.json'
                    if not os.path.exists(save_file):
                        yield scrapy.Request(new_url, callback=self.parse)

    def parse(self, response, **kwargs):
        response_json = json.loads(response.text)
        logging.info("爬取网页：{}, code:{}, request_priority:{}, request_depth:{},response_depth:{}".format(response.url, response_json['code'],response.request.priority,response.request.meta['depth'],response.meta['depth']))

        aid=re.search("aid=(\S+?)&",response.url).groups()[0]
        bvid=re.search("bvid=(\S+)",response.url).groups()[0]
        try:
            cid=response_json['data'][0]['cid']
        except Exception as e:
            logging.error(e)
            logging.info(response_json)
            new_item = BilibiliSpiderEachVideoViewItem()
            new_item['save_name'] = aid
            new_item['dict_data'] ={}
            yield new_item
        else:
            new_url = 'http://api.bilibili.com/x/web-interface/view?aid={}&bvid={}&cid={}'.format(aid,bvid,cid)
            yield scrapy.Request(new_url, callback=self.parse_video_view,priority=100)

    def parse_video_view(self,response,**kwargs):
        response_json = json.loads(response.text)
        logging.info("爬取网页：{}, code:{}, request_priority:{}, request_depth:{},response_depth:{}".format(response.url, response_json['code'],response.request.priority,response.request.meta['depth'],response.meta['depth']))

        aid = re.search("aid=(\S+?)&", response.url).groups()[0]
        new_item=BilibiliSpiderEachVideoViewItem()
        new_item['save_name'] = aid
        new_item['dict_data']=response_json['data']
        # for cur_item_key in new_item.fields.keys():
        #     if cur_item_key == "save_name":
        #         new_item[cur_item_key] = aid
        #     else:
        #         if cur_item_key.startswith("desc_v2_"):
        #             new_item['desc_v2_raw_text']=response_json['data']['desc_v2'][0]['raw_text']
        #         elif cur_item_key.startswith("owner_"):
        #             map_key=cur_item_key.split('_',1)[-1]
        #             new_item[cur_item_key]=response_json['data']['owner'][map_key]
        #         elif cur_item_key.startswith("stat_"):
        #             map_key = cur_item_key.split('_', 1)[-1]
        #             new_item[cur_item_key] = response_json['data']['stat'][map_key]
        #         elif cur_item_key.startswith("dimension_"):
        #             map_key = cur_item_key.split('_', 1)[-1]
        #             new_item[cur_item_key] = response_json['data']['dimension'][map_key]
        #         elif cur_item_key=='pages':
        #             pages_str=json.dumps(response_json['data']['pages'])
        #             new_item[cur_item_key] =pages_str
        #         elif cur_item_key=='subtitle':
        #             subtitle_str=json.dumps(response_json['data']['subtitle'])
        #             new_item[cur_item_key] =subtitle_str
        #         elif cur_item_key=='rights':
        #             rights_str=json.dumps(response_json['data']['rights'])
        #             new_item[cur_item_key] =rights_str
        #         elif cur_item_key == 'forward' or cur_item_key == 'mission_id' or cur_item_key == 'redirect_url':
        #             if cur_item_key in response_json['data'].keys():
        #                 new_item[cur_item_key] =response_json['data'][cur_item_key]
        #         else:
        #             new_item[cur_item_key] = response_json['data'][cur_item_key]
        yield new_item


