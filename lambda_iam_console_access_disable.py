import json
import os
import boto3
import datetime as dt
from datetime import date
import datetime
import time
from dateutil.tz import tzlocal
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

def lambda_handler(event, context):

    iam = boto3.client('iam')
    ses = boto3.client('ses',region_name='us-east-1')

    # create_iam_login_profile = iam.create_login_profile(UserName='umanath_test',Password='NewPassword',PasswordResetRequired=True)

    max_days_since_pw_used = 45
    warning_days = 28

    user_list = iam.list_users()['Users']

    for user in user_list:
        user_name = user['UserName']
        user_tags = iam.list_user_tags(UserName=user_name)['Tags']
        email = ''
        for tag in user_tags:
            if tag['Key'] == 'email':
                email = tag['Value']
        password_last_used = user.get('PasswordLastUsed')

        if password_last_used is None:
            continue
            # password_last_used = "DEFAULT_VALUE"
            # print(user_name)
            # disable_iam_user = iam.delete_login_profile(UserName=user_name)

        days_since_pw_used = (datetime.now(password_last_used.tzinfo) - password_last_used).days

        if days_since_pw_used > max_days_since_pw_used:
            disable_iam_user = iam.delete_login_profile(UserName=user_name)
            print("The",user_name,"has been disabled")
            message = f"Your password for the AWS account has not been used in {days_since_pw_used} days, and we have sent a reminder to renew the password as well, but it didn't get renewed. So we have disabled the Console Access of your IAM User {user_name}"
            ses.send_email(
                Source='umanath.pathak@tothenew.com',
                Destination={
                    'ToAddresses': [email],
                    'CcAddresses': ['umanath.pathak@yahoo.com']
                },
                Message={
                    'Subject': {
                        'Data': 'Password warning'
                    },
                    'Body': {
                        'Text': {
                            'Data': message
                        }
                    }
                }
            )

        elif days_since_pw_used > warning_days:
            message = f"Your password for the AWS account has not been used in {days_since_pw_used} days. Please log in and change your password."
            # sendEmail = sns.publish(TopicArn='arn:aws:sns:us-east-1:459743668989:umanath_sns_test',Message=message,Subject='Password Warning')
            ses.send_email(
                Source='umanath.pathak@tothenew.com',
                Destination={
                    'ToAddresses': [email]
                },
                Message={
                    'Subject': {
                        'Data': 'Password warning'
                    },
                    'Body': {
                        'Text': {
                            'Data': message
                        }
                    }
                }
            )


    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
