# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BilibiliSpiderSearchVideoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    save_name=scrapy.Field()
    aid=scrapy.Field()#稿件avid
    arcurl=scrapy.Field()#稿件url
    author=scrapy.Field()
    bvid=scrapy.Field()#稿件bvid
    mid=scrapy.Field()#UP主mid
    description=scrapy.Field()
    duration=scrapy.Field()#视频时长
    favorites=scrapy.Field()#视频收藏数
    pic=scrapy.Field()#视频封面url
    play=scrapy.Field()#视频播放量
    pubdate=scrapy.Field()#	视频投稿时间	时间戳
    senddate=scrapy.Field()#视频发布时间	时间戳
    rank_score=scrapy.Field()#结果排序量化值
    review=scrapy.Field()#视频评论数
    tag=scrapy.Field()#视频TAG	每项TAG用,分隔
    title=scrapy.Field()#视频标题	关键字用xml标签<em class="keyword">标注
    type=scrapy.Field()#结果类型
    typeid=scrapy.Field()#视频分区tid
    typename=scrapy.Field()#视频子分区名
    video_review=scrapy.Field()#视频弹幕量

class BilibiliSpiderEachVideoViewItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    save_name=scrapy.Field()
    dict_data=scrapy.Field()
    # aid=scrapy.Field()#稿件avid
    # bvid=scrapy.Field()#稿件bvid
    # cid=scrapy.Field()#视频cid
    # tid=scrapy.Field()#分区tid
    # tname=scrapy.Field()#子分区名称
    # copyright=scrapy.Field()#视频类型 1：原创,2：转载
    # pic=scrapy.Field()#稿件封面图片url
    # title=scrapy.Field()#稿件标题
    # pubdate=scrapy.Field()#稿件发布时间	时间戳
    # ctime=scrapy.Field()#用户投稿时间	时间戳
    # desc=scrapy.Field()#视频简介
    # desc_v2_raw_text=scrapy.Field()#新版视频简介内容
    # duration=scrapy.Field()#稿件总时长(所有分P) 单位为秒
    # owner_mid=scrapy.Field()#UP主mid
    # owner_name=scrapy.Field()#	UP主昵称
    # owner_face = scrapy.Field()#	UP主头像
    # stat_aid=scrapy.Field()#稿件avid
    # stat_view=scrapy.Field()#播放数
    # stat_danmaku=scrapy.Field()#弹幕数
    # stat_reply=scrapy.Field()#评论数
    # stat_favorite=scrapy.Field()#收藏数
    # stat_coin=scrapy.Field()#投币数
    # stat_share=scrapy.Field()#分享数
    # stat_now_rank=scrapy.Field()#	当前排名
    # stat_his_rank = scrapy.Field()  #历史最高排行
    # stat_like=scrapy.Field()#获赞数
    # stat_dislike=scrapy.Field()#点踩数	恒为0
    # stat_evaluation=scrapy.Field()#	视频评分
    # stat_argue_msg=scrapy.Field()#警告/争议提示信息
    # dynamic=scrapy.Field()#视频同步发布的的动态的文字内容
    # dimension_width=scrapy.Field()#视频分辨率
    # dimension_height=scrapy.Field()#视频分辨率
    # pages=scrapy.Field()#视频分P列表,用json转str存,数组中对象：
    # #cid，当前分P cid
    # #page，当前分P
    # #from，视频来源	vupload：普通上传（B站）；hunan：芒果TV；qq：腾讯
    # # part，当前分P标题
    # # duration，当前分P持续时间	单位为秒
    # # vid，站外视频vid	仅站外视频有效
    # # weblink，站外视频跳转url	仅站外视频有效
    # # dimension，当前分P分辨率	部分较老视频无分辨率值
    # subtitle=scrapy.Field()#视频CC字幕信息,用json转str存：
    # #allow_submit，是否允许提交字幕
    # #list，字幕列表
    # rights=scrapy.Field()#视频属性标志,用json转str存:
    # # elec,是否支持充电;download,是否允许下载;movie,是否电影;pay,是否PGC付费
    # #hd5,是否有高码率;no_reprint;是否显示“禁止转载“标志;autoplay,是否自动播放;ugc_pay,是否UGC付费;is_stein_gate,是否为互动视频
    # #is_cooperation是否为联合投稿
    #
    # #不一定有
    # forward=scrapy.Field()#仅撞车视频存在此字段
    # mission_id=scrapy.Field()#稿件参与的活动id
    # redirect_url=scrapy.Field()#重定向url，仅番剧或影视视频存在此字段，用于番剧&影视的av/bv->ep

class BilibiliSpiderVideoStreamItem(scrapy.Item):
    save_name=scrapy.Field()
    aid=scrapy.Field()
    bvid=scrapy.Field()
    cid=scrapy.Field()
    video_url=scrapy.Field()
    audio_url=scrapy.Field()
    file_urls=scrapy.Field()
    file_names = scrapy.Field()
    files=scrapy.Field()

class BilibiliSpiderVideoReplyItem(scrapy.Item):
    save_name=scrapy.Field()
    oid=scrapy.Field()#目标评论区id
    mid=scrapy.Field()#UP主mid
    replies=scrapy.Field()

class BilibiliSpiderVideoRelatedItem(scrapy.Item):
    save_name=scrapy.Field()
    aid=scrapy.Field()
    bvid=scrapy.Field()
    dict_data=scrapy.Field()

class BilibiliSpiderVideoDMItem(scrapy.Item):
    save_name=scrapy.Field()
    aid=scrapy.Field()
    cid=scrapy.Field()
    dict_data=scrapy.Field()


class BilibiliSpiderUserItem(scrapy.Item):
    save_name=scrapy.Field()
    mid=scrapy.Field()
    dict_data=scrapy.Field()