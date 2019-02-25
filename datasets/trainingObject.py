
# python libraries
import pandas as pd
from pprint import pprint
import json
import datetime
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from PIL import Image
import pyart
import numpy as np
# import warnings
from pathlib import Path

# project modules
from datasets.NCDC_stormevents_data_loader import load_CSV_file

'''

storm data-> corresponds to detectron bounding box
goes data -> corresponds to images in detectron
nexrad data ->corresponds to masks.

Example detectron COCO dataset
For general data-type and format go-to "http://cocodataset.org/#format-data"
{
  "info":{
        "description": "storm events 2017",
		"url": "",
		"version": "1.0",
		"year": 2017,
		"contributor": "Haidar",
		"date_created": "2017-01-27 09:11:52.357475"
  },
  "licenses":[
    {
		"url": "http:\/\/creativecommons.org\/licenses\/by-nc-sa\/2.0\/",
		"id": 1, #unique
		"name": "Attribution-NonCommercial-ShareAlike License"
	}
  ],
  "images":[
    {
		"license": 4, #FOREGIN_KEY->licenses
		"url": "http:\/\/farm7.staticflickr.com\/6116\/6255196340_da26cf2c9e_z.jpg",
		"file_name": "COCO_val2014_000000397133.jpg", #goes data (images)
		"height": 427, #goes image height
		"width": 640,  #goes image width
		"date_captured": "2013-11-14 17:02:52",
		"id": 397133 #unique
	}
  ],
  "type":"instances",
  "annotations":[
    {
        #nexrad data mask
		"segmentation": [[224.24, 297.18, 228.29, 297.18, 234.91, 298.29, 243, 297.55, 249.25, 296.45, 252.19, 294.98, 256.61, 292.4, 254.4, 264.08, 251.83, 262.61, 241.53, 260.04, 235.27, 259.67, 230.49, 259.67, 233.44, 255.25, 237.48, 250.47, 237.85, 243.85, 237.11, 240.54, 234.17, 242.01, 228.65, 249.37, 224.24, 255.62, 220.93, 262.61, 218.36, 267.39, 217.62, 268.5, 218.72, 295.71, 225.34, 297.55]],
		"area": 1481.38065, storm data area
		"iscrowd": 0,
		"image_id": 397133, #FOREGIN_KEY->images
		"bbox": [217.62, 240.54, 38.99, 57.75], #nexrad image jpg bounding box
		"category_id": 44, #FOREGIN_KEY->categories
		"id": 82445 #unique
	}
  ],
  "categories":[
    {
		"supercategory": "person",
		"id": 1,
		"name": "person"
	}
  ]
}

classification loss
goes 3 channels
'''

class TrainingObject:
    def __init__(self,track,year,output_dir,**kwargs):
        # warnings.simplefilter('error', UserWarning)
        self.track=track
        self.year=year
        self.output_dir='./NCDC_stormevents/'+output_dir
        self.current_image_dir=None
        self.current_segmentation=None

        self.fig = plt.figure()

        # instances header
        self.instances={
            "info":{
                "description": "Storm Events "+self.year,
                "url": "ftp://ftp.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/",
                "version": "1.0",
                "year": int(self.year),
                "contributor": "Haidar",
                "date_created": str(datetime.datetime.now())
            },
            "licenses":[{
                "url": "ftp://ftp.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/",
                "id": 1,
                "name": "ncdc.noaa.gov License"
            }],
            "images":[],
            "type":"instances",
            "annotations":[],
            "categories":[
                {
            		"supercategory": "BigStorms",
            		"id": 1,
            		"name": "BigStorms"
            	},
                {
            		"supercategory": "SmallStorms",
            		"id": 2,
            		"name": "SmallStorms"
            	}
            ]
        }
        self.track.info("initialized instances object")




    def create_training_instance(self,storm_row,goes_object,rows,cols):
        # modify instances
        # append image instance
        image_dict={
    		"license": 1, #FOREGIN_KEY->licenses
    		"url": "https://s3.amazonaws.com/",
    		"file_name": self.current_image_dir.split("/")[3], #goes data (images)
    		"height": float(rows), #goes image height
    		"width": float(cols),  #goes image width
    		"date_captured": str(goes_object['bucket_begin_time']),
    		"id": int(storm_row.name) #unique
    	}
        self.track.info("append image")
        self.instances['images'].append(image_dict)

        # append annotation instance

        # numpy to list of lists
        list=[]
        list.append(self.current_segmentation.tolist())

        bbox=self.generate_bounding_box(float(cols),float(rows))

        annoatation_dict={
            "segmentation": list,
            "area": float(bbox["area"]), #storm data area
            "iscrowd": 0,
            "image_id": int(storm_row.name), #FOREGIN_KEY->images
            "bbox": bbox["coordinates"], # nexrad image jpg bounding bbox[x,y,width,height]
            "category_id": 1, #FOREGIN_KEY->categories
            "id": int(storm_row.name) #unique
        }
        self.track.info("append annotations")
        self.instances['annotations'].append(annoatation_dict)

    def dump_instances(self):
        # dump instances
        self.track.info("Dump instances, Directory: "+self.output_dir)
        with open(self.output_dir, 'w') as out:
            json.dump(self.instances,out)

    def generate_training_images(self,goes_data):

        # self.canvas = FigureCanvas(self.fig)
        # ax0 = self.fig.add_subplot(1, 1, 1)

        plt.imshow(goes_data)

        if Path(self.current_image_dir).is_file():
            print(self.current_image_dir)
            raise Exception('Duplicate image')

        self.fig.savefig(self.current_image_dir, dpi=100)
        self.track.info("image created: "+self.current_image_dir)

    def generate_segmentation_image(self,radar):
        value = 35
        refl_grid = radar.get_field(0, 'reflectivity')
        valueList = []
        valueList = refl_grid[refl_grid >= 35].data
        self.current_segmentation=valueList
        # print(valueList)


    def generate_bounding_box(self,width,height):
        # image width and height
        # im = Image.open(self.current_image_dir)
        # width, height = im.size

        area=width*height
        return {
            "area":area,
            "coordinates":[0, 0, width, height]

        }







