import urllib
import urllib.request
import bs4
from bs4 import BeautifulSoup
from pathlib import Path
import time
import os
import requests
from requests import Timeout

def send_request(url_: str, sleep_=0.3) -> bs4.BeautifulSoup:
    # 若url是本地的html文件，则无法发送请求
    if "http" not in url_:
        return bs4_local_html(url_)
    req = urllib.request.Request(url_)
    # 设置请求头
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36')  # set user-agent header
    # req.add_header('Cookie','xxx')
    response_ = urllib.request.urlopen(req)
    soup = BeautifulSoup(response_, "html.parser")
    # 给服务器减压
    time.sleep(sleep_)
    return soup


def get_soup_by_requests(url: str, params: dict, headers: dict, sleep_=0.3) -> bs4.BeautifulSoup:
    """
    https://curlconverter.com/ may help for auto generating params and headers.
    Be careful of leaking your cookies to this site。

    eg:
        params = {
            'searchtype': '2',
            'page_index': '1',
            ...
            'zoneId': '',
            'pppStatus': '0',
            'agentName': '',
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            # 'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Sec-GPC': '1',
        }
    """
    time.sleep(sleep_)
    response = requests.get(url, params=params, headers=headers)
    return BeautifulSoup(response.content, "html.parser")


def download_html(url_, path_):
    """
    从服务器下载html，将其存放在当前文件夹下
    便于本地BeautifulSoup调试

    # BeautifulSoup解析本地html
    soup = BeautifulSoup(open("data.html",encoding="utf-8"), 'lxml')

    :param url_: 进行下载网页的url
    :return:
    """
    req = urllib.request.Request(url_)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36')  # set user-agent header
    # req.add_header('Cookie', 'UM_dis3aa97')  # 更改cookie
    response = urllib.request.urlopen(req)
    # 获得当前路径
    # path = os.getcwd() + '/data.html'
    p = Path('')
    path = p.joinpath(path_)
    fo = open(path, "wb")
    fo.write(response.read())
    fo.close()


def to_html_by_response(response, name="data.html"):
    """
    :param name:
    :param response: type: http.client.HTTPResponse
    :return:
    """
    path = os.getcwd() + f'{name}'
    fo = open(path, "wb")
    fo.write(response.read())
    fo.close()


def bs4_local_html(filename) -> bs4.BeautifulSoup:
    with open(filename, 'rb') as f:
        doc_html = f.read()
    return BeautifulSoup(doc_html, "html.parser")




'''
http://docs.python-requests.org/en/master/
'''
class Downloader(object):
    def __init__(self):
        self.request_session = requests.session()
        self.request_session.proxies

    def download(self,filename, url, retry_count=3, headers=None, proxies=None, data=None)->bool:
        '''
        :param url: 准备下载的 URL 链接
        :param retry_count: 如果 url 下载失败重试次数
        :param headers: http header={'X':'x', 'X':'x'}
        :param proxies: 代理设置 proxies={"https": "http://12.112.122.12:3212"}
        :param data: 需要 urlencode(post_data) 的 POST 数据
        :return: 网页内容或者 None
        '''
        if headers:
            self.request_session.headers.update(headers)
        try:
            if data:
                content = self.request_session.post(url, data, proxies=proxies).content
            else:
                content = self.request_session.get(url, proxies=proxies).content
        except (ConnectionError, Timeout) as e:
            print('Downloader download ConnectionError or Timeout:' + str(e))
            content = None
            if retry_count > 0:
                self.download(url, retry_count - 1, headers, proxies, data)
        except Exception as e:
            print('Downloader download Exception:' + str(e))
            content = None
        
        try:
            with open(filename,'wb+') as f:
                f.write(content)
                f.close()
                return True
        except:
            return False
    
