#!/usr/bin/env python27
# -*- coding: utf-8 -*-

import os, sys
from environment import Env

def main(event, context):
    return Env(__file__).get('version')
