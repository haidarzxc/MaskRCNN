

import boto3
import botocore

import os, sys, inspect
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)



import settings.local as local

session = boto3.Session(
    aws_access_key_id=local.AWSAccessKeyId,
    aws_secret_access_key=local.AWSSecretKey,
)

s3 = session.resource('s3')


try:
    bucket=s3.Bucket("noaa-nexrad-level2")
    # print(bucket.Object("1991/12/26/KTLX/KTLX19911226_025749.gz"))
    x=0
    for object in bucket.objects.all():
        print(object.key.split("/")[4])
        if x==4:
            break
        x+=1

except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
        print("The object does not exist.")
    else:
        raise