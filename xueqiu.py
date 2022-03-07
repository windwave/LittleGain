# -*- coding: utf-8 -*-
import scrapy
import json
from collections import deque
from xueqiuCrawler.items import XueqiucrawlerItem
from xueqiuCrawler.scrapy_redis.spiders import RedisSpider

class XueqiuSpider(RedisSpider):
    name = 'xueqiu'
    redis_key = 'xueqiu:start_urls'
    allowed_domains = ['xueqiu.com']
    start_urls = ['https://xueqiu.com/friendships/groups/members.json?uid=5842900570&page=1&gid=0']
    first_user_id = 5842900570

    # 在关注页面用的header
    my_header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Upgrade-Insecure-Requests": "1",
        "Cookie":"Hm_lvt_1db88642e346389874251b5a1eded6e3=1646571445; device_id=b9e400fb745c0d8ec45259208e85c4fc; xq_a_token=eaf4608c640982f55a7e02cc9ef7c61abeb0ff68; xqat=eaf4608c640982f55a7e02cc9ef7c61abeb0ff68; xq_r_token=93e5baef354e8fcf218a6bf117c7acebc3030159; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjMyMDg0MzcxMzQsImlzcyI6InVjIiwiZXhwIjoxNjQ4NzA1MDQ2LCJjdG0iOjE2NDY1NzE0NzU2OTMsImNpZCI6ImQ5ZDBuNEFadXAifQ.nyYC8AbQgUTxUBjCuNwyqKTsJrASdWGU3Mkqs76c4oxGLdDuwXk7C_FbguTXpK0eBMcDmjROkdyTC6eGgsppn8TWAPTiUwIZNNTXs7PYrcPvaIIAYvi-dBdzhDdXbmoX3B5acQvEjW7ORe0VsNEeJfufDJyyqymDtEimclT2xH3xDvx67UsGrsueTMT1HKXdGSYrHSFUBNfSBRezZ0ksVqWG756NDfB483mbMLIpjj0HyQL9mOckUvYF5JZUjTXBu7IfxxseDCLNAPFRIngk-pRpp_6wffjvR4HbaE4pXL8qnJBK1LCLJodq2SxRMM6dKIQNqUgHsG-OLe4vfNmNtw; u=3208437134; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1646572585; remember=1; xq_is_login=1; s=ca11s1jb7x; bid=8ba08f0e1e5164b57b5ac3644a818c97_l0fasx1d"      
        }
    def start_requests(self):
        for url in XueqiuSpider.start_urls:
            yield scrapy.Request(
                                url=url,
                                headers=XueqiuSpider.my_header,
                                callback=self.parse,
                                meta={'user_id':XueqiuSpider.first_user_id}
                                )

    def parse(self, response):
        # """该解析函数主要用来收集用户的所有关注"""
        context = json.loads(response.text)
        current_id = response.meta.get('user_id')
        page_num = context['maxPage'] # 该用户总共有多少页面
        current_page = context['page'] # 目前是第几页

        for user in context['users']: # 遍历当前页面下的所有关注用户
            U = UserItem()
            U['user_id'] = user['id']
            U['user_name'] = user['screen_name']
            U['follow_num'] = user['friends_count']
            U['fans_num'] = user['followers_count']
            yield U
            
            #check portfolio
            user_portfolio_url = "https://stock.xueqiu.com/v5/stock/portfolio/stock/list.json?size=1000&category=3&uid={user_id}"
            
            yield scrapy.Request(
                url=user_portfolio_url,
                headers=XueqiuSpider.my_header,
                callback=self.parse_users_portf,  # 开始收集用户的关注页面
                meta={'user_id': user['id']}  # 用户的id
            )
            

            url_str = "https://xueqiu.com/friendships/groups/members.json?uid={user_id}&page=1&gid=0"
            next_url = url_str.format(user_id=user['id'])

            yield scrapy.Request(
                url=next_url,
                headers=XueqiuSpider.my_header,
                callback=self.parse,  # 开始收集用户的关注页面
                meta={'user_id': user['id']}  # 用户的id
            )

        if current_page >= page_num: # 当前用户的所有关注页面已经收集完毕
            #开始收集该用户粉丝页面的用户
            url_str = "https://xueqiu.com/friendships/followers.json?uid={user_id}&pageNo=1"
            url = url_str.format(user_id=current_id)
            yield scrapy.Request(
                url=url,
                headers=XueqiuSpider.my_header,
                callback=self.parse2, # 收集所有的粉丝
                meta={'user_id': current_id}
            )

        else: # 该用户的下一个关注页面
            url_str = "https://xueqiu.com/friendships/groups/members.json?uid={user_id}&page={page_id}&gid=0"
            page_id = int(current_page)+1
            next_url = url_str.format(user_id=current_id, page_id=page_id)

            yield scrapy.Request(
                url=next_url,
                headers=XueqiuSpider.my_header,
                callback=self.parse,
                meta={'user_id': current_id} # 仍然是当前用户的id
            )

    def parse2(self, response):
        context = json.loads(response.text)
        current_id = response.meta.get('user_id')
        page_num = context['maxPage']  # 该用户总共有多少页面
        current_page = context['page']  # 目前是第几页

        for user in context['followers']:  # 遍历当前页面下的所有用户
            U = UserItem()
            U['user_id'] = user['id']
            U['user_name'] = user['screen_name']
            U['follow_num'] = user['friends_count']
            U['fans_num'] = user['followers_count']
            yield U

            #check portfolio
            user_portfolio_url = "https://stock.xueqiu.com/v5/stock/portfolio/stock/list.json?size=1000&category=3&uid={user_id}"
            
            yield scrapy.Request(
                url=user_portfolio_url,
                headers=XueqiuSpider.my_header,
                callback=self.parse_users_portf,  # 开始收集用户的关注页面
                meta={'user_id': user['id']}  # 用户的id
            )
            

            url_str = "https://xueqiu.com/friendships/groups/members.json?uid={user_id}&page=1&gid=0"
            next_url = url_str.format(user_id=user['id'])
            
            
            url_str = "https://xueqiu.com/friendships/groups/members.json?uid={user_id}&page=1&gid=0"
            next_url = url_str.format(user_id=user['id'])

            yield scrapy.Request(
                url=next_url,
                headers=XueqiuSpider.my_header,
                callback=self.parse,  # 开始收集用户的关注页面
                meta={'user_id': user['id']}  # 用户的id
            )

        if current_page >= page_num:  # 当前用户的所有页面（关注+粉丝）已经收集完毕
            pass
        else:  # 该用户的下一个粉丝页面
            url_str = "https://xueqiu.com/friendships/followers.json?uid={user_id}&pageNo={page_id}"
            page_id = int(current_page) + 1
            next_url = url_str.format(user_id=current_id, page_id=page_id)

            yield scrapy.Request(
                url=next_url,
                headers=XueqiuSpider.my_header,
                callback=self.parse2,
                meta={'user_id': current_id}  # 仍然是当前用户的id
            )

            
    def parse_users_portf(self, response):
        context = json.loads(response.text)
        
        for p in context['stocks']:
            portfolio_id = p['symbol']
            portfolio_detail_url="https://xueqiu.com/P/{portfolio_id}"
            yield scrapy.Request(
                url=portfolio_detail_url,
                headers=XueqiuSpider.my_header,
                callback=self.parse_portf,
                meta={'user_id': current_id}  # 仍然是当前用户的id
            )


    def parse_portf(self, response):
        html = response.body.decode()
        pos_start = html.find('SNB.cubeInfo = ') + len('SNB.cubeInfo = ')
        pos_end = html.find('SNB.cubePieData')
        time.sleep(5)
        if pos_end <= 0:
            return
        P = PortfolioItem()
        P['portfolio_id'] = response.meta['symbol']
        P['portfolio_totalAction'] = json.loads(html[pos_start:pos_end - 2])
        yield P

            
            
class UserInfo(object):
    def __init__(self, user_id, user_name, follow_num, fans_num):
        self.user_id = user_id
        self.user_name = user_name
        self.follow_num = follow_num
        self.fans_num = fans_num
        
        
class PortfolioItem(object):
    def __init__(self,portfolio_id, portfolio_totalAction):
        self.portfolio_id = portfolio_id
        self.portfolio_totalAction = portfolio_totalAction
 