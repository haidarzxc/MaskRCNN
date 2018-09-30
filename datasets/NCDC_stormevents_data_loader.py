import urllib.request as request
import wget
import os
import gzip
import pandas as pd
import utils.track as tr

Track=tr.Track()

'''
https://www.ncdc.noaa.gov/stormevents/ftp.jsp
ftp://ftp.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/
'''
def get_NCDC_data(output_dir,year=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    url ="ftp://ftp.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
    html = request.urlopen(url).read()

    for i in str(html.decode("utf-8")).splitlines():
        if(i.endswith('gz')):
            file=i.split(' ')
            file_name=file[len(i.split(' '))-1]
            file_year=file_name.split("_")[3].replace("d","")

            if int(file_year)!=year:
                continue

            dir=(output_dir+"/"+file_name)
            Track.info(file_name+"-> year "+file_year)

            wget.download(url=(url+file_name), out=output_dir)
            df = pd.read_csv(dir, compression='gzip', header=0, sep=',', quotechar='"')
            df.to_csv(output_dir+"/"+file_name.replace(".gz",""))
            os.remove(".\\"+dir)
            print("\n")


def load_NCDC_file(fileName):
    csv_path=os.path.abspath(fileName)
    try:
        csv_file=pd.read_csv(csv_path)
        Track.info("csv file read")
    except:
        Track.warn("unable to open")


