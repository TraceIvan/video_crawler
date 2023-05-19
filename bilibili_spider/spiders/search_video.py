import scrapy
from urllib.parse import quote,unquote
import json
import logging
from bilibili_spider.items import BilibiliSpiderSearchVideoItem
import re
import os
import numpy as np
import pandas as pd
from tqdm import tqdm, trange
class SearchVideoSpider(scrapy.Spider):
    name = 'search_video'
    allowed_domains = [
        'api.bilibili.com',
        #'api.bilibili.com/x/web-interface/search/type'
    ]
    search_type='video'
    keywords=['肖申克的救赎']
    duration_type=1
    start_urls = ['0']
    custom_settings = {
        "ITEM_PIPELINES":{
            'bilibili_spider.pipelines.BilibiliSpiderSearchVideoPipeline':300
        }
    }
    save_dir = 'bilibili_search_video_res/'
    logHandSt = logging.StreamHandler()
    logHandSt.setLevel(logging.INFO)
    StreamHandler_formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
    logHandSt.setFormatter(StreamHandler_formatter)
    def __init__(self, **kwargs):
        logging.root.addHandler(self.logHandSt)
        super().__init__(**kwargs)
    # for cur_keyword in keywords:
    #     start_url = 'https://api.bilibili.com/x/web-interface/search/type?search_type=%s&order=totalrank&keyword=%s&duration=%d&__refresh__=true&tids=0&highlight=1&single_column=0&page=%d' % (
    #         search_type, quote(cur_keyword), duration_type, 1)
    #     start_urls.append(start_url)

    def start_requests(self):
        keywords_file='tconst_title.csv'
        tot_data=pd.read_csv(keywords_file,index_col=False).values.tolist()
        for i in tqdm(range(len(tot_data)), desc='Getting start urls:'):
            if (i + 1) % 100 == 0:
                logging.info('Getting start urls: {}/{}'.format(i + 1, len(tot_data)))
            cur_data=tot_data[i]
            cur_keyword=cur_data[0]
            imdb_tt_id=cur_data[1]
            start_url = 'https://api.bilibili.com/x/web-interface/search/type?search_type=%s&order=totalrank&keyword=%s&duration=%d&__refresh__=true&tids=0&highlight=1&single_column=0&page=%d' % (
                self.search_type, quote(cur_keyword), self.duration_type,1)
            save_file = self.save_dir + imdb_tt_id + '.csv'
            if not os.path.exists(save_file):
                yield scrapy.Request(start_url, callback=self.parse,meta={"save_name":imdb_tt_id})

    def parse(self, response, **kwargs):
        imdb_tt_id=response.meta.get('save_name')
        response_json=json.loads(response.text)
        cur_keyword=unquote(re.search("keyword=(\S+?)&",response.url).groups()[0])
        logging.info("爬取网页：{}, code:{}, request_priority:{}, request_depth:{},response_depth:{}".format(response.url, response_json['code'],response.request.priority,response.request.meta['depth'],response.meta['depth']))
        if 'result' not in response_json['data'].keys():
            logging.error("no 'result' key:{}".format(json.dumps(response_json)))
            cur_item = BilibiliSpiderSearchVideoItem()
            cur_item["save_name"] = imdb_tt_id
            cur_item["aid"]="empty"
            yield cur_item
        else:
            if re.search("page=(\d+)",response.url).groups()[0]=='1':
                numPages=response_json['data']['numPages']
                for new_page in range(2,numPages+1):
                    new_url='https://api.bilibili.com/x/web-interface/search/type?search_type=%s&order=totalrank&keyword=%s&duration=%d&__refresh__=true&tids=0&highlight=1&single_column=0&page=%d'%(self.search_type,quote(cur_keyword),self.duration_type,new_page)
                    yield scrapy.Request(new_url, callback=self.parse,meta={"save_name":imdb_tt_id},priority=100)

            for cur_re in response_json['data']['result']:
                cur_item=BilibiliSpiderSearchVideoItem()
                for cur_item_key in cur_item.fields.keys():
                    if cur_item_key=="save_name":
                        cur_item[cur_item_key]=imdb_tt_id
                    else:
                        if cur_item_key in cur_re.keys():
                            cur_item[cur_item_key]=cur_re[cur_item_key]
                        else:
                            cur_item[cur_item_key] =""
                yield cur_item


