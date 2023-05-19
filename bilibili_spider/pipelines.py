# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
import csv
import logging
import json
import requests
from scrapy.pipelines.files import FilesPipeline
import scrapy
import random
import shutil

class BilibiliSpiderSearchVideoPipeline:
    sep = '\t'
    save_dir='bilibili_search_video_res/'
    sum_json='sum_bilibili_search_video_res.json'
    def __init__(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    def process_item(self, item, spider):
        save_file=self.save_dir+item['save_name']+'.csv'
        head=list(item.fields.keys())
        head.remove('save_name')
        data=[]
        if item['aid']=="empty":
            if not os.path.exists(save_file):
                with open(save_file, 'w', encoding="utf8", newline='') as fi:
                    writer = csv.writer(fi, delimiter=self.sep)
                    writer.writerow(head)
            return item
        for cur_col in head:
            data.append(item[cur_col])
        with open(self.sum_json, 'r', encoding="utf8", newline='') as fi:
            json_data=json.load(fi)
        if not os.path.exists(save_file):
            with open(save_file, 'w', encoding="utf8", newline='') as fi:
                writer = csv.writer(fi, delimiter=self.sep)
                writer.writerow(head)
            json_data['bilibili_search_video_res_crawled']+=1
        with open(save_file, 'a+', encoding="utf8", newline='') as fi:
            writer = csv.writer(fi, delimiter=self.sep)
            writer.writerow(data)
        json_data['bilibili_search_video_res_samples']+=1
        json_data['bilibili_search_video_res_attributes'] += len(data)
        with open(self.sum_json, 'w', encoding="utf-8", newline='') as fi:
            new_sum_json = json.dumps(json_data, ensure_ascii=False, indent=4)
            fi.write(new_sum_json)
        return item

class BilibiliSpiderVideoViewPipeline:
    sep = '\t'
    save_dir='bilibili_video_view_res/'
    sum_json = 'sum_bilibili_video_view_res.json'
    def __init__(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    def process_item(self, item, spider):
        save_file=self.save_dir+item['save_name']+'.json'
        with open(save_file, 'w', encoding="utf-8", newline='') as fi:
            char_infos_json = json.dumps(item['dict_data'], ensure_ascii=False, indent=4)
            fi.write(char_infos_json)
        with open(self.sum_json, 'r', encoding="utf8", newline='') as fi:
            json_data=json.load(fi)
        json_data['bilibili_video_view_res_crawled'] += 1
        if isinstance(item['dict_data'], list):
            json_data['bilibili_video_view_res_samples'] += len(item['dict_data'])
            for pos in range(len(item['dict_data'])):
                json_data['bilibili_video_view_res_attributes'] += len(item['dict_data'][pos].items())
        else:
            json_data['bilibili_video_view_res_samples'] += 1
            json_data['bilibili_video_view_res_attributes'] += len(item['dict_data'].items())
        with open(self.sum_json, 'w', encoding="utf-8", newline='') as fi:
            new_sum_json = json.dumps(json_data, ensure_ascii=False, indent=4)
            fi.write(new_sum_json)
        return item

class BilibiliSpiderVideoStreamFilePipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        USER_AGENT_LIST = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
        ]
        rand_use = random.choice(USER_AGENT_LIST)
        headers={"User-Agent":rand_use,'referer':"https://www.bilibili.com"}
        for file_url,file_name in zip(item['file_urls'],item['file_names']):
            yield scrapy.Request(file_url,meta={"file_name":file_name},headers=headers,priority=100)

    def file_path(self, request, response=None, info=None, *, item=None):
        file_name=request.meta['file_name']
        return file_name

class BilibiliSpiderVideoStreamPipeline:
    sep = '\t'
    save_dir='bilibili_video_stream_res/'
    sum_json = 'sum_bilibili_video_stream_res.json'
    def __init__(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def process_item(self, item, spider):
        USER_AGENT_LIST = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
        ]
        rand_use = random.choice(USER_AGENT_LIST)
        headers = {"User-Agent": rand_use, 'referer': "https://www.bilibili.com"}
        save_file=self.save_dir+item['save_name']+'.mp4'
        save_video_file = self.save_dir + item['save_name'] + '_video.mp4'
        save_audio_file = self.save_dir + item['save_name'] + '_audio.mp3'
        # with open(save_video_file, "wb") as f:
        #      f.write(requests.get(url=item['video_url'],headers=headers,proxies=None,stream=True).content)
        # with open(save_audio_file, "wb") as f:
        #      f.write(requests.get(url=item['audio_url'],headers=headers,proxies=None,stream=True).content)
        ex_cmd = "ffmpeg -i {} -i {} -c:v copy -c:a aac -strict experimental {}".format(save_video_file,save_audio_file,save_file)
        #ffmpeg -i {} -i {} -map 0:v -map 1:a {}
        #ffmpeg -i {} -i {} -vcodec copy -acodec copy {}
        #ffmpeg -i {} -i {} -c:v copy -c:a aac -strict experimental {}
        message=os.system(ex_cmd)
        if message:
            logging.error(message)
        else:
            os.remove(save_video_file)
            os.remove(save_audio_file)
            with open(self.sum_json, 'r', encoding="utf8", newline='') as fi:
                json_data = json.load(fi)
            json_data['bilibili_video_stream_res_crawled'] += 1
            json_data['bilibili_video_stream_res_samples'] += 1
            with open(self.sum_json, 'w', encoding="utf-8", newline='') as fi:
                new_sum_json = json.dumps(json_data, ensure_ascii=False, indent=4)
                fi.write(new_sum_json)

        return item

class BilibiliSpiderVideoReplyPipeline:
    sep = '\t'
    save_dir='bilibili_video_reply_res/'
    sum_json = 'sum_bilibili_video_reply_res.json'
    def __init__(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    def process_item(self, item, spider):
        save_file=self.save_dir+item['save_name']+'.json'
        with open(save_file, 'w', encoding="utf-8", newline='') as fi:
            char_infos_json = json.dumps(item['replies'], ensure_ascii=False, indent=4)
            fi.write(char_infos_json)
        with open(self.sum_json, 'r', encoding="utf8", newline='') as fi:
            json_data = json.load(fi)
        json_data['bilibili_video_reply_res_crawled'] += 1
        if isinstance(item['replies'], list):
            json_data['bilibili_video_reply_res_samples'] += len(item['replies'])
            for pos in range(len(item['replies'])):
                json_data['bilibili_video_reply_res_attributes'] += len(item['replies'][pos].items())
        else:
            json_data['bilibili_video_reply_res_samples'] += 1
            json_data['bilibili_video_reply_res_attributes'] += len(item['replies'].items())
        with open(self.sum_json, 'w', encoding="utf-8", newline='') as fi:
            new_sum_json = json.dumps(json_data, ensure_ascii=False, indent=4)
            fi.write(new_sum_json)
        return item

class BilibiliSpiderVideoRelatedPipeline:
    sep = '\t'
    save_dir='bilibili_video_related_res/'
    sum_json = 'sum_bilibili_video_related_res.json'
    def __init__(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    def process_item(self, item, spider):
        save_file=self.save_dir+item['save_name']+'.json'
        with open(save_file, 'w', encoding="utf-8", newline='') as fi:
            char_infos_json = json.dumps(item['dict_data'], ensure_ascii=False, indent=4)
            fi.write(char_infos_json)
        with open(self.sum_json, 'r', encoding="utf8", newline='') as fi:
            json_data = json.load(fi)
        json_data['bilibili_video_related_res_crawled'] += 1
        if isinstance(item['dict_data'], list):
            json_data['bilibili_video_related_res_samples'] += len(item['dict_data'])
            for pos in range(len(item['dict_data'])):
                json_data['bilibili_video_related_res_attributes'] += len(item['dict_data'][pos].items())
        else:
            json_data['bilibili_video_related_res_samples'] += 1
            json_data['bilibili_video_related_res_attributes'] += len(item['dict_data'].items())
        with open(self.sum_json, 'w', encoding="utf-8", newline='') as fi:
            new_sum_json = json.dumps(json_data, ensure_ascii=False, indent=4)
            fi.write(new_sum_json)
        return item

class BilibiliSpiderVideoDMPipeline:
    save_dir = 'bilibili_video_dm_res/'
    sum_json = 'sum_bilibili_video_dm_res.json'
    def __init__(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    def process_item(self, item, spider):
        save_file=self.save_dir+item['save_name']+'.json'
        with open(save_file, 'w', encoding="utf-8", newline='') as fi:
            char_infos_json = json.dumps(item['dict_data']['elems'], ensure_ascii=False, indent=4)
            fi.write(char_infos_json)
        with open(self.sum_json, 'r', encoding="utf8", newline='') as fi:
            json_data = json.load(fi)
        json_data['bilibili_video_dm_res_crawled'] += 1
        if isinstance(item['dict_data']['elems'], list):
            json_data['bilibili_video_dm_res_samples'] += len(item['dict_data']['elems'])
            for pos in range(len(item['dict_data']['elems'])):
                json_data['bilibili_video_dm_res_attributes'] += len(item['dict_data']['elems'][pos].items())
        else:
            json_data['bilibili_video_dm_res_samples'] += 1
            json_data['bilibili_video_dm_res_attributes'] += len(item['dict_data']['elems'].items())
        with open(self.sum_json, 'w', encoding="utf-8", newline='') as fi:
            new_sum_json = json.dumps(json_data, ensure_ascii=False, indent=4)
            fi.write(new_sum_json)
        return item

class BilibiliSpiderUserPipeline:
    sep = '\t'
    save_dir='bilibili_user_res/'
    sum_json = 'sum_bilibili_user_res.json'
    def __init__(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        if not os.path.exists(self.sum_json):
            tmp_dict={"bilibili_user_res_crawled":0,"bilibili_user_res_samples":0,"bilibili_user_res_attributes":0}
            with open(self.sum_json, 'w', encoding="utf-8", newline='') as fi:
                new_sum_json = json.dumps(tmp_dict, ensure_ascii=False, indent=4)
                fi.write(new_sum_json)
    def process_item(self, item, spider):
        save_file=self.save_dir+item['save_name']+'.json'
        with open(save_file, 'w', encoding="utf-8", newline='') as fi:
            char_infos_json = json.dumps(item['dict_data'], ensure_ascii=False, indent=4)
            fi.write(char_infos_json)
        with open(self.sum_json, 'r', encoding="utf8", newline='') as fi:
            json_data=json.load(fi)
        json_data['bilibili_user_res_crawled'] += 1
        if isinstance(item['dict_data'], list):
            json_data['bilibili_user_res_samples'] += len(item['dict_data'])
            for pos in range(len(item['dict_data'])):
                json_data['bilibili_user_res_attributes'] += len(item['dict_data'][pos].items())
        else:
            json_data['bilibili_user_res_samples'] += 1
            json_data['bilibili_user_res_attributes'] += len(item['dict_data'].items())
        with open(self.sum_json, 'w', encoding="utf-8", newline='') as fi:
            new_sum_json = json.dumps(json_data, ensure_ascii=False, indent=4)
            fi.write(new_sum_json)
        return item