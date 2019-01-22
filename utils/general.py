def verify_lon_lat(BEGIN_LON,END_LON, BEGIN_LAT,END_LAT,track=None):
    values=dict(BEGIN_LON=BEGIN_LON,
                END_LON=END_LON,
                BEGIN_LAT=BEGIN_LAT,
                END_LAT=END_LAT
                )
                
    # All longtudes are negative
    if (BEGIN_LON is not None and BEGIN_LON > 0):
        if track is not None:
            track.warning("Exception: BEGIN_LON greator than zero!")
        values['BEGIN_LON']=values['BEGIN_LON']*-1

    if (END_LON is not None and END_LON > 0):
        if track is not None:
            track.warning("Exception: END_LON greator than zero!")
        values['END_LON']=values['END_LON']*-1



    # BEGIN_LAT must be less than END_LAT
    if values['BEGIN_LAT'] is not None and \
        values['END_LAT'] is not None and \
        values['BEGIN_LAT'] > values['END_LAT']:
        if track is not None:
            track.warning("Exception: BEGIN_LAT > END_LAT")

        temp=values['BEGIN_LAT']
        values['BEGIN_LAT']=values['END_LAT']
        values['END_LAT']=temp


    # BEGIN_LON must be less than END_LON

    if values['BEGIN_LON'] is not None and \
        values['END_LON'] is not None and \
        values['BEGIN_LON'] > values['END_LON']:
        if track is not None:
            track.warning("Exception: BEGIN_LON > END_LON")

        temp=values['BEGIN_LON']
        values['BEGIN_LON']=values['END_LON']
        values['END_LON']=temp


    return values
