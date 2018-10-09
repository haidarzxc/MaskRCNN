import React, { Component } from 'react';
import '../css/App.css';
import LoadCSV from "./LoadCSV.js"
import PlotBox from "./PlotBox.js"
import PlotBoxModal from "./PlotBoxModal.js"
import { connect  } from 'react-redux';

class App extends Component {
  constructor(props){

    super(props)
    this.handleRow=this.handleRow.bind(this)
  }

  handleRow(evt){
    let values=[]
    for(var child in evt.currentTarget.childNodes){
      let value=evt.currentTarget.childNodes[child].innerHTML
      if(value!=undefined){
        values.push(value)
      }//end of if
    }//end of loop
    this.props.dispatch({ type: 'DATA_PLOT', values:values });
  }//end of handleRow

  render() {
    let data=this.props.LoadCSV.csv_data
    let content;
    let header=[];
    let body=[];
    let plot
    let plotModal
    if(data!=null){
      //header
      for(var prop in data[0]){
        if(data[0][prop]!=="" | data[0][prop]!==null){
          header[prop]=<th scope="col" key={prop}>{data[0][prop]}</th>
        }
      }//end of header

      for(var idx in data){
        if(idx==0){
          continue
        }
        let cells=[]
        for(var cell in data[idx]){
          cells[cell]=<th key={cell}>{data[idx][cell]}</th>
        }
        body[idx]=<tr key={idx} onClick={this.handleRow}>{cells}</tr>
      }//end of row

      content=
      <table className="table table-striped table-hover">
      <thead>
        <tr>
          {header}

        </tr>
      </thead>
        <tbody>
          {body}

        </tbody>
      </table>
    }//data not null



    if(this.props.LoadCSV.plot_data!=null){
      plot=<PlotBox/>
    }


    if(data!=null){
      plotModal=<PlotBoxModal/>
    }

    return (

      <div>
        <div className="row mainRow">

          <div className="col-sm-6">

            <div className="row">
              <div className="App">
                <LoadCSV/>
              </div>
            </div>

            <div className="row tableColumn">
              {content}
            </div>

          </div>

          <div className="col-sm-6">
            {plotModal}
            {plot}

          </div>

        </div>
      </div>

    );
  }
}//end of App

function mapStateToProps(state) {
  return {
    LoadCSV: state.LoadCSV,
  };
}//end of mapStateToProps

export default connect(mapStateToProps)(App)
