#!/bin/bash
# set -e

aws sts assume-role --role-arn arn:aws:iam::908699337798:role/role-to-be-assumed --role-session-name ijin-assumed > /tmp/sts.json; export AWS_ACCESS_KEY=`cat /tmp/sts.json | jq -r .Credentials.AccessKeyId`; export AWS_SECRET_KEY=`cat /tmp/sts.json | jq -r .Credentials.SecretAccessKey`; export AWS_SESSION_TOKEN=`cat /tmp/sts.json | jq -r .Credentials.SessionToken`; export  AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY; export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_KEY
rm -rf /tmp/sts.json
