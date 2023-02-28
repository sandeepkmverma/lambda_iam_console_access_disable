################################# IAM Policies Starts Here #################################
#1. CloudWatchWritingLogs
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Sid": "CloudWatchLogsWriteAccess",
#             "Effect": "Allow",
#             "Action": [
#                 "logs:CreateLogGroup",
#                 "logs:CreateLogStream",
#                 "logs:PutLogEvents"
#             ],
#             "Resource": "arn:aws:logs:*:*:*"
#         }
#     ]
# }

#2. LambdaListingAndDeletingIAMUsers
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Action": [
#                 "iam:ListUsers",
#                 "iam:ListUserTags",
#                 "iam:CreateLoginProfile",
#                 "iam:DeleteLoginProfile",
#                 "iam:GetLoginProfile"
#             ],
#             "Resource": "*"
#         }
#     ]
# }

#3. LambdaSESSendingEmailLambda
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Sid": "SendEmail",
#             "Effect": "Allow",
#             "Action": [
#                 "ses:SendEmail",
#                 "ses:SendRawEmail"
#             ],
#             "Resource": "*"
#         }
#     ]
# }
################################# IAM Policies Ends Here #################################


################################# Lambda Function Starts Here #################################
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

    ################################# Variable Stack Starts Here #################################
    account_name = "AWS Account Name"
    ses_region_name='us-east-1'
    max_days_since_pw_used = 45
    warning_days = 38
    ses_source_email_address = "sandeep.km.59@gmail.com"
    cc_email_list = ['umanath.pathak@yahoo.com', 'urpathak14@gmail.com']
    ################################# Variable Stack Ends Here #################################



    ################################# Code Starts Here #################################
    iam = boto3.client('iam')
    ses = boto3.client('ses',region_name=ses_region_name)

    # create_iam_login_profile = iam.create_login_profile(UserName='umanath_test',Password='NewPassword',PasswordResetRequired=True)

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

        days_since_pw_used = (datetime.now(password_last_used.tzinfo) - password_last_used).days

        if days_since_pw_used > max_days_since_pw_used:

            disabled_email_subject = f"Console Access of your IAM User {user_name} in {account_name} AWS Account has been disabled"

            disabled_email_body = f"Your password for the AWS account {account_name} has not been used in {days_since_pw_used} days, and we have sent a reminder to renew the password as well, but it didn't get renewed. So we have disabled the Console Access of your IAM User {user_name}"

            try:
                user_profile_check = iam.get_login_profile(UserName=user_name)
                disable_iam_user = iam.delete_login_profile(UserName=user_name)
                print(disabled_email_subject)

                ses.send_email(
                    Source=ses_source_email_address,
                    Destination={
                        'ToAddresses': [email],
                        'CcAddresses': cc_email_list
                    },
                    Message={
                        'Subject': {
                            'Data': disabled_email_subject
                        },
                        'Body': {
                            'Text': {
                                'Data': disabled_email_body
                            }
                        }
                    }
                )

            except iam.exceptions.NoSuchEntityException as e:
                iam_profile_error = str(e)
                already_disabled_message = f"Console Access is already disabled of {user_name} in {account_name}"
                print(already_disabled_message)


        elif days_since_pw_used == warning_days:

            warning_email_subject = f"Warning for your IAM User {user_name} for AWS Account {account_name}"

            warning_email_body = f"Your IAM user {user_name} of AWS account {account_name} has not been used in {days_since_pw_used} days. Please log in and change your password."

            try:
                user_profile_check = iam.get_login_profile(UserName=user_name)
                print(warning_email_body)

                ses.send_email(
                    Source=ses_source_email_address,
                    Destination={
                        'ToAddresses': [email],
                        'CcAddresses': cc_email_list
                    },
                    Message={
                        'Subject': {
                            'Data': warning_email_subject
                        },
                        'Body': {
                            'Text': {
                                'Data': warning_email_body
                            }
                        }
                    }
                )

            except iam.exceptions.NoSuchEntityException as e:
                iam_profile_error = str(e)
                already_disabled_message = f"Console Access is already disabled of {user_name} in {account_name}"
                print(already_disabled_message)
    ################################# Code Ends Here #################################

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
################################# Lambda Function Ends Here #################################









