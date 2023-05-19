import scrapy
import os
import json
import logging
import re
from dm_pb2 import DmSegMobileReply
from google.protobuf.json_format import MessageToJson,Parse
from bilibili_spider.items import BilibiliSpiderVideoDMItem
import datetime
import time
import math
import numpy as np
from tqdm import tqdm, trange
def createDatalist(datestart, dateend=None):
    if dateend is None:
        dateend = datetime.datetime.now().strftime('%Y-%m-%d')
    datestart = datetime.datetime.utcfromtimestamp(datestart)
    dateend = datetime.datetime.strptime(dateend, '%Y-%m-%d')
    date_list = []
    date_list.append(datestart.strftime('%Y-%m-%d'))
    while datestart < dateend:
        datestart += datetime.timedelta(days=+1)
        date_list.append(datestart.strftime('%Y-%m-%d'))
    return date_list

class VideoDmSpider(scrapy.Spider):
    name = 'video_dm'
    allowed_domains = ['api.bilibili.com']
    start_urls = []
    video_view_save_dir = 'bilibili_video_view_res/'
    save_dir = 'bilibili_video_dm_res/'

    custom_settings = {
        "ITEM_PIPELINES": {
            'bilibili_spider.pipelines.BilibiliSpiderVideoDMPipeline': 300,
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
        #yield scrapy.Request('http://api.bilibili.com/x/v2/dm/web/seg.so?type=1&oid=406183227&pid=805454906&segment_index=1', callback=self.parse)
        tot_files=list(os.listdir(self.video_view_save_dir))
        for i in tqdm(range(len(tot_files)), desc='Getting start urls:'):
            if (i + 1) % 100 == 0:
                logging.info('Getting start urls: {}/{}'.format(i + 1, len(tot_files)))
            cur_video=tot_files[i]
            video_view_file = self.video_view_save_dir +cur_video
            if os.path.exists(video_view_file) and os.path.isfile(video_view_file):
                with open(video_view_file, 'r', encoding='utf8') as f:
                    video_view_dict = json.load(f)
                try:
                    cid = video_view_dict['cid']
                    aid = video_view_dict['aid']
                    # bvid=video_view_dict['bvid']
                    # pubdate=video_view_dict['pubdate']
                    duration_seconds=video_view_dict['duration']
                    duration_segments=math.ceil(duration_seconds/60/6)
                    new_url = 'http://api.bilibili.com/x/v2/dm/web/seg.so?type=1&oid={}&pid={}&segment_index={}'.format(cid, aid, 1)
                    save_file = self.save_dir + str(aid) + '.json'
                    if not os.path.exists(save_file):
                        yield scrapy.Request(new_url, callback=self.parse,meta={"aid":aid,'duration_segments':duration_segments})
                except Exception as e:
                    logging.error(e)
        # for cur_video in list(os.listdir(self.video_view_save_dir)):
        #     video_view_file = self.video_view_save_dir +cur_video
        #     if os.path.exists(video_view_file) and os.path.isfile(video_view_file):
        #         with open(video_view_file, 'r', encoding='utf8') as f:
        #             video_view_dict = json.load(f)
        #         cid = video_view_dict['cid']
        #         aid = video_view_dict['aid']
        #         bvid=video_view_dict['bvid']
        #         pubdate=video_view_dict['pubdate']
        #         pubdate=datetime.datetime.utcfromtimestamp(pubdate).strftime("%Y-%m-%d")
        #         new_url = 'http://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid={}&date={}'.format(cid, pubdate)
        #         save_file = self.save_dir + str(aid) + '.json'
        #         if not os.path.exists(save_file):
        #             yield scrapy.Request(new_url, callback=self.parse,meta={"aid":aid})

    def parse(self, response, **kwargs):
        logging.info("爬取网页：{}, request_priority:{}, request_depth:{},response_depth:{}".format(response.url, response.request.priority, response.request.meta['depth'],
                                                                                               response.meta['depth']))
        cid = re.search("oid=(\S+?)&", response.url).groups()[0]
        data=response.body
        DM = DmSegMobileReply()
        try:
            DM.ParseFromString(data)
        except Exception as e:
            logging.error(e)
            if "item" in response.meta.keys():
                yield response.meta['item']
            else:
                new_item = BilibiliSpiderVideoDMItem()
                new_item['save_name'] = str(response.meta['aid'])
                new_item['aid'] = response.meta['aid']
                new_item['cid'] = cid
                new_item['dict_data'] = {"elems":[]}
                yield new_item
        else:
            dm_json = json.loads(MessageToJson(DM))
            duration_segments=response.meta['duration_segments']
            if "item" not in response.meta.keys() and 'elems' not in dm_json.keys():
                pass
            elif "item" not in response.meta.keys():
                new_item=BilibiliSpiderVideoDMItem()
                new_item['save_name']=str(response.meta['aid'])
                new_item['aid'] = response.meta['aid']
                new_item['cid'] = cid
                new_item['dict_data'] = dm_json
                new_url = re.search("(^\S+)&segment_index", response.url).groups()[0]
                cur_segment_index=int(re.search("segment_index=(\S+)", response.url).groups()[0])
                if cur_segment_index<duration_segments:
                    new_url=new_url+"&segment_index="+str(cur_segment_index+1)
                    yield scrapy.Request(new_url, callback=self.parse,meta={"item":new_item,'duration_segments':duration_segments},priority=100)
                else:
                    new_item['dict_data']['elems'] = [x for x in new_item['dict_data']['elems'] if 'progress' in x.keys()]
                    new_item['dict_data']['elems'] = sorted(new_item['dict_data']['elems'], key=lambda x: x['progress'])
                    logging.info("{} 获取弹幕数：{}".format(new_item['aid'], len(new_item['dict_data']['elems'])))
                    yield new_item
                # new_url = re.search("(^\S+)&date", response.url).groups()[0]
                # cur_date=re.search("date=(\S+)", response.url).groups()[0]
                # new_date=datetime.datetime.strptime(cur_date, '%Y-%m-%d')+ datetime.timedelta(days=+1)
                # new_url=new_url+"&date="+new_date.strftime('%Y-%m-%d')
                # yield scrapy.Request(new_url, callback=self.parse,meta={"item":new_item},priority=100)
            elif 'elems' in dm_json.keys():
                item=response.meta['item']
                item['dict_data']['elems'].extend(dm_json['elems'])
                new_url = re.search("(^\S+)&segment_index", response.url).groups()[0]
                cur_segment_index = int(re.search("segment_index=(\S+)", response.url).groups()[0])
                new_url = new_url + "&segment_index=" + str(cur_segment_index + 1)
                if cur_segment_index < duration_segments:
                    yield scrapy.Request(new_url, callback=self.parse, meta={"item": item,'duration_segments':duration_segments}, priority=200)
                else:
                    item['dict_data']['elems'] = [x for x in item['dict_data']['elems'] if 'progress' in x.keys()]
                    item['dict_data']['elems'] = sorted(item['dict_data']['elems'], key=lambda x: x['progress'])
                    logging.info("{} 获取弹幕数：{}".format(item['aid'], len(item['dict_data']['elems'])))
                    yield item
                # new_url = re.search("(^\S+)&date", response.url).groups()[0]
                # cur_date = re.search("date=(\S+)", response.url).groups()[0]
                # new_date = datetime.datetime.strptime(cur_date, '%Y-%m-%d') + datetime.timedelta(days=+1)
                # new_url = new_url + "&date=" + new_date.strftime('%Y-%m-%d')
                # yield scrapy.Request(new_url, callback=self.parse, meta={"item": item}, priority=100)
            else:
                item = response.meta['item']
                item['dict_data']['elems'] =[x for x in item['dict_data']['elems'] if 'progress' in x.keys()]
                item['dict_data']['elems']=sorted(item['dict_data']['elems'],key=lambda x:x['progress'])
                logging.info("{} 获取弹幕数：{}".format(item['aid'],len(item['dict_data']['elems'])))
                yield item




