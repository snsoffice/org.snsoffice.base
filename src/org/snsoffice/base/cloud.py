# -*- coding: utf-8 -*-
"""https://developer.qiniu.com/kodo/sdk/1242/python"""

from org.snsoffice.base import _

from qiniu import Auth, put_data, build_batch_delete, Auth, BucketManager
import qiniu.config

access_key = 'QFgSb93d8-jgKpKmqnXPsIb2CntjxmZJOo7mZpOg'
secret_key = '_AOrXX3Y05HwCdXk-dfl816HJnX8eecYN2KHk2xP'

def makeToken(bucket_name, key_prefix):
    q = Auth(access_key, secret_key)
    policy = {
        'scope': bucket_name + ':' + key_prefix, 
        'isPrefixalScope': 1,
    }
    #3600为token过期时间，秒为单位。3600等于一小时
    return q.upload_token(bucket_name, key_prefix, 3600, policy)

def uploadData(data, bucket_name, key):
    q = Auth(access_key, secret_key)
    token = q.upload_token(bucket_name, key, 3600)
    ret, info = put_data(token, key, data)

def listCloudResource(bucket_name, prefix, limit=30):
    q = Auth(access_key, secret_key)
    bucket = BucketManager(q)
    # 列举出除'/'的所有文件以及以'/'为分隔的所有前缀
    delimiter = None
    # 标记
    marker = None
    ret, eof, info = bucket.list(bucket_name, prefix, marker, limit, delimiter)
    print(info)
    assert len(ret.get('items')) is not None
    return [(prefix + '/' + x['key']) for x in ret['items']]

def deleteCloudResource(bucket_name, key):
    #初始化Auth状态
    q = Auth(access_key, secret_key)
    #初始化BucketManager
    bucket = BucketManager(q)
    #删除bucket_name 中的文件 key
    ret, info = bucket.delete(bucket_name, key)
    print(info)
    assert ret == {}

def batchDeleteCloudResource(bucket_name, key):
    q = Auth(access_key, secret_key)
    bucket = BucketManager(q)
    ops = build_batch_delete(bucket_name, keys)
    ret, info = bucket.batch(ops)
    print(info)
