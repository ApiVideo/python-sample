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

def login(apiKey):
	global headers
	payload = {"apiKey": apiKey}
	response = requests.request("POST", "/auth/api-key", data=json.dumps(payload), headers=headers)
	jsonResponse = response.json()
	headers = {'content-type': 'application/json', 'Authorization': 'Bearer '+jsonResponse['access_token']}

def video():
	global headers
	payload =  {"title": "Test"}
	response = requests.request("POST", "/videos", data=json.dumps(payload), headers=headers)
	jsonResponse = response.json()
	return jsonResponse

def patch(videoJson):
	global headers
	if 'content-type' not in headers:
		headers['content-type'] = 'application/json'
	videoId = videoJson['videoId']
	payload =  {"description": "Test description"}
	response = requests.request("PATCH", "/videos/"+videoId, data=json.dumps(payload), headers=headers)
	jsonResponse = response.json()
	return jsonResponse

def upload(videoJson, source):
	global headers
	uriUpload = videoJson['source']['uri']
	file = {'file': open(source, 'rb')}
	if 'content-type' in headers:
		del headers['content-type']
	response = requests.request("POST", uriUpload, files=file, headers=headers)
	jsonResponse = response.json()
	videoId = jsonResponse['videoId']
	return videoId

def uploadByChunk(videoJson, source):
	global headers
	uriUpload = videoJson['source']['uri']

	if 'content-type' in headers:
		del headers['content-type']

	content_size = os.stat(source).st_size
	headers['Expect'] = '100-Continue'
	headers['Content-Type'] = 'application/octet-stream'
	headers['Content-Disposition'] = 'form-data'
	file = open(source)
	index=0
	offset=0

	for chunk in read_in_chunks(file):
		offset = index + len(chunk)
		headers['Content-Range'] = 'bytes %s-%s/%s' % (index, offset, content_size)
		index = offset
		try:
			response = requests.request("POST", uriUpload, files={'file': chunk}, headers=headers)
			print response.status_code
			print response.content
		except Exception, e:
			print e

def getVideo(videoId):
	global headers
	if 'content-type' not in headers:
		headers['content-type'] = 'application/json'
	response = requests.request("GET", "/videos/"+videoId, headers=headers)
	jsonResponse = response.json()


def deleteVideo(videoId):
	global headers
	if 'content-type' not in headers:
		headers['content-type'] = 'application/json'
	response = requests.request("DELETE", "/videos/"+videoId, headers=headers)


def listWithoutPaginate():
	global headers
	if 'content-type' not in headers:
		headers['content-type'] = 'application/json'
	response = requests.request("GET", "/videos", headers=headers)

def listWithPaginate():
	global headers
	if 'content-type' not in headers:
		headers['content-type'] = 'application/json'
	paginate = {'page': 2, 'pageSize': 25}
	response = requests.request("GET", "/videos", params=paginate, headers=headers)

def listWithPaginateAndOrder():
	global headers
	if 'content-type' not in headers:
		headers['content-type'] = 'application/json'
	paginateOrder = {'page': 2, 'pageSize': 25, 'sortBy': 'publishedAt', 'sortOrder': 'desc'}
	response = requests.request("GET", "/videos", params=paginateOrder, headers=headers)
