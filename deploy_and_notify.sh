#!/bin/bash
set -ex

export SHA1=`echo ${CIRCLE_SHA1} | cut -c1-7`
export ENV=`echo $1 | rev | cut -d \- -f1 | rev`

if [ $1 -eq 'staging']; then
    export S3_BUCKET=$S3_BUCKET_STAGING
    export LAMBDA_EXEC_ROLE=$LAMBDA_EXEC_ROLE_STAGING
    python src/environment.py staging
    pushd src && python install.py && popd
elif [ $1 -eq 'production']; then
    aws sts assume-role --role-arn $STS_ROLE_PRODUCTION --role-session-name circleci > /tmp/sts.json; export AWS_ACCESS_KEY=`cat /tmp/sts.json | jq -r .Credentials.AccessKeyId`; export AWS_SECRET_KEY=`cat /tmp/sts.json | jq -r .Credentials.SecretAccessKey`; export AWS_SESSION_TOKEN=`cat /tmp/sts.json | jq -r .Credentials.SessionToken`; export  AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY; export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_KEY
    rm -f /tmp/sts.json

    export S3_BUCKET=$S3_BUCKET_STAGING
    export LAMBDA_EXEC_ROLE=$LAMBDA_EXEC_ROLE_STAGING
    python src/environment.py production
    pushd src && python install.py && popd
fi
# exit code??
#lamvery deploy -s #$1

if [ $? -eq 0 ]; then
    export SL_COLOR="good"
    export SL_TEXT="Success: Deployed ${CIRCLE_BRANCH} (<${CIRCLE_COMPARE_URL}|${SHA1}>) by ${CIRCLE_USERNAME} !!"
    export SL_ICON="https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/AWS_Simple_Icons_Compute_AWSLambda.svg/150px-AWS_Simple_Icons_Compute_AWSLambda.svg.png"
else
    export SL_COLOR="danger"
    export SL_TEXT="Failure: Deploying ${CIRCLE_BRANCH} (<${CIRCLE_COMPARE_URL}|${SHA1}>) by ${CIRCLE_USERNAME} !!"
    export SL_ICON="https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/AWS_Simple_Icons_Compute_AWSLambda.svg/150px-AWS_Simple_Icons_Compute_AWSLambda.svg.png"
fi

curl -X POST --data-urlencode 'payload={"username": "Elastic Beanstalk", "icon_url": "'"$SL_ICON"'", "channel": "'"${CHANNEL:-#test}"'", "attachments": [{ "color": "'"$SL_COLOR"'", "text": "'"$SL_TEXT"'", "mrkdwn_in": ["text"] }] }' https://hooks.slack.com/services/${SLACK_HOOK}
