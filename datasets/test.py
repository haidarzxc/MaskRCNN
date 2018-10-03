import pandas as pd
import numpy as np
import os, sys, inspect
# NOTE: switch python PATH to look at parent_directory
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)

from datasets.boto import filter_stormevents
from datasets.intersect import *


# testing intersect module
# Example 1
p1=Point(0,10)
p2=Point(10,0)
p3=Point(5,5)
p4=Point(15,0)
r1=Box(p1,p2)
r2=Box(p3,p4)
res=is_intersecting(r1,r2)
print(res)

# Example 2
p1A=Point(3,7)
p2A=Point(12,-10)
p3A=Point(8,4)
p4A=Point(20,7)
r1A=Box(p1A,p2A)
r2A=Box(p3A,p4A)
resA=is_intersecting(r1A,r2A)
print(resA)

# Example 3
p1B=Point(-1,-1)
p2B=Point(1,1)
p3B=Point(0,0)
p4B=Point(2,2)
r1B=Box(p1B,p2B)
r2B=Box(p3B,p4B)
resB=is_intersecting(r1B,r2B)
print(resB)

# Example 4
p1C=Point(-1,-1)
p2C=Point(1,1)
p3C=Point(2,2)
p4C=Point(3,3)
r1C=Box(p1C,p2C)
r2C=Box(p3C,p4C)
resC=is_intersecting(r1C,r2C)
print(resC)


# testing filter_stormevents
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
print(loc)
print(stm)