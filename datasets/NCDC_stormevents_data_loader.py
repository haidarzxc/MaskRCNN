import urllib.request as request
import wget
import os
import gzip
import pandas as pd
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def get_data(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    url ="ftp://ftp.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
    html = request.urlopen(url).read()

    for i in str(html.decode("utf-8")).splitlines():
        if(i.endswith('gz')):
            file=i.split(' ')[len(i.split(' '))-1]
            dir=(output_dir+"/"+file)
            print(file,end="")

            wget.download(url=(url+file), out=output_dir)
            df = pd.read_csv(dir, compression='gzip', header=0, sep=',', quotechar='"')
            df.to_csv(output_dir+"/"+file.replace(".gz","")+".csv")
            os.remove(".\\"+dir)

# def create_database(dbname, user, host, password, files):
#     try:
#         # con = psycopg2.connect(dbname=dbname,user=user, host=host,password=password)
#         # con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
#         # cur = con.cursor()
#         # cur.execute("CREATE TABLE "+"test"+"() ;")
#
#         # cur.copy_from(f, sd, sep=',')
#         # f.close()
#     except:
#         pass


# create_database("test","postgres","127.0.0.1","",
# dict(StormEvents="dir/StormEvents_details-ftp_v1.0_d1950_c20170120.csv"))
# get_data("dir")
