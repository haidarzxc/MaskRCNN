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
         layout={{title: 'Boxes',
         'shapes': [
                 {
                     'type': 'rect',
                     'x0': this.props.LoadCSV.plot_data[1],
                     'y0': this.props.LoadCSV.plot_data[2],
                     'x1': this.props.LoadCSV.plot_data[3],
                     'y1': this.props.LoadCSV.plot_data[4],
                     'line': {
                         'color': 'rgba(128, 0, 128, 1)',
                     },
                 },

              ]
       }}
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
