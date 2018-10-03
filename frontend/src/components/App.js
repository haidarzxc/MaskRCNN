import React, { Component } from 'react';
import '../css/App.css';
import LoadCSV from "./LoadCSV.js"
import PlotBox from "./PlotBox.js"
import { connect  } from 'react-redux';

class App extends Component {


  handleRow(evt){
    console.log(evt.currentTarget);

  }

  render() {
    let data=this.props.LoadCSV.csv_data
    let content;
    let header=[];
    let body=[];
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

    return (

      <div className="container">
        <div className="row">

          <div className="col-sm-6">

            <div className="row">
              <div className="App">
                <LoadCSV/>
              </div>
            </div>

            <div className="row">
              {content}
            </div>

          </div>

          <div className="col-sm-6">
            
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
