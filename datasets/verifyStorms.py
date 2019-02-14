
# python libraries
import pandas as pd


# project modules
from datasets.NCDC_stormevents_data_loader import load_CSV_file

class VerifyStorms:
    def __init__(self,storms,output_dir=None,track=None,**kwargs):
        self.storms=None
        self.track=track
        self.output=pd.DataFrame()
        self.count_lons_violations=0
        self.count_lats_violations=0
        self.count_non_negative_lons_violations=0
        self.output = self.output.assign(BEGIN_LAT=pd.Series())
        self.output = self.output.assign(BEGIN_LON=pd.Series())
        self.output = self.output.assign(END_LAT=pd.Series())
        self.output = self.output.assign(END_LON=pd.Series())
        self.output = self.output.assign(BEGIN_DATE_TIME=pd.Series())
        self.output = self.output.assign(CZ_TIMEZONE=pd.Series())
        self.output = self.output.assign(END_DATE_TIME=pd.Series())

        # testing
        if track==None and output_dir==None:
            self.storms=storms
            stormevents_df=self.storms[['BEGIN_LAT','BEGIN_LON','END_LAT','END_LON','BEGIN_DATE_TIME','CZ_TIMEZONE','END_DATE_TIME']]
            stormevents_df=stormevents_df[(
                            stormevents_df['BEGIN_LAT'].notnull() &
                            stormevents_df['BEGIN_LON'].notnull() &
                            stormevents_df['END_LAT'].notnull() &
                            stormevents_df['END_LON'].notnull() &
                            stormevents_df['BEGIN_DATE_TIME'].notnull() &
                            stormevents_df['CZ_TIMEZONE'].notnull() &
                            stormevents_df['END_DATE_TIME'].notnull()
                            )]
            self.output=stormevents_df.apply(self.iterate_lons_lats, axis=1)
            return

        self.storms=load_CSV_file("./NCDC_stormevents/"+storms)
        self.output_dir="./NCDC_stormevents/"+output_dir


        # create Log File
        self.track.createLogFile("./logs/verify_lon_lat.txt")

        stormevents_df=self.storms[['BEGIN_LAT','BEGIN_LON','END_LAT','END_LON','BEGIN_DATE_TIME','CZ_TIMEZONE','END_DATE_TIME']]
        stormevents_df=stormevents_df[(
                        stormevents_df['BEGIN_LAT'].notnull() &
                        stormevents_df['BEGIN_LON'].notnull() &
                        stormevents_df['END_LAT'].notnull() &
                        stormevents_df['END_LON'].notnull() &
                        stormevents_df['BEGIN_DATE_TIME'].notnull() &
                        stormevents_df['CZ_TIMEZONE'].notnull() &
                        stormevents_df['END_DATE_TIME'].notnull()
                        )]

        self.track.info("removing Nulls "+str(stormevents_df.shape))

        self.track.info("verify lons lats")
        self.output=stormevents_df.apply(self.iterate_lons_lats, axis=1)

        self.output=self.output.reset_index(drop=True)
        self.track.info("reseting index")

        self.output.to_csv(self.output_dir)
        self.track.info("verification Done")

        # re-test
        self.track.info("running again")
        self.storms=load_CSV_file(self.output_dir)
        self.track.info("re-verify lons lats")
        self.output=self.storms.apply(self.iterate_lons_lats, axis=1)
        self.track.info("testing "+self.output_dir+" Done.")

        self.track.info("count_lons_violations "+str(self.count_lons_violations))
        self.track.info("count_lats_violations "+str(self.count_lats_violations))
        self.track.info("count_non_negative_lons_violations "+str(self.count_non_negative_lons_violations))

    def iterate_lons_lats(self,row):
        rowCopy=row
        # verify lons and lats
        # method signiture BEGIN_LON,END_LON, BEGIN_LAT,END_LAT,track=None
        result=self.verify_lon_lat(
            rowCopy['BEGIN_LON'],
            rowCopy['END_LON'],
            rowCopy['BEGIN_LAT'],
            rowCopy['END_LAT'],
            rowCopy
        )



        # after varification
        rowCopy['BEGIN_LON']=result['BEGIN_LON']
        rowCopy['BEGIN_LAT']=result['BEGIN_LAT']
        rowCopy['END_LON']=result['END_LON']
        rowCopy['END_LAT']=result['END_LAT']
        # from source
        rowCopy['BEGIN_DATE_TIME']=rowCopy['BEGIN_DATE_TIME']
        rowCopy['CZ_TIMEZONE']=rowCopy['CZ_TIMEZONE']
        rowCopy['END_DATE_TIME']=rowCopy['END_DATE_TIME']

        return rowCopy


    def verify_lon_lat(self,BEGIN_LON,END_LON, BEGIN_LAT,END_LAT,row=None):
        values=dict(BEGIN_LON=BEGIN_LON,
                    END_LON=END_LON,
                    BEGIN_LAT=BEGIN_LAT,
                    END_LAT=END_LAT
                    )

        # All longtudes are negative
        if (values['BEGIN_LON'] is not None and values['BEGIN_LON'] > 0):
            if self.track is not None and row is not None:
                self.track.warn("Exception: BEGIN_LON greator than zero! "+str(row.name))
                self.count_non_negative_lons_violations+=1
            values['BEGIN_LON']=values['BEGIN_LON']*-1

        if (values['END_LON'] is not None and values['END_LON'] > 0):
            if self.track is not None and row is not None:
                self.track.warn("Exception: END_LON greator than zero! "+str(row.name))
                self.count_non_negative_lons_violations+=1
            values['END_LON']=values['END_LON']*-1



        # BEGIN_LAT must be less than END_LAT
        if values['BEGIN_LAT'] is not None and \
            values['END_LAT'] is not None and \
            values['BEGIN_LAT'] > values['END_LAT']:
            if self.track is not None and row is not None:
                self.track.warn("Exception: BEGIN_LAT > END_LAT, "+ str(values['BEGIN_LAT'])+" > "+str(values['END_LAT'])+", index"+str(row.name))
                self.count_lats_violations+=1

            temp=values['BEGIN_LAT']
            values['BEGIN_LAT']=values['END_LAT']
            values['END_LAT']=temp


        # BEGIN_LON must be less than END_LON

        if values['BEGIN_LON'] is not None and \
            values['END_LON'] is not None and \
            values['BEGIN_LON'] > values['END_LON']:
            if self.track is not None and row is not None:
                self.track.warn("Exception: BEGIN_LON > END_LON , "+str(values['BEGIN_LON'])+" > "+str(values['END_LON'])+", index"+str(row.name))
                self.count_lons_violations+=1

            temp=values['BEGIN_LON']
            values['BEGIN_LON']=values['END_LON']
            values['END_LON']=temp


        return values
