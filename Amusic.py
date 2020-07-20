import json
import random
import re
import time
from urllib import parse

import requests


# 解析jsonp数据格式为json
def loads_jsonp(_jsonp):
    try:
        return json.loads(re.match(".*?({.*}).*", _jsonp, re.S).group(1))
    except:
        raise ValueError('Invalid Input')


def get_xima_music_parm(music_url):
    print("开始获取喜马拉雅的参数")
    # 将%xx转义符替换为它们的单字符等效项
    url_data = parse.unquote(music_url)

    # url结果
    result = parse.urlparse(url_data)
    print(result)

    song_id = result.path.rsplit('/', 1)[1]
    print(song_id)

    url = "https://m.ximalaya.com/tracks/" + song_id + ".json"

    headers = {
        'Host': "m.ximalaya.com",
        'Accept-Encoding': "gzip, deflate",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers)
    print(response.text)

    music_data = json.loads(response.text)
    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", music_data["title"])
    print(music_name)
    play_path_64 = music_data["play_path_64"]

    music_parm = [music_name, play_path_64]
    return music_parm


def get_changba_music_parm(music_url):
    print("开始获取唱吧的参数")
    html = requests.get(music_url).text

    title_res = re.search(r'<div class="title">(?P<title>[\s\S]*?)</div>', html)
    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", title_res.groupdict()['title'])
    print(music_name)
    work_id_res = re.search(r'<span class="fav" data-workid="(?P<work_id>[\s\S]*?)" data-status="0">', html)
    work_id = work_id_res.groupdict()['work_id']
    mp3_url = "http://qiniuuwmp3.changba.com/" + work_id + ".mp3"

    music_parm = [music_name, mp3_url]
    return music_parm


# （已发现缺陷）打印日志不全，文件头过长，不过文件转换没有问题
def get_lizhi_music_parm(music_url):
    print("开始获取荔枝的参数")
    # 将%xx转义符替换为它们的单字符等效项
    url_data = parse.unquote(music_url)

    # url结果
    result = parse.urlparse(url_data)
    print(result)

    song_id = result.path.rsplit('/', 1)[1]
    print(song_id)

    url = "https://m.lizhi.fm/vodapi/voice/info/" + song_id

    headers = {
        'Host': "m.lizhi.fm",
        'Accept-Encoding': "gzip, deflate",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers)
    print(response.text)

    music_data = json.loads(response.text)["data"]
    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", music_data["userVoice"]["voiceInfo"]["name"])
    print(music_name)
    track_url = music_data["userVoice"]["voicePlayProperty"]["trackUrl"]

    music_parm = [music_name, track_url]
    return music_parm


def get_changya_music_parm(music_url):
    print("开始获取唱鸭的参数")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
    }
    html = requests.request("GET", music_url, headers=headers).text

    song_json_res = re.search(
        r'<script id="__NEXT_DATA__" type="application/json" crossorigin="anonymous">(?P<song_json>[\s\S]*?)</script>',
        html)
    song_data = song_json_res.groupdict()['song_json'].strip()
    music_data = json.loads(song_data)["props"]["pageProps"]["clip"]

    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", music_data["songName"])
    print(music_name)
    mp3_url = music_data["audioSrc"]

    music_parm = [music_name, mp3_url]
    return music_parm


def get_changya2_music_parm(music_url):
    print("开始获取唱鸭2的参数")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
    }
    html = requests.request("GET", music_url, headers=headers).text

    song_json_res = re.search(
        r'<script id="__NEXT_DATA__" type="application/json" crossorigin="anonymous">(?P<song_json>[\s\S]*?)</script>',
        html)
    song_data = song_json_res.groupdict()['song_json'].strip()
    mp4_url = json.loads(song_data)["props"]["pageProps"]["url"]

    music_name = "changya" + str(int(round(time.time() * 1000)))
    print(music_name)

    music_parm = [music_name, mp4_url]
    return music_parm


def get_kugouchang_music_parm(music_url):
    print("开始获取酷狗唱唱和斗歌的参数")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
    }
    res = requests.request("GET", music_url, headers=headers, allow_redirects=False)
    location_url = res.headers["Location"]
    pre_location_url = location_url.split('?')[0]
    slash_location_url = pre_location_url.rsplit('/', 1)[1]
    req_parm = slash_location_url.split('-')
    data = req_parm[1][4:]
    sign = req_parm[3][4:]

    url = "https://acsing.service.kugou.com/sing7/web/jsonp/cdn/opus/listenGetData?data=" + data + "&sign=" + sign + "&channelId=0"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers)

    music_data = json.loads(response.text.encode('utf8'))["data"]

    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", music_data["opusName"])
    print(music_name)
    opus_url = music_data["opusUrl"]

    music_parm = [music_name, opus_url]
    return music_parm


def get_kg_music_parm(music_url):
    print("开始获取全民K歌的参数")
    # 将%xx转义符替换为它们的单字符等效项
    url_data = parse.unquote(music_url)

    # url结果
    result = parse.urlparse(url_data)
    print(result)

    # url里的查询参数
    query_dict = parse.parse_qs(result.query)
    s_id = query_dict["s"]
    print(s_id)

    url = "https://cgi.kg.qq.com/fcgi-bin/kg_ugc_getdetail"

    querystring = {"inCharset": "GB2312", "outCharset": "utf-8", "v": "4", "shareid": s_id,
                   "_": str(int(round(time.time() * 1000)))}

    headers = {
        'Host': "cgi.kg.qq.com",
        'Accept-Encoding': "gzip, deflate",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    music_data = loads_jsonp(response.text)["data"]
    print(music_data["song_name"] + ".m4a")
    play_url = "http://node.kg.qq.com/cgi/fcgi-bin/fcg_get_play_url?shareid=" + s_id[0]
    print(play_url)
    print(music_data["playurl"])
    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", music_data["song_name"])
    music_parm = [music_name, play_url]
    return music_parm


def get_maozhua_music_parm(music_url):
    print("开始获取猫爪弹唱的参数")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
    }
    html = requests.request("GET", music_url, headers=headers).text

    song_media_res = re.search(r'media:(?P<song_media>[\s\S]*?),', html)
    song_media = song_media_res.groupdict()['song_media'].strip().strip("\"")
    mp4_url = song_media.replace("\\u002F", "/")

    music_name = "maozhua" + str(int(round(time.time() * 1000)))
    print(music_name)

    music_parm = [music_name, mp4_url]
    return music_parm


def get_tanchang_music_parm(music_url):
    print("开始获取弹唱达人的参数")
    # 将%xx转义符替换为它们的单字符等效项
    url_data = parse.unquote(music_url)

    # url结果
    result = parse.urlparse(url_data)
    print(result)

    # url里的查询参数
    query_dict = parse.parse_qs(result.query)
    works_id = query_dict["worksID"][0]
    print(works_id)

    publisher = query_dict["publisher"][0]
    print(publisher)

    url = "http://res.tc.xfun233.com/musical/h5/share/songs/info?publisher=" + publisher + "&worksId=" + works_id

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers)

    music_data = json.loads(response.text)["result"]
    print(music_data["name"] + ".aac")
    works_url = music_data["worksUrl"]
    print(works_url)
    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", music_data["name"])
    music_parm = [music_name, works_url]
    return music_parm


def get_aichang_music_parm(music_url):
    print("开始获取爱唱的参数")
    music_name = "aichang" + str(int(round(time.time() * 1000)))
    print(music_name)
    music_parm = [music_name, music_url]
    return music_parm


def get_shange_music_parm(music_url):
    print("开始获取闪歌的参数")
    # 将%xx转义符替换为它们的单字符等效项
    url_data = parse.unquote(music_url)

    # url结果
    result = parse.urlparse(url_data)
    print(result)

    # url里的查询参数
    query_dict = parse.parse_qs(result.query)
    song_id = query_dict["id"][0]
    print(song_id)

    url = "http://shange.musiccz.net:6060/product/get?id=" + song_id

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
    }

    response = requests.request("POST", url, headers=headers)

    product_data = json.loads(response.text)["data"]["product"]
    music_url = product_data["url"]
    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", product_data["title"])

    music_parm = [music_name, music_url]
    return music_parm


def get_vv_music_parm(music_url):
    print("开始获取VV音乐的参数")
    # 将%xx转义符替换为它们的单字符等效项
    url_data = parse.unquote(music_url)

    # url结果
    result = parse.urlparse(url_data)
    print(result)

    # url里的查询参数
    query_dict = parse.parse_qs(result.query)
    av_id = query_dict["avId"][0]
    print(av_id)

    url = "http://k.51vv.com/userPage/getAvinfo.htm?parameter={avID:" + av_id + "}&r=" + str(random.random())

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers)

    result_data = json.loads(response.text)["result"]
    music_url = result_data["fileURL"]
    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", result_data["name"])

    music_parm = [music_name, music_url]
    return music_parm


def get_iting_music_parm(music_url):
    print("开始获取爱听的参数")
    html = requests.get(music_url).text

    title_res = re.search(r'<header class="music_title">(?P<title>[\s\S]*?)</header>', html)
    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", title_res.groupdict()['title'])
    print(music_name)
    song_url_res = re.search(r'<input type="hidden" id="ksongUrl" value="(?P<song_url>[\s\S]*?)" />', html)
    mp3_url = song_url_res.groupdict()['song_url']

    music_parm = [music_name, mp3_url]
    return music_parm


def get_kugoudazi_music_parm(music_url):
    print("开始获取酷狗音乐大字版的参数")
    # 将%xx转义符替换为它们的单字符等效项
    url_data = parse.unquote(music_url)

    # url结果
    result = parse.urlparse(url_data)
    print(result)

    # url里的查询参数
    query_dict = parse.parse_qs(result.query)
    data = query_dict["data"][0]
    sign = query_dict["sign"][0]

    url = "https://acsing.service.kugou.com/sing7/web/jsonp/cdn/opus/listenGetData?data=" + data + "&sign=" + sign + "&channelId=0"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers)

    music_data = json.loads(response.text.encode('utf8'))["data"]

    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", music_data["opusName"])
    print(music_name)
    opus_url = music_data["opusUrl"]

    music_parm = [music_name, opus_url]
    return music_parm


def get_kuwokge_music_parm(music_url):
    print("开始获取酷我K歌的参数")
    song_id = music_url.rsplit('/', 1)[1]
    print(song_id)

    base_url = "http://nksingserver.kuwo.cn/nks/mobile/GetWorkBase?id=" + song_id

    base_headers = {
        'User-Agent': 'android-async-http/1.4.3 (http://loopj.com/android-async-http)'
    }

    base_response = requests.request("GET", base_url, headers=base_headers)

    title = json.loads(base_response.text.encode('utf8'))["title"]
    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    song_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", parse.unquote(title))
    print(song_name)

    detail_url = "http://nksingserver.kuwo.cn/nks/mobile/GetWorkDetail?id=" + song_id

    detail_headers = {
        'User-Agent': 'android-async-http/1.4.3 (http://loopj.com/android-async-http)'
    }

    detail_response = requests.request("GET", detail_url, headers=detail_headers)

    temp_url = json.loads(detail_response.text.encode('utf8'))["url"]
    # 将%xx转义符替换为它们的单字符等效项
    aac_url = parse.unquote(temp_url)
    print(aac_url)

    music_parm = [song_name, aac_url]
    return music_parm


def get_qmks_music_parm(music_url):
    print("开始获取全民K诗的参数")
    # 将%xx转义符替换为它们的单字符等效项
    url_data = parse.unquote(music_url)

    # url结果
    result = parse.urlparse(url_data)
    print(result)

    # url里的查询参数
    query_dict = parse.parse_qs(result.query)
    s_id = query_dict["id"][0]
    print(s_id)

    url = "https://ks.weinisongdu.com/shareOpusV3?id=" + s_id
    html = requests.get(url).text

    content_res = re.search(r'var shareContent = (?P<content>[\s\S]*?);', html)
    content_str = content_res.groupdict()['content'].strip()
    music_data = json.loads(content_str)

    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", music_data["title"])
    print(music_name)

    mp3_url = music_data["dataUrl"]
    print(mp3_url)

    music_parm = [music_name, mp3_url]
    return music_parm


def get_all_music_parm(music_url):
    if re.match(r"^((https|http)?:\/\/kg[2-9].qq.com)[^\s]+", music_url) is not None:
        music_parm = get_kg_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/kg.qq.com)[^\s]+", music_url) is not None:
        music_parm = get_kg_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/node.kg.qq.com)[^\s]+", music_url) is not None:
        music_parm = get_kg_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/www.ximalaya.com)[^\s]+", music_url) is not None:
        music_parm = get_xima_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/changba.com)[^\s]+", music_url) is not None:
        music_parm = get_changba_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/www.lizhi.fm)[^\s]+", music_url) is not None:
        music_parm = get_lizhi_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/t.kugou.com)[^\s]+", music_url) is not None:
        music_parm = get_kugouchang_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/changya.i52hz.com/soloShare)[^\s]+", music_url) is not None:
        music_parm = get_changya_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/changya.i52hz.com/user-piece)[^\s]+", music_url) is not None:
        music_parm = get_changya_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/changya.i52hz.com/video)[^\s]+", music_url) is not None:
        music_parm = get_changya2_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/maozhua.xiaochang.com)[^\s]+", music_url) is not None:
        music_parm = get_maozhua_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/res.tc.xfun233.com)[^\s]+", music_url) is not None:
        music_parm = get_tanchang_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/weibo.mengliaoba.cn)[^\s]+", music_url) is not None:
        music_parm = get_aichang_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/shange.musiccz.net)[^\s]+", music_url) is not None:
        music_parm = get_shange_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/k.51vv.com)[^\s]+", music_url) is not None:
        music_parm = get_vv_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/m.imusic.cn)[^\s]+", music_url) is not None:
        music_parm = get_iting_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/activity.kugou.com)[^\s]+", music_url) is not None:
        music_parm = get_kugoudazi_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/kge.kuwo.cn)[^\s]+", music_url) is not None:
        music_parm = get_kuwokge_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/ks.weinisongdu.com)[^\s]+", music_url) is not None:
        music_parm = get_qmks_music_parm(music_url)
    else:
        music_parm = ["null", "null"]

    # music_parm = ['音乐名', '音乐链接']
    return music_parm


def test():
    print("测试函数")


if __name__ == '__main__':
    test()
