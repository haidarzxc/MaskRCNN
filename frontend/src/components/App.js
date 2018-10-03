import React, { Component } from 'react';
import '../css/App.css';
import LoadCSV from "./LoadCSV.js"

class App extends Component {
  render() {
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
            </div>
          </div>

          <div className="col-sm-6">
          </div>
        </div>
      </div>

    );
  }
}

export default App;
