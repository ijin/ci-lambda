#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
from boto3.s3.transfer import TransferConfig, S3Transfer
import os
import time
import subprocess
import json
import hashlib
import sys

MB = 1024 * 1024
S3_BUCKET = os.environ.get('S3_BUCKET', 'rq1-nobita-log-test-bucket')
SUB_KEY = 'lambda_functions'
S3_FILENAME = 'lambda.zip'
LOCAL_FILENAME = 'lambda.zip'
S3_CHUNK_SIZE = 8 * MB

LAMBDA_MEMORY_SIZE = [128, 192, 256, 320, 384, 448, 512, 576, 640, 704, 768, 832,
                      896, 960, 1024, 1088, 1152, 1216, 1280, 1344, 1408, 1472, 1536]

LAMBDA_EXEC_ROLE = os.environ.get('LAMBDA_EXEC_ROLE', 'arn:aws:iam::477957410617:role/richard_test_role_container')
LAMBDA_DESC = 'Lambda Function from Garden installer'
LAMBDA_MEMORY = 128
LAMBDA_TIMEOUT = 30


def _wrap_with(code):
    def inner(text, bold=False):
        c = code
        if bold: c = "1;%s" % c
        return "\033[%sm%s\033[0m" % (c, text)
    return inner

red = _wrap_with('31')
green = _wrap_with('32')
yellow = _wrap_with('33')
blue = _wrap_with('34')
magenta = _wrap_with('35')
cyan = _wrap_with('36')
white = _wrap_with('37')
black = _wrap_with('30')


def exist_lambda(function_name):
    already_exist_lambdas = []
    lmd = boto3.client('lambda', region_name='ap-northeast-1')
    for func in lmd.list_functions()['Functions']:
        already_exist_lambdas.append(func['FunctionName'])
    return function_name in already_exist_lambdas


def md5(filename):
    with open(filename, "rb") as f: data = f.read()
    return hashlib.md5(data).hexdigest()


def multipart_md5(filename):
    digests = ''
    with open(filename) as f:
        while True:
            k = f.read(S3_CHUNK_SIZE)
            if k == '': break
            else:
                digests += (hashlib.md5(k).digest())
    return hashlib.md5(digests).hexdigest()


def get_s3_md5(s3_bucket, filename):
    s3 = boto3.client('s3')
    next_page = ''
    key_path_list = []

    while True:
        lis = s3.list_objects(Bucket=s3_bucket, Delimiter='/', MaxKeys=20, Prefix=filename, Marker=next_page)
        if 'Contents' in lis:
            key_path_list.extend(map(lambda l: l['Key'], lis['Contents']))
        next_page = lis['NextMarker'] if ('NextMarker' in lis) else None
        if next_page is None: break

    return s3.get_object(Bucket=s3_bucket, Key=filename).get('ETag', 'NOT_EXIST_S3_OBJECT').replace('"', '') if filename in key_path_list else 'NOT_EXIST_S3_OBJECT'


def generate_zip():
    lambdas = []

    print ''
    print yellow('='*15 + 'GENERATE LAMBDA ZIP PACKAGE' + '='*15)

    src_path = os.path.abspath(os.path.dirname(__file__))
    for d in os.listdir(src_path):
        if os.path.isdir(d):
            gensh_path = os.path.join(d, 'generate.sh')
            fcnf_path = os.path.join(d, 'env.json')
            abs_dir = os.path.abspath(d)
            print(abs_dir)

            if os.path.exists(gensh_path) and os.path.exists(fcnf_path):
                os.environ['PATH'] += ':' + os.path.abspath(os.path.dirname(__file__))
                subprocess.call(['bash', gensh_path])

                with open(fcnf_path, 'r') as f: fconf = json.load(f)

                info = {}
                info['zip_path'] = os.path.join(abs_dir, LOCAL_FILENAME)
                info['s3key'] = '%s/%s/%s' % (SUB_KEY, d, S3_FILENAME)
                info['function_name'] = fconf['lambda_config']['function_name']
                info['handler'] = fconf['lambda_config']['handler']
                info['description'] = fconf['lambda_config']['description'] if 'description' in fconf['lambda_config'] else LAMBDA_DESC
                info['role'] = fconf['lambda_config']['role'] if 'role' in fconf['lambda_config'] else LAMBDA_EXEC_ROLE
                info['vpc_config'] = fconf['lambda_config']['vpc_config'] if 'vpc_config' in fconf['lambda_config'] else {'SubnetIds': [], 'SecurityGroupIds': []}

                if 'memory_size' in fconf['lambda_config']:
                    memory_size = LAMBDA_MEMORY
                    conf_size = int(fconf['lambda_config']['memory_size'])
                    for size in LAMBDA_MEMORY_SIZE:
                        if conf_size >= size: memory_size = size
                        else: break
                    info['memory_size'] = memory_size
                else:
                    info['memory_size'] = LAMBDA_MEMORY

                if 'function_timeout' in fconf['lambda_config']:
                    info['function_timeout'] = min([260, max([int(fconf['lambda_config']['function_timeout']), 1])])
                else:
                    info['function_timeout'] = LAMBDA_TIMEOUT

                info['zip_md5'] = md5(info['zip_path'])
                info['zip_multipart_md5'] = multipart_md5(info['zip_path'])
                info['s3_md5'] = get_s3_md5(S3_BUCKET, info['s3key'])
                info['is_latest'] = (info['zip_md5'] == info['s3_md5']) or (info['s3_md5'].split('-')[0] == info['zip_multipart_md5'])

                lambdas.append(info)
    return lambdas

def upload_zip(lambdas):
    print ''
    print yellow('='*15 + 'UPLOAD_LAMBDA_ZIP_PACKAGE' + '='*15)

    client = boto3.client('s3')
    config = TransferConfig(multipart_threshold= 32*MB, multipart_chunksize= S3_CHUNK_SIZE)
    s3 = S3Transfer(client, config)

    for zf in lambdas:
        zip_path = zf['zip_path']
        s3_key = zf['s3key']
        is_latest = zf['is_latest']

        if is_latest:
            print '%s is latest' % (s3_key)
        else:
            s3.upload_file(zip_path, S3_BUCKET, s3_key)
            print 'UPLOAD %s ---> %s' % (zip_path, s3_key)

        print 'S3 MD5 : %s' % zf['s3_md5']
        print 'ZIPMP5 : %s' % zf['zip_multipart_md5']
        print 'ZIPMD5 : %s' % zf['zip_md5']


def update_lambda(lambdas):
    print ''
    print yellow('='*15 + 'CREATE/UPDATE LAMBDA' + '='*15)

    lmd = boto3.client('lambda', region_name='ap-northeast-1')

    for l in lambdas:
        commit_hash = os.environ.get('CIRCLE_SHA1', "NOCOMMIT")
        ci_build_number = os.environ.get('CIRCLE_BUILD_NUM', 99999)
        alias_name = '%05d_%s' % (int(ci_build_number), commit_hash[0:8])

        if not exist_lambda(l['function_name']):
            print('not exist!')
            print(l['function_name'])
            res = lmd.create_function(FunctionName=l['function_name'],
                                      Runtime='python2.7',
                                      Handler=l['handler'],
                                      Code={
                                          'S3Bucket': S3_BUCKET,
                                          'S3Key':l['s3key']
                                      },
                                      Role=LAMBDA_EXEC_ROLE,
                                      Timeout=l['function_timeout'],
                                      Description=l['description'],
                                      VpcConfig=l['vpc_config'],
                                      Publish=True)
            print 'CREATED NEW LAMBDA FUNCTION %s (VERSION:%s as %s)' % (l['function_name'], res['Version'], alias_name)

        else:
            lmd.update_function_configuration(FunctionName=l['function_name'], Role=l['role'],
                                              Handler=l['handler'], Description=l['description'],
                                              Timeout=l['function_timeout'], MemorySize=l['memory_size'], VpcConfig=l['vpc_config'])
            res = lmd.update_function_code(FunctionName=l['function_name'], S3Bucket=S3_BUCKET, S3Key=l['s3key'], Publish=True)
            print 'UPDATE LAMBDA CODE %s (VERSION:%s as %s)' % (l['function_name'], res['Version'], alias_name)

        lmd.create_alias(FunctionName=l['function_name'], Name=alias_name, FunctionVersion=res['Version'])



if __name__ == '__main__':
    branch_name = os.environ.get('CIRCLE_BRANCH')
    if branch_name: S3_FILENAME = '%s_lambda.zip' % branch_name
    print cyan('USE %s as a S3_FILENAME' % S3_FILENAME)

    lz = generate_zip()
    upload_zip(lz)
    update_lambda(lz)
    print green('Done!')

