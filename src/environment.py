#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import sys

ENV_JSON = 'env.json'

def generate_environment(directory, profile='staging'):
    fcnf_path = os.path.join(directory, 'info.json')
    env_path = os.path.join(directory, ENV_JSON)
    with open(fcnf_path, 'r') as f: fconf = json.load(f)
    with open(env_path, 'w') as f: json.dump(fconf[profile], f)
    print 'Generated %s (%s)' % (env_path, profile)

def prepare_environment(profile):
    lambdas = []
    src_path = os.path.abspath(os.path.dirname(__file__))

    for d in os.listdir(src_path):
        func_dir = os.path.join(src_path, d)

        if os.path.isdir(func_dir):
            gensh_path = os.path.join(func_dir, 'generate.sh')
            fcnf_path = os.path.join(func_dir, 'info.json')

            if os.path.exists(gensh_path) and os.path.exists(fcnf_path):
                generate_environment(func_dir, profile=profile)


class Env():
    env = None
    def __init__(self, lambda_file_path):
        env_path = os.path.join(os.path.dirname(lambda_file_path), ENV_JSON)
        with open(env_path) as env: self.env = json.load(env)


    def get(self, key):
        return self.env['lambda_variable'][key] if key in self.env['lambda_variable'] else None


if __name__ == '__main__':
    if (len(sys.argv) > 1 and sys.argv[1] == 'production'):
        print('found production')
        profile = 'production'
    else:
        print('using default staging')
        profile = 'staging'
    prepare_environment(profile)
