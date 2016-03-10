#!/bin/bash
set -x

export SHA1=`echo ${CIRCLE_SHA1} | cut -c1-7`
export ENV=`echo $1 | rev | cut -d \- -f1 | rev`

if [ $1 == 'staging' ]; then
    export S3_BUCKET=$S3_BUCKET_STAGING
    export LAMBDA_EXEC_ROLE=$LAMBDA_EXEC_ROLE_STAGING
    python src/environment.py staging
    pushd src && python install.py && popd
elif [ $1 == 'production' ]; then
    export S3_BUCKET=$S3_BUCKET_PRODUCTION
    export LAMBDA_EXEC_ROLE=$LAMBDA_EXEC_ROLE_PRODUCTION
    python src/environment.py production
    pushd src && . env.sh ; python install.py && popd
fi

if [ $? -eq 0 ]; then
    export SL_COLOR="good"
    export SL_TEXT="Success: Deployed ${CIRCLE_BRANCH} (<${CIRCLE_COMPARE_URL}|${SHA1}>) by ${CIRCLE_USERNAME} !!"
    export SL_ICON="https://s3-us-west-2.amazonaws.com/slack-files2/avatars/2015-05-21/4984475810_da919f053253801b5ed9_34.jpg"
    export EXIT=0
else
    export SL_COLOR="danger"
    export SL_TEXT="Failure: Deploying ${CIRCLE_BRANCH} (<${CIRCLE_COMPARE_URL}|${SHA1}>) by ${CIRCLE_USERNAME} !!"
    export SL_ICON="https://s3-us-west-2.amazonaws.com/slack-files2/avatars/2015-05-21/4984475810_da919f053253801b5ed9_34.jpg"
    export EXIT=1
fi

curl -X POST --data-urlencode 'payload={"username": "One Garden", "icon_url": "'"$SL_ICON"'", "channel": "'"${CHANNEL:-#test}"'", "attachments": [{ "color": "'"$SL_COLOR"'", "text": "'"$SL_TEXT"'", "mrkdwn_in": ["text"] }] }' https://hooks.slack.com/services/${SLACK_HOOK}

exit $EXIT
