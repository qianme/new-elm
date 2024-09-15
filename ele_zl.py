"""
cron: 15 8,20 * * *
new Env('饿了么吃助力');
"""
import hashlib
import json
import os
import time

import requests
from urllib.parse import quote
import datetime

host = 'https://acs.m.goofish.com'

zlck = os.environ.get('ZL_CK', "")
elm_host = open('xsign_host.txt', 'r', encoding='utf-8').read().split("\n")[0]
ck = ""


def get_cookie_map(cookie_string):
    """
    解析为cookie_map
    """
    cookie_pairs = cookie_string.split(";")
    cookie_map = {}
    for pair in cookie_pairs:
        if "=" in pair:
            name, value = pair.split("=", 1)
            cookie_map[name.strip()] = value.strip()
        else:
            continue
    return cookie_map


def map_to_cookie_string(cookie_map):
    """
    将cookie_map还原为cookie
    """
    cookie_string = ""
    for key, value in cookie_map.items():
        cookie_string += f"{key}={value};"
    return cookie_string.strip()


def hbh5tk(tk_cookie, enc_cookie, cookie_str):
    """
    合并带_m_h5_tk
    """
    txt = cookie_str.replace(" ", "")
    if txt[-1] != ';':
        txt += ';'
    cookie_parts = txt.split(';')[:-1]
    updated = False
    for i, part in enumerate(cookie_parts):
        key_value = part.split('=')
        if key_value[0].strip() in ["_m_h5_tk", " _m_h5_tk"]:
            cookie_parts[i] = tk_cookie
            updated = True
        elif key_value[0].strip() in ["_m_h5_tk_enc", " _m_h5_tk_enc"]:
            cookie_parts[i] = enc_cookie
            updated = True

    if updated:
        return ';'.join(cookie_parts) + ';'
    else:
        return txt + tk_cookie + ';' + enc_cookie + ';'


def tq(cookie_string):
    """
    获取_m_h5_tk
    """
    if not cookie_string:
        return '-1'
    cookie_pairs = cookie_string.split(';')
    for pair in cookie_pairs:
        key_value = pair.split('=')
        if key_value[0].strip() in ["_m_h5_tk", " _m_h5_tk"]:
            return key_value[1]
    return '-1'


def tq1(txt):
    """
    拆分cookie
    """
    try:
        txt = txt.replace(" ", "")
        txt = txt.replace("chushi;", "")
        if txt[-1] != ';':
            txt += ';'
        pairs = txt.split(";")[:-1]
        ck_json = {}
        for pair in pairs:
            key, value = pair.split("=", 1)
            ck_json[key] = value
        return ck_json
    except Exception as e:
        print(f'❎Cookie解析错误: {e}')
        return {}


def md5(text):
    """
    md5加密
    """
    hash_md5 = hashlib.md5()
    hash_md5.update(text.encode())
    return hash_md5.hexdigest()


def check_cookie(cookie):
    url = "https://waimai-guide.ele.me/h5/mtop.alsc.personal.queryminecenter/1.0/?jsv=2.6.2&appKey=12574478"
    headers = {
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            cookie_jar = response.cookies
            token = cookie_jar.get('_m_h5_tk', '')
            token_cookie = "_m_h5_tk=" + token
            enc_token = cookie_jar.get('_m_h5_tk_enc', '')
            enc_token_cookie = "_m_h5_tk_enc=" + enc_token
            cookie = hbh5tk(token_cookie, enc_token_cookie, cookie)
            return cookie
        else:
            return None
    except Exception as e:
        print("解析ck错误")
        return None


class LYB:
    def __init__(self, cki):
        self.cookie = cki
        self.ck1 = tq1(cki)
        self.uid = self.ck1.get("unb")
        self.sid = self.ck1.get("cookie2")
        self.name = self.uid

    def xsign(self, api, data, wua, v):
        url = elm_host
        body = {
            "data": data,
            "api": api,
            "pageId": '',
            "uid": self.uid,
            'sid': self.sid,
            "deviceId": '',
            "utdid": '',
            "wua": wua,
            'ttid': '1551089129819@eleme_android_10.14.3',
            "v": v
        }

        max_retries = 5
        retries = 0
        while retries < max_retries:
            try:
                r = requests.post(url, json=body, timeout=9)
                return r.json()
            except requests.exceptions.HTTPError as e:
                print(f'❎请求签名服务器失败: {e}')
            except requests.exceptions.Timeout:
                print("❎签名接口请求超时")
            except requests.exceptions.RequestException as e:
                print(f'❎请求签名服务器错误: {e}')
            retries += 1
            print(f"❎重试次数: {retries}")
            if retries >= max_retries:
                print("❎尝试次数上限,哦豁，签名通道不可用！")
                return None

    def req(self, api, data, wua='False', v="1.0"):
        try:
            if type(data) == dict:
                data = json.dumps(data)
            wua = str(wua)
            sign = self.xsign(api, data, wua, v)
            url = f"{host}/gw/{api}/{v}/"
            headers = {
                "x-sgext": quote(sign.get('x-sgext')),
                "x-sign": quote(sign.get('x-sign')),
                'x-sid': self.sid,
                'x-uid': self.uid,
                'x-pv': '6.3',
                'x-features': '1051',
                'x-mini-wua': quote(sign.get('x-mini-wua')),
                'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'x-t': sign.get('x-t'),
                'x-extdata': 'openappkey%3DDEFAULT_AUTH',
                'x-ttid': '1551089129819@eleme_android_10.14.3',
                'x-utdid': '',
                'x-appkey': '24895413',
                'x-devid': '',
            }

            params = {"data": data}
            if 'wua' in sign:
                params["wua"] = sign.get('wua')

            max_retries = 5
            retries = 0
            while retries < max_retries:
                try:
                    res = requests.post(url, headers=headers, data=params, timeout=15)
                    return res
                except requests.exceptions.Timeout:
                    print("❎接口请求超时")
                except requests.exceptions.RequestException as e:
                    print(f"❎请求异常: {e}")
                retries += 1
                print(f"❎重试次数: {retries}")
                if retries >= max_retries:
                    print("❎重试次数上限")
                    return None
        except Exception as e:
            print(f'❎请求接口失败: {e}')
            return None

    def req1(self, api, data, v="1.0"):
        try:
            cookie = check_cookie(self.cookie)
            timestamp = int(time.time() * 1000)
            data_str = json.dumps(data)
            token = tq(cookie)
            token_part = token.split("_")[0]

            sign_str = f"{token_part}&{timestamp}&12574478&{data_str}"
            sign = md5(sign_str)
            url = f"https://guide-acs.m.taobao.com/h5/{api}/{v}/?jsv=2.6.1&appKey=12574478&t={timestamp}&sign={sign}&api={api}&v={v}&type=originaljson&dataType=json"
            headers = {
                "authority": "shopping.ele.me",
                "accept": "application/json",
                "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
                "cookie": cookie,
                "user-agent": "Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36"
            }
            max_retries = 5
            retries = 0
            while retries < max_retries:
                try:
                    r = requests.post(url, headers=headers, data={'data': data_str})
                    return r
                except requests.exceptions.Timeout:
                    print("❎接口请求超时")
                except requests.exceptions.RequestException as e:
                    print(f"❎请求异常: {e}")
                retries += 1
                print(f"❎重试次数: {retries}")
                if retries >= max_retries:
                    print("❎重试次数上限")
                    return None
        except Exception as e:
            print(f'❎请求接口失败: {e}')
            return None

    def yqm(self):
        api = 'mtop.ele.biz.growth.task.core.querytask'
        data = json.dumps({"missionCollectionId": "839",
                           "locationInfos": "[\"{\\\"lng\\\":\\\"105.75325090438128\\\",\\\"lat\\\":\\\"30.597472842782736\\\"}\"]",
                           "bizScene": "game_center", "accountPlan": "HAVANA_COMMON"})
        try:
            res = self.req(api, data, 'False' "1.0")
            if res.json()["ret"][0] == "SUCCESS::接口调用成功":
                for y in res.json()['data']['mlist']:
                    if y['name'] == "邀请好友助力":
                        actId = y['actionConfig']['ext']['actId']
                        ShareId = y['actionConfig']['ext']['shareId']
                        return actId, ShareId
            else:
                if res.json()["ret"][0] == "FAIL_SYS_SESSION_EXPIRED::Session过期":
                    print("❎cookie已过期，请重新获取")
                    return None, None
                else:
                    print(res.text)
                    return None, None
        except Exception:
            print(f'❎请求错误')
            return None, None

    def share(self, actid1, shareId1):
        api = 'mtop.koubei.interactioncenter.share.common.triggershare'
        data = {"actId": actid1, "shareId": shareId1, "bizScene": "DEFAULT", "requestId": "1719848804784"}
        try:
            res = self.req1(api, data, "1.0")
            if res is None:
                return None
            if res.json()["ret"][0] == "SUCCESS::调用成功":
                print(f"[{self.name}] ✅助力成功")
                return True
            else:
                if res.json()["ret"][0] == "FAIL_SYS_SESSION_EXPIRED::Session过期":
                    print(f"[{self.name}] ❎cookie已过期，请重新获取")
                    return False
                else:
                    if res.json()["data"]['errorMsg'] == "助力次数已用完":
                        print(f"[{self.name}] ❎助力次数已用完")
                        return False
                    if res.json()["data"]['errorMsg'] == "今日助力次数已用完":
                        print(f"[{self.name}] ❎哦豁，莫得次数咯")
                        return False
                    if res.json()["data"]['errorMsg'] == " 人传人关系已达上限":
                        print(f"[{self.name}] ❎助力上限\n")
                        return 'SX'
                    if res.json()["data"]['errorMsg'] == "分享者已被助力成功，客态重复助力":
                        print(f"[{self.name}] ❎重复助力")
                        return None
                    else:
                        print(f"[{self.name}] ❎助力失败")
                        print(res.text)
                        return None
        except Exception:
            print(f'请求错误')
            return None

    def prize(self):
        api1 = 'mtop.ele.biz.growth.task.core.querytask'
        data1 = {"missionCollectionId": "839",
                 "locationInfos": "[\"{\\\"lng\\\":\\\"105.75325090438128\\\",\\\"lat\\\":\\\"30.597472842782736\\\"}\"]",
                 "bizScene": "game_center", "accountPlan": "HAVANA_COMMON"}
        try:
            res1 = self.req(api1, data1, 'False', "1.0")
            if res1 is None:
                return None
            if res1.json()["ret"][0] == "SUCCESS::接口调用成功":
                for y in res1.json()['data']['mlist']:
                    if y['name'] == "邀请好友助力":
                        for o in y['missionStageDTOS']:
                            if o['rewardStatus'] == "TODO" and o['status'] == "FINISH":
                                api = 'mtop.ele.biz.growth.task.core.receiveprize'
                                data2 = {
                                    "missionCollectionId": "839",
                                    "missionId": "20544001",
                                    "count": o['stageCount']
                                }
                                try:
                                    res = self.req1(api, data2, "1.0")
                                    if res is None:
                                        continue
                                    data = res.json()["data"]
                                    if data.get('errorMsg') is not None:
                                        print(f"[{self.name}] ❎领取奖励失败: {data['errorMsg']}")
                                    else:
                                        rlist = data.get('rlist')
                                        if rlist is not None:
                                            print(f"[{self.name}] ✅领取奖励成功--{rlist[0]['value']}乐园币")
                                        else:
                                            print(f"[{self.name}] ❎{res.json()['ret'][0]}")
                                except Exception:
                                    print(f'请求错误')
                                    return None
            else:
                if res1.json()["ret"][0] == "FAIL_SYS_SESSION_EXPIRED::Session过期":
                    print(f"[{self.name}] ❎cookie已过期，请重新获取")
                else:
                    print(f"[{self.name}] ❎获取列表失败:", res1.json()["data"]['errorMsg'])
        except Exception:
            print(f'请求错误')
            return None


def get_ck_usid(ck1):
    try:
        key_value_pairs = ck1.split(";")
        for pair in key_value_pairs:
            key, value = pair.split("=")
            if key.lower() == "unb":
                return value
    except Exception:
        return 'y'


if __name__ == '__main__':
    today = datetime.date.today()
    today_str = today.strftime('%Y%m%d')
    filename = f'{today_str}.json'
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({}, f)
        print("今日助力json文件不存在，已创建")
    else:
        print("今日助力json文件已存在")

    with open(filename, 'r') as file:
        data = json.load(file)

    if 'elmck' in os.environ:
        cookie = os.environ.get('elmck')
    else:
        print("❎环境变量中不存在[elmck],启用本地变量模式")
        cookie = ck
    if cookie == "":
        print("❎本地变量为空，请设置其中一个变量后再运行")
        exit(-1)
    
    cookies = cookie.split("&")

    zlck_list = zlck.split("&")
    print(f"获取到 {len(zlck_list)} 个被助力账号")

    dzl_num = 0
    for zlck in zlck_list:
        dzl_num += 1
        lyb = LYB(zlck)
        nm = get_ck_usid(zlck)
        actid, shareId = lyb.yqm()
        print(actid)
        if actid is None or shareId is None:
            print("❎获取助力id失败")
        else:
            print(f"======被助力账号[{dzl_num}]--[{nm}]获取邀请码成功,开始助力======")
            for i, ck in enumerate(cookies):
                if ck == zlck:
                    continue
                ck = ck.replace("chushi;", "")
                usid = get_ck_usid(ck)
                zlcs = data.get(f"{usid}", 0)
                if zlcs < 3:
                    print(f"======被助力账号[{dzl_num}]--[{nm}]-开始第{i + 1}/{len(cookies)}个账号助力======")
                    a = LYB(ck).share(actid, shareId)
                    if a == 'SX':
                        break
                    elif a:
                        data[f"{usid}"] = zlcs + 1
                        with open(filename, 'w') as file:
                            json.dump(data, file, indent=4)
                        print("2s后进行下一个账号")
                        continue
                    elif a is False:
                        data[f"{usid}"] = 3
                        with open(filename, 'w') as file:
                            json.dump(data, file, indent=4)
                        print("2s后进行下一个账号")
                        continue
                    else:
                        print("2s后进行下一个账号")
                        continue
                else:
                    continue
        print(f"======被助力账号{nm}-领取奖励======")
        lyb.prize()
        print(f"======被助力账号{nm}-助力结束======\n\n")
