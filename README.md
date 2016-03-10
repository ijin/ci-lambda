# ci-lambda
assume roles in CI server and deploys lambda functions

## staging (develop branch)

IAM user

Lambda s3 Policy
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect":"Allow",
      "Action":"s3:*",
      "Resource":"arn:aws:s3:::ci-lambda-*"
    },{
      "Effect":"Allow",
      "Action":"s3:ListAllMyBuckets",
      "Resource":"*"
    }
  ]
}
```

Lambda deploy Policy
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1457367905000",
            "Effect": "Allow",
            "Action": [
                "lambda:CreateAlias",
                "lambda:DeleteAlias",
                "lambda:GetAlias",
                "lambda:GetFunction",
                "lambda:GetFunctionConfiguration",
                "lambda:GetPolicy",
                "lambda:ListAliases",
                "lambda:ListVersionsByFunction",
                "lambda:PublishVersion",
                "lambda:UpdateAlias",
                "lambda:UpdateFunctionCode",
                "lambda:UpdateFunctionConfiguration"
            ],
            "Resource": [
                "arn:aws:lambda:ap-northeast-1:713403314913:function:SupportEnvironment*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:CreateFunction",
                "lambda:ListFunctions"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": [
                "arn:aws:iam::713403314913:role/lambda_exec_role"
            ]
        }
    ]
}
```

Assume Policy
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1457362449000",
            "Effect": "Allow",
            "Action": [
                "sts:AssumeRole"
            ],
            "Resource": [
                "arn:aws:iam::908699337798:role/role-to-be-assumed"
            ]
        }
    ]
}
```

## production account (deploy branch)

IAM role

Lambda s3 Policy
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect":"Allow",
      "Action":"s3:*",
      "Resource":"arn:aws:s3:::ci-lambda-*"
    },{
      "Effect":"Allow",
      "Action":"s3:ListAllMyBuckets",
      "Resource":"*"
    }
  ]
}

```

Lambda deploy policy
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1457367905000",
            "Effect": "Allow",
            "Action": [
                "lambda:CreateAlias",
                "lambda:DeleteAlias",
                "lambda:GetAlias",
                "lambda:GetFunction",
                "lambda:GetFunctionConfiguration",
                "lambda:GetPolicy",
                "lambda:ListAliases",
                "lambda:ListVersionsByFunction",
                "lambda:PublishVersion",
                "lambda:UpdateAlias",
                "lambda:UpdateFunctionCode",
                "lambda:UpdateFunctionConfiguration"
            ],
            "Resource": [
                "arn:aws:lambda:ap-northeast-1:908699337798:function:Support*"
            ]
        },
        {
            "Sid": "Stmt1457367905001",
            "Effect": "Allow",
            "Action": [
                "lambda:ListFunctions",
                "lambda:CreateFunction"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": [
                "arn:aws:iam::908699337798:role/lambda_basic_execution"
            ]
        }
    ]
}
```

Trust Relationship
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::713403314913:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```
```

