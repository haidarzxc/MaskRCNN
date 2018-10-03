import React, { Component } from 'react';
// import '../css/App.css';
import CSVReader from "react-csv-reader";

const handleForce = data => {
  console.log(data);
};

class LoadCSV extends Component {
  render() {
    return (
      <CSVReader
      cssClass="react-csv-input"
      label="Load CSV"
      onFileLoaded={handleForce}
    />
    );
  }
}

export default LoadCSV;
