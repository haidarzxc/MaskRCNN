import React, { Component } from 'react';
import '../css/App.css';
import { connect  } from 'react-redux';
// import { netcdfGcms } from 'netcdf-gcms';
// import { fs } from 'fs';
import AWS from 'aws-sdk';



class App extends Component {
  // constructor(props){
  //
  //   super(props)
  //
  // }

  render() {

    AWS.config.update({
      accessKeyId: '',
      secretAccessKey: '',
      region: 'us-west-2',
      endpoint:'s3.amazonaws.com',

    })
    const s3 = new AWS.S3()


    var bucketParams = {Bucket: 'noaa-nexrad-level2'
                        }
    s3.listObjects(bucketParams, function(err, data) {
      if (err) console.log(err, err.stack); // an error occurred
      else     console.log(data);           // successful response
    });

    return (

      <h1>xzc</h1>
    );
  }
}//end of App

function mapStateToProps(state) {
  return {
    LoadCSV: state.LoadCSV,
  };
}//end of mapStateToProps

export default connect(mapStateToProps)(App)
