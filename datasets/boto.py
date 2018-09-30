
import boto3
import botocore
import os, sys, inspect

# NOTE: switch python PATH to look at parent_directory
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)


import settings.local as local
from NCDC_stormevents_data_loader import load_NCDC_file, get_NCDC_data



def create_session():
    session = boto3.Session(
        aws_access_key_id=local.AWSAccessKeyId,
        aws_secret_access_key=local.AWSSecretKey,
    )

    return session.resource('s3')

def get_data():
    session=create_session()
    try:
        bucket=session.Bucket("noaa-nexrad-level2")
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



load_NCDC_file("NCDC_stormevents/StormEvents_details-ftp_v1.0_d2017_c20180918.csv")
# get_NCDC_data("NCDC_stormevents",2017)



