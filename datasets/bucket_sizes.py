

total_volume=0
def iterate_intersections_v1(row):
    global total_volume
    total_volume+=row['SIZE']
    print(row.name,row['SIZE'],total_volume)

def get_file_size(input_dir):
    file=load_CSV_file(input_dir,["KEY", "SIZE", "IS_TIME_INTERSECTING", "BEGIN_TIME_UTC", "END_TIME_UTC", "bucket_begin_time", "bucket_end_time"])
    file=file.drop_duplicates(['KEY'])
    file.apply(lambda x:iterate_intersections_v1(x),axis=1)
    print(total_volume)


def get_goes_size(bucket,
                    output_dir=None,
                    product='ABI-L1b-RadC',
                    year="2017",
                    start_date=None,
                    end_date=None,
                    channel=None):
    counter=0
    total_volume=0
    try:
        if not os.path.exists(output_dir):
            file=open(output_dir, 'w+')
            file.close()
        session=create_session()
        bucket=session.Bucket(bucket)
        objects=[]
        if start_date and end_date:
            start=datetime.datetime.strptime(start_date,'%Y-%m-%d').date()
            end=datetime.datetime.strptime(end_date,'%Y-%m-%d').date()
            start_dayOfYear=datetime.datetime.strftime(start,'%j')
            end_dayOfYear=datetime.datetime.strftime(end,'%j')
            dayOfYear=list(range(int(start_dayOfYear), (int(end_dayOfYear)+1)))

            for day in dayOfYear:
                day_object=datetime.datetime.strptime(str(day),'%j').date()
                day_object_dayOfYear=datetime.datetime.strftime(day_object,'%j')
                objects=bucket.objects.filter(Prefix=product+"/"+year+'/'+day_object_dayOfYear)
                print(year,day_object_dayOfYear)
                for object in objects:
                    split_object_key=object.key.split('/')
                    split_object_filename=split_object_key[4].split('_')
                    if channel:
                        object_channel=split_object_filename[1].split('-')[3]
                        if not object_channel[2:]==channel:
                            continue
                    print(object.key,object.size,counter)
                    total_volume+=object.size
                    with open(output_dir, "a") as myfile:
                        rec=str(object.key)+ \
                            ","+str(object.size*0.000001)+ \
                            "\n"
                        myfile.write(rec)
                    counter+=1
            data=load_CSV_file(output_dir,['KEY','SIZE'])
            data.to_csv(output_dir)
            print(total_volume)


    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            Track.warn("The object does not exist.")
        else:
            raise
            Track.warn("Error.")