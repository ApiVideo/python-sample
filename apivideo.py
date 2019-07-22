try:
    import json
except ImportError:
    import simplejson as json

import requests
import os

headers = {'content-type': 'application/json'}


def read_in_chunks(file_object, chunk_size=10485760):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def login(api_key):
    global headers
    payload = {"apiKey": api_key}
    response = requests.request("POST", "https://ws.api.video/auth/api-key", data=json.dumps(payload), headers=headers)
    json_response = response.json()
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + json_response['access_token']}
    return json_response


def video():
    global headers
    payload = {"title": "Test"}
    response = requests.request("POST", "https://ws.api.video/videos", data=json.dumps(payload), headers=headers)
    json_response = response.json()
    return json_response


def patch(video_json):
    global headers
    if 'content-type' not in headers:
        headers['content-type'] = 'application/json'
    video_id = video_json['videoId']
    payload = {"description": "Test description"}
    response = requests.request("PATCH", "https://ws.api.video/videos/" + video_id, data=json.dumps(payload),
                                headers=headers)
    json_response = response.json()
    return json_response


def upload(video_json, source):
    global headers
    uri_upload = video_json['source']['uri']
    file = {'file': open(source, 'rb')}
    if 'content-type' in headers:
        del headers['content-type']
    response = requests.request("POST", "https://ws.api.video" + uri_upload, files=file, headers=headers)
    json_response = response.json()
    video_id = json_response['videoId']
    return video_id


def upload_by_chunk(video_json, source):
    global headers
    uriUpload = video_json['source']['uri']

    if 'content-type' in headers:
        del headers['content-type']

    content_size = os.stat(source).st_size
    headers['Expect'] = '100-Continue'
    headers['Content-Type'] = 'application/octet-stream'
    headers['Content-Disposition'] = 'form-data'
    file = open(source)
    index = 0
    offset = 0
    lastResponse = None
    for chunk in read_in_chunks(file):
        offset = index + len(chunk)
        headers['Content-Range'] = 'bytes %s-%s/%s' % (index, offset, content_size)
        index = offset
        try:
            response = requests.request("POST", "https://ws.api.video" + uriUpload, files={'file': chunk},
                                        headers=headers)
            lastResponse = response
            print(response.status_code)
            print(response.content)
        except Exception as e:
            print(e)

    return lastResponse.json()


def get_video(video_id):
    global headers
    if 'content-type' not in headers:
        headers['content-type'] = 'application/json'
    response = requests.request("GET", "https://ws.api.video/videos/" + video_id, headers=headers)
    return response.json()


def delete_video(video_id):
    global headers
    if 'content-type' not in headers:
        headers['content-type'] = 'application/json'
    response = requests.request("DELETE", "https://ws.api.video/videos/" + video_id, headers=headers)
    return response.json()


def list_without_paginate():
    global headers
    if 'content-type' not in headers:
        headers['content-type'] = 'application/json'
    response = requests.request("GET", "https://ws.api.video/videos", headers=headers)
    return response.json()


def list_with_paginate():
    global headers
    if 'content-type' not in headers:
        headers['content-type'] = 'application/json'
    paginate = {'page': 2, 'pageSize': 25}
    response = requests.request("GET", "https://ws.api.video/videos", params=paginate, headers=headers)
    return response.json()


def list_with_paginate_and_order():
    global headers
    if 'content-type' not in headers:
        headers['content-type'] = 'application/json'
    paginateOrder = {'page': 2, 'pageSize': 25, 'sortBy': 'publishedAt', 'sortOrder': 'desc'}
    response = requests.request("GET", "https://ws.api.video/videos", params=paginateOrder, headers=headers)
    return response.json()
