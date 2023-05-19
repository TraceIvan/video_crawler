from scrapy.cmdline import execute
import datetime

today=datetime.datetime.now()
spider_type="video_related"
log_file='logs/bilibili_{}_{}_{}_{}.log'.format(spider_type,today.year,today.month,today.day)
execute("scrapy crawl {} -s LOG_FILE={}".format(spider_type,log_file).split())#-s LOG_FILE={}