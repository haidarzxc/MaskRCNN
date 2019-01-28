# def verify_lon_lat(BEGIN_LON,END_LON, BEGIN_LAT,END_LAT,track=None):
#     values=dict(BEGIN_LON=BEGIN_LON,
#                 END_LON=END_LON,
#                 BEGIN_LAT=BEGIN_LAT,
#                 END_LAT=END_LAT
#                 )
#
#     # All longtudes are negative
#     if (values['BEGIN_LON'] is not None and values['BEGIN_LON'] > 0):
#         if track is not None:
#             track.warn("Exception: BEGIN_LON greator than zero!")
#         values['BEGIN_LON']=values['BEGIN_LON']*-1
#
#     if (values['END_LON'] is not None and values['END_LON'] > 0):
#         if track is not None:
#             track.warn("Exception: END_LON greator than zero!")
#         values['END_LON']=values['END_LON']*-1
#
#
#
#     # BEGIN_LAT must be less than END_LAT
#     if values['BEGIN_LAT'] is not None and \
#         values['END_LAT'] is not None and \
#         values['BEGIN_LAT'] > values['END_LAT']:
#         if track is not None:
#             track.warn("Exception: BEGIN_LAT > END_LAT, "+ str(values['BEGIN_LAT'])+" > "+str(values['END_LAT']))
#
#         temp=values['BEGIN_LAT']
#         values['BEGIN_LAT']=values['END_LAT']
#         values['END_LAT']=temp
#
#
#     # BEGIN_LON must be less than END_LON
#
#     if values['BEGIN_LON'] is not None and \
#         values['END_LON'] is not None and \
#         values['BEGIN_LON'] > values['END_LON']:
#         if track is not None:
#             track.warn("Exception: BEGIN_LON > END_LON , "+str(values['BEGIN_LON'])+" > "+str(values['END_LON']))
#
#         temp=values['BEGIN_LON']
#         values['BEGIN_LON']=values['END_LON']
#         values['END_LON']=temp
#
#
#     return values
