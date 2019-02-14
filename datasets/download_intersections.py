# python libraries
import botocore
import os

# project modules
from utils.boto import create_session
import settings.local as local
from utils.track import Track

track=Track()

# create Log File
track.createLogFile("./logs/download_intersections.txt")

def iterate_nexrad_intersections(row,output_dir):
    global total
    try:
        session=create_session(local)
        bucket=session.Bucket("noaa-nexrad-level2")

        os.chdir(os.path.dirname(os.path.realpath(output_dir)).split(output_dir)[0])

        obj=bucket.Object(row['KEY'])

        rep=row['KEY'].rpartition("/")
        path=output_dir+"/"+rep[0]
        if not os.path.exists(path):
            os.makedirs(path)


        os.chdir(path)
        bucket.download_file(obj.key,rep[2])
        total+=(obj.get()['ContentLength']*0.000001)
        track.info(str(obj.key)+", "+str(row.name)+", "+path+", "+str(total))
        print(obj.key,row.name,path,total)

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            track.warn("The object does not exist.")
        else:
            raise
            track.warn("Error.")

def iterate_goes_intersections(row,output_dir):
    global total
    try:
        session=create_session(local)
        bucket=session.Bucket("noaa-goes16")
        obj=bucket.Object(row['KEY'])
        bucket.download_file(obj.key,output_dir+"/"+obj.key.replace('/',"_"))
        total+=(obj.get()['ContentLength']*0.000001)
        track.info(str(obj.key)+", "+str(row.name)+", "+output_dir+", "+str(total))
        print(obj.key,row.name,output_dir,total)

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            track.warn("The object does not exist.")
        else:
            raise
            track.warn("Error.")

total=0
def download_intersections(bucket,input_dir,output_dir):

    file=load_CSV_file(input_dir)
    file=file.sort_values(by='KEY')
    file=file.drop_duplicates(['KEY'])
    track.createLogFile(output_dir+"/log.log")
    if bucket=="noaa-goes16":
        file.apply(lambda x:iterate_goes_intersections(x,output_dir),axis=1)
    elif bucket=="noaa-nexrad-level2":
        file.apply(lambda x:iterate_nexrad_intersections(x,output_dir),axis=1)
    track.info("total volume (mb): "+str(total))

