import React, { Component } from 'react';
// import '../css/App.css';
import CSVReader from "react-csv-reader";
import { connect  } from 'react-redux';
import Plot from 'react-plotly.js';


class PlotBoxModal extends Component {

  constructor(props){

    super(props)

  }



  render() {

    let data=this.props.LoadCSV.csv_data
    let passedData=[]
    let x=[]
    let y=[]

    for(var idx in data){
      if(idx==0){
        continue
      }

      if(data[idx][1]==undefined |
        data[idx][2]==undefined |
        data[idx][3]==undefined |
        data[idx][4]==undefined |
        data[idx][5]==undefined |
        data[idx][6]==undefined |
        data[idx][7]==undefined |
        data[idx][8]==undefined
      ){
        continue
      }



      if(data[idx][5]==data[idx][7] &&
        data[idx][6]==data[idx][8]){
          x.push(data[idx][5])
          y.push(data[idx][6])
        }

      let stm_obj={
          'type': 'rect',
          'x0': data[idx][1],
          'y0': data[idx][2],
          'x1': data[idx][3],
          'y1': data[idx][4],
          'line': {
              'color': 'rgba(128, 0, 128, 1)',
          },
      }
      let loc_obj={
          'type': 'rect',
          'x0': data[idx][5],
          'y0': data[idx][6],
          'x1': data[idx][7],
          'y1': data[idx][8],
          'line': {
              'color': 'rgba(255, 0, 0, 1)',
          },
      }



      passedData.push(stm_obj)
      passedData.push(loc_obj)



    }
    // console.log(passedData);
    return (
      <div>
      <button type="button" className="btn btn-primary" data-toggle="modal" data-target="#exampleModal">
        Plot All Points
      </button>

      <div className="modal fade" id="exampleModal" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
        <div className="modal-dialog modal-lg" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title" id="exampleModalLabel">Ploting Boxes</h5>
              <button type="button" className="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>

            <div className="modal-body">
            <Plot
                  data={[
                  {
                    x: x,
                    y: y,
                    type: 'scatter',
                    mode: 'markers',
                    marker: {color: 'red'},
                  },
                ]}
               layout={{title: 'Boxes',
               'shapes': passedData
             }}
             />
            </div>

            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" data-dismiss="modal">Close</button>
            </div>
          </div>
        </div>
      </div>
      </div>
    );
  }
}//end of PlotBoxModal

function mapStateToProps(state) {
  return {
    LoadCSV: state.LoadCSV,
  };
}//end of mapStateToProps

export default connect(mapStateToProps)(PlotBoxModal)
