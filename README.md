# video_crawler
基于scrapy框架，借助B站对外开放的API来采集同IMDB电影相关的短视频数据。

## 1、爬虫说明
SearchVideoSpider：通过B站提供的搜索视频api，检索和IMDB影片相关的短视频。

GetVideoSpider：通过B站提供的短视频详情api，获取短视频的基本信息。

VideoReplySpider：通过B站提供的短视频评论api，获取短视频的评论信息。

VideoRelatedSpider：通过B站提供的短视频相关推荐api，获取短视频的相关其他视频。

VideoDmSpider：通过B站提供的短视频弹幕api，获取短视频的弹幕信息。

GetVideoStreamSpider：通过B站提供的短视频的音视频流api，获取短视频的音视频下载链接，并将其下载到本地。

GetUserInfoSpider：通过B站提供的用户api，获取短视频的用户信息。

## 2、接口说明
### SearchVideoSpider类
start_requests(self)：通过读取IMDB影片列表，构建搜索视频api请求。

parse(self, response, **kwargs)：由start_requests调用，将api返回的json数据进行解析，并将其保存在相关的item类中。

### GetVideoSpider类
start_requests(self)：据SearchVideoSpider类中获取的短视频aid和bvid，构建对应的api请求。

parse(self, response, **kwargs)：由start_requests调用，用于解析api返回后的json数据，获取短视频的cid，构建短视频详情api的请求。

parse_video_view(self,response,**kwargs)：由parse调用，用于解析api返回后的json数据，获取短视频详情信息，并将其保存在相关的item类中。

### VideoReplySpider类
start_requests(self)：根据SearchVideoSpider类中获取的短视频aid，构建对应的api请求。

parse(self, response, **kwargs)：由start_requests调用，用于解析api返回后的json数据，获取短视频的评论信息，并将其保存在相关的item类中。

next_parse(self,response,**kwargs)：当存在更多的评论时，由parse或next_parse调用，获取短视频的下一页评论信息，并将其保存在相关的item类中。

### VideoDmSpider类
start_requests(self)：根据GetVideoSpider类中获取的短视频cid和aid，构建对应的api请求。

parse(self, response, **kwargs)：由start_requests调用，用于解析api返回后的json数据，获取短视频的弹幕信息，并将其保存在相关的item类中。

### VideoRelatedSpider类
start_requests(self)：根据SearchVideoSpider类中获取的短视频aid和bvid，构建对应的api请求。

parse(self, response, **kwargs)：由start_requests调用，用于解析api返回后的json数据，获取短视频的相关推荐视频，并将其保存在相关的item类中。

### GetVideoStreamSpider类
start_requests(self)：根据GetVideoSpider类中获取的短视频aid、cid和bvid，构建对应的api请求。

parse(self, response, **kwargs)：由start_requests调用，用于解析api返回后的json数据，获取短视频的音视频流链接，并将其保存在相关的item类中。

### GetUserInfoSpider类
start_requests(self)：根据SearchVideoSpider类中获取的短视频mid，构建对应的api请求。

parse(self, response, **kwargs)：由start_requests调用，用于解析api返回后的json数据，获取短视频的所属用户的基本信息，并将其保存在相关的item类中。

parse_card(self, response, **kwargs)：由parse调用，用于解析api返回后的json数据，获取短视频的所属用户的个人卡片信息，并将其保存在相关的item类中。
