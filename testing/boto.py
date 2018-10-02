

loc=pd.DataFrame()
loc['BEGIN_LON']=pd.Series([0,3,-1])
loc['END_LON']=pd.Series([10,7,-1])
loc['BEGIN_LAT']=pd.Series([10,12,1])
loc['END_LAT']=pd.Series([0,-10,1])
loc['STATIONID']=pd.Series(["xxxx","xxxx","xxxx"])

stm=pd.DataFrame()
stm['BEGIN_LON']=pd.Series([5,8,0])
stm['END_LON']=pd.Series([5,4,0])
stm['BEGIN_LAT']=pd.Series([15,20,2])
stm['END_LAT']=pd.Series([0,7,2])
stm['STATIONID']=pd.Series()
stm['IS_INTERSECTING']=pd.Series()

# print(loc)
# print(loc['BEGIN_LON'] > stm['END_LON'])
# print(stm['BEGIN_LON'] > loc['END_LON'])
# print(loc['BEGIN_LAT'] < stm['END_LAT'])
# print(stm['BEGIN_LAT'] < loc['END_LAT'])
stm=stm.apply(lambda x: filter_stormevents(x,loc),axis=1)
print(stm)