import urllib.request as request
import wget
import os
import gzip
import pandas as pd

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



# get_data("dir")
