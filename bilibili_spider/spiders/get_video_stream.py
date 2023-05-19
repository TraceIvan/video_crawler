import scrapy
import pandas as pd
import json
import logging
import re
import os
import numpy as np
from tqdm import tqdm, trange
from bilibili_spider.items import BilibiliSpiderVideoStreamItem

class GetVideoStreamSpider(scrapy.Spider):
    name = 'get_video_stream'
    allowed_domains = [
        "*",
        #'api.bilibili.com',
        #'upos-sz-mirrorkodo.bilivideo.com'
        #'api.bilibili.com/x/player/playurl'
    ]
    start_urls = []
    keywords = ['肖申克的救赎']
    search_video_save_dir = 'bilibili_search_video_res/'
    video_view_save_dir='bilibili_video_view_res/'
    save_dir = 'bilibili_video_stream_res/'
    custom_settings = {
        "ITEM_PIPELINES": {
            'bilibili_spider.pipelines.BilibiliSpiderVideoStreamPipeline': 300,
            'bilibili_spider.pipelines.BilibiliSpiderVideoStreamFilePipeline': 1
        },
        'FILES_STORE':save_dir
    }

    logHandSt = logging.StreamHandler()
    logHandSt.setLevel(logging.INFO)
    StreamHandler_formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
    logHandSt.setFormatter(StreamHandler_formatter)

    def __init__(self, **kwargs):
        logging.root.addHandler(self.logHandSt)
        super().__init__(**kwargs)

    def start_requests(self):
        tot_files=list(os.listdir(self.video_view_save_dir))
        for i in tqdm(range(len(tot_files)), desc='Getting start urls:'):
            if (i + 1) % 100 == 0:
                logging.info('Getting start urls: {}/{}'.format(i + 1, len(tot_files)))
            cur_video=tot_files[i]
            video_view_file = self.video_view_save_dir +cur_video
            if os.path.exists(video_view_file) and os.path.isfile(video_view_file):
                with open(video_view_file, 'r', encoding='utf8') as f:
                    video_view_dict = json.load(f)
                cid = video_view_dict['cid']
                aid = video_view_dict['aid']
                bvid=video_view_dict['bvid']
                new_url = 'http://api.bilibili.com/x/player/playurl?qn=0&fnver=0&fnval=80&fourk=1&aid={}&bvid={}&cid={}'.format(aid, bvid, cid)
                save_file = self.save_dir + str(aid) + '.mp4'
                if not os.path.exists(save_file):
                    yield scrapy.Request(new_url, callback=self.parse)
        # keywords_file='tconst_title.csv'
        # data=pd.read_csv(keywords_file).values.tolist()
        # for cur_data in data:
        #     cur_keyword=cur_data[0]
        #     imdb_tt_id=cur_data[1]
        #     file = self.search_video_save_dir + imdb_tt_id + '.csv'
        #     if os.path.exists(file):
        #         data = pd.read_csv(file, sep='\t')
        #         sub_data = data[['aid', 'bvid']].values.tolist()
        #         for cur_video in sub_data:
        #             video_view_file = self.video_view_save_dir + str(cur_video[0]) + '.json'
        #             if os.path.exists(video_view_file):
        #                 video_view_dict = {}
        #                 with open(video_view_file, 'r', encoding='utf8') as f:
        #                     video_view_dict = json.load(f)
        #                 cid = video_view_dict['cid']
        #                 new_url = 'http://api.bilibili.com/x/player/playurl?fnval=80&fourk=1&aid={}&bvid={}&cid={}'.format(cur_video[0], cur_video[1], cid)
        #                 save_file = self.save_dir + str(cur_video[0]) + '.mp4'
        #                 if not os.path.exists(save_file):
        #                     yield scrapy.Request(new_url, callback=self.parse)

    def parse(self, response, **kwargs):
        response_json = json.loads(response.text)
        logging.info("爬取网页：{}, code:{}, request_priority:{}, request_depth:{},response_depth:{}".format(response.url, response_json['code'],response.request.priority,response.request.meta['depth'],response.meta['depth']))

        new_item=BilibiliSpiderVideoStreamItem()
        new_item["aid"] = re.search("aid=(\S+?)&", response.url).groups()[0]
        new_item["save_name"]=new_item["aid"]
        new_item["bvid"] = re.search("bvid=(\S+?)&", response.url).groups()[0]
        new_item["cid"] = re.search("cid=(\S+)", response.url).groups()[0]
        new_item["video_url"]=response_json['data']['dash']['video'][0]['baseUrl']
        new_item["audio_url"]=response_json['data']['dash']['audio'][0]['baseUrl']
        new_item['file_urls']=[new_item["video_url"],new_item["audio_url"]]
        new_item['file_names']=[new_item['save_name'] + '_video.mp4',new_item['save_name'] + '_audio.mp3']
        yield new_item

        #meta=new_item

        #yield scrapy.Request(new_item["video_url"],callback=self.parse_video,priority=100,meta=meta)

    def parse_video(self,response, **kwargs):
        logging.info("爬取网页：{}, request_priority:{}, request_depth:{},response_depth:{}".format(response.url, response.request.priority, response.request.meta['depth'],
                                                                                                        response.meta['depth']))
        item=response.meta
        file_name=self.save_dir + item['save_name'] + '_video.mp4'
        with open(file_name, "wb") as f:
            f.write(response.body)

        yield scrapy.Request(item["audio_url"],callback=self.parse_audio,priority=200,meta=item)
    def parse_audio(self,response,**kwargs):
        logging.info("爬取网页：{}, request_priority:{}, request_depth:{},response_depth:{}".format(response.url, response.request.priority, response.request.meta['depth'],
                                                                                               response.meta['depth']))
        item = response.meta
        file_name = self.save_dir + item['save_name'] + '_audio.mp3'
        with open(file_name, "wb") as f:
            f.write(response.body)

        yield item