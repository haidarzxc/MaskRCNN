import React, { Component } from 'react';
// import '../css/App.css';
import CSVReader from "react-csv-reader";
import { connect  } from 'react-redux';
import Plot from 'react-plotly.js';


class PlotBox extends Component {

  constructor(props){

    super(props)
  }

  render() {
    return (
      <Plot
         data={[
           {
             x: this.props.LoadCSV.plot_data,

             type: 'scatter',
             mode: 'points',
             marker: {color: 'red'},
           },

         ]}

       />
    );
  }
}//end of PlotBox

function mapStateToProps(state) {
  return {
    LoadCSV: state.LoadCSV,
  };
}//end of mapStateToProps

export default connect(mapStateToProps)(PlotBox)
