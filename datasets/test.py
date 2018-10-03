import pandas as pd
import numpy as np
import os, sys, inspect
# NOTE: switch python PATH to look at parent_directory
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)

from datasets.boto import filter_stormevents

loc=pd.DataFrame()
loc['BEGIN_LON']=pd.Series([0,3,-1])
loc['END_LON']=pd.Series([10,7,-1])
loc['BEGIN_LAT']=pd.Series([10,12,1])
loc['END_LAT']=pd.Series([0,-10,1])
loc['STATIONID']=pd.Series(["xxxx1","xxxx2","xxxx3"])

stm=pd.DataFrame()
stm['BEGIN_LON']=pd.Series([5,8,0])
stm['END_LON']=pd.Series([5,4,0])
stm['BEGIN_LAT']=pd.Series([15,20,2])
stm['END_LAT']=pd.Series([0,7,2])
stm['STATIONID']=pd.Series()
stm['IS_INTERSECTING']=pd.Series()

stm=stm.apply(lambda x: filter_stormevents(x,loc),axis=1)
print(stm)