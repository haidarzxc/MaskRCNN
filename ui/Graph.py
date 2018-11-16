import matplotlib.pyplot as plt
import pyart
import settings.local as local
import boto3
import os

def create_session():
    session = boto3.Session(
        aws_access_key_id=local.AWSAccessKeyId,
        aws_secret_access_key=local.AWSSecretKey,
    )
    return session.resource('s3')


def get_aws_object(bucket,key,output_dir):
    session=create_session()
    bucket=session.Bucket(bucket)
    bucket.download_file(key,output_dir)


def graph(path):
# open the file, create the displays and figure
    radar = pyart.io.read_nexrad_archive(path)
    display = pyart.graph.RadarDisplay(radar)
    fig = plt.figure(figsize=(10, 8))
    fig.subplots_adjust(hspace=0.4)
    nplots = 10
    for snum in range(10):
        ax = fig.add_subplot(nplots, 4, snum+1)
        display.plot('reflectivity', 0,
                     vmin=-32, vmax=64, ax=ax)
        display.plot_range_ring(radar.range['data'][-1]/1000., ax=ax)
        display.set_limits(xlim=(-500, 500), ylim=(-500, 500), ax=ax)
    # plot super resolution reflectivity


    # --------------


    plt.show()