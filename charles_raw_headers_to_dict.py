import json
import re
import urllib.parse

from loguru import logger


def raw_http_to_requests_code(raw_http_str):
    """
    解析Charles抓包工具的http报文生成python requests代码
    :param raw_http_str: Charles 抓包 request Raw全选复制即可
    :return: python requests模拟请求代码
    """
    match = re.search(r':path: (.*?)\n', raw_http_str)
    if not match:
        logger.error('未匹配到 path')
        return
    path = match.group(1)
    # 判断请求方式
    match = re.search(r':method: (.*?)\n', raw_http_str)
    if not match:
        logger.error('未匹配到 request method！')
        return
    request_method = match.group(1).upper()
    # 获取请求头部分
    temp_li = raw_http_str.split('\n\n', 1)
    headers_str = temp_li[0]

    # 解析请求头
    headers_str_li = headers_str.split('\n')
    headers_str_li = [i for i in headers_str_li if not i.startswith(':')]
    headers = {}
    for i in headers_str_li:
        k, v = i.split(': ', 1)
        if k.lower() in ['content-length', 'accept-encoding']:
            continue
        headers[k] = v
    # 打印path
    path_li = path.split('?', 1)
    path = path_li[0]
    params = {}
    if len(path_li) > 1:
        # query_params解析
        query_params_str = path_li[1]
        query_params_dict = form_str_to_form_dict(query_params_str)
        if query_params_dict:
            params = query_params_dict
    print(f'host = "此处填写目标网站的域名"')
    print(f'path = "{path}"')
    print(f'url = host + path')
    # 打印params
    print('params = {')
    for k, v in params.items():
        print(f'    "{k}": "{v}",')
    print('}')
    # 打印请求头
    print('headers = {')
    for k, v in headers.items():
        print(f'    "{k}": "{v}",')
    print('}')

    body_str = None
    if request_method in ['GET', ]:
        pass
    elif request_method in ['POST', 'PUT', 'DELETE'] and len(temp_li) > 1:
        # 获取请求体部分
        body_str = temp_li[1]
    else:
        logger.error(f'未适配的 request method: {request_method}')
        return
    if body_str:
        content_type_dict = {
            'application/x-www-form-urlencoded': form_str_to_form_dict,
            'application/json': json_str_to_form_dict,
        }
        # 判断content-type
        content_type = None
        match = re.search(r'(?i)content-type: (.*?)[;\n]', headers_str)
        if match:
            content_type = match.group(1).lower()
        if content_type and (content_type in content_type_dict):
            body_dict = content_type_dict[content_type](body_str)
            # 未读取到content-type尝试解析为json
        else:
            body_dict = json_str_to_form_dict(body_str)
        if body_dict is None:
            body_dict = form_str_to_form_dict(body_str)
        if body_dict is None:
            print(f'data = "{body_str}"')
        else:
            # 打印请求体
            print('data = {')
            for k, v in body_dict.items():
                print(f'    "{k}": "{v}",')
            print('}')
            # 解析失败尝试解析为from
            # 解析失败输出字符串
        print(f'response = requests.{request_method.lower()}(url, params=params, headers=headers, data=data)')
        print(f'print(response.text)')


def form_str_to_form_dict(form_str):
    try:
        return dict(urllib.parse.parse_qsl(form_str))
    except:
        return None


def json_str_to_form_dict(json_str):
    try:
        return json.loads(json_str)
    except:
        return None


if __name__ == '__main__':
    raw_http_str = """:method: POST
:authority: search100-search-quic-lq.amemv.com
:scheme: https
:path: /aweme/v1/search/item/?manifest_version_code=100601&_rticket=1634268005995&app_type=normal&iid=888845654309592&channel=xiaomi&device_type=Pixel%203&language=zh&host_abi=armeabi-v7a&uuid=990012006096793&resolution=1080*2028&openudid=b3ac79237e1b88ee&update_version_code=10609900&cdid=603b58da-b096-4f5a-952f-ff681a0c64df&os_api=28&dpi=440&ac=wifi&device_id=2665648574433789&os_version=9&version_code=100600&app_name=aweme&version_name=10.6.0&device_brand=google&ssmix=a&device_platform=android&aid=1128&ts=1634268019
content-length: 191
cookie: install_id=888845654309592
cookie: ttreq=1$ccc57498c85ec15a17491e610902b50f81f811fd
cookie: odin_tt=9f3263e7d537f31665eb7e263f45fc2927df1de62285347a39ddc2ea81ded59a9ba5a55fe6d6c52041c435366beed57ead01091391447d34daf156a208911052
x-ss-req-ticket: 1634268005993
sdk-version: 1
content-type: application/x-www-form-urlencoded; charset=UTF-8
x-ss-stub: 255F7AF5B3939C6750CC9F68A5C11AEC
x-ss-dp: 1128
x-tt-trace-id: 00-81f6c7ea0d97864ac6009fdda51d0468-81f6c7ea0d97864a-01
user-agent: com.ss.android.ugc.aweme/100601 (Linux; U; Android 9; zh_CN_#Hans; Pixel 3; Build/PQ3A.190605.003; Cronet/TTNetVersion:3154e555 2020-03-04 QuicVersion:8fc8a2f3 2020-03-02)
accept-encoding: gzip, deflate, br
x-khronos: 1634268005
x-gorgon: 040180620401d2bd36b4c93263760e0385d82baa2f74146dca6e

keyword=%E7%8E%8B%E8%80%85%E8%8D%A3%E8%80%80&offset=0&count=10&source=video_search&is_pull_refresh=1&hot_search=0&search_id=&query_correct_type=1&is_filter_search=0&sort_type=0&publish_time=0"""
    raw_http_to_requests_code(raw_http_str)
