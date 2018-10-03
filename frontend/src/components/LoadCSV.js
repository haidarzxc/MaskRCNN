import React, { Component } from 'react';
// import '../css/App.css';
import CSVReader from "react-csv-reader";
import { connect  } from 'react-redux';



class LoadCSV extends Component {

  constructor(props){

    super(props)
    this.handleForce=this.handleForce.bind(this)
  }

  handleForce(csv) {
    this.props.dispatch({ type: 'DATA_LOADED', data:csv });
  };

  render() {
    return (
      <CSVReader
      cssClass="react-csv-input"
      label="Load CSV"
      onFileLoaded={this.handleForce}
    />
    );
  }
}//end of LoadCSV

function mapStateToProps(state) {
  return {
    LoadCSV: state.LoadCSV,
  };
}//end of mapStateToProps

export default connect(mapStateToProps)(LoadCSV)
