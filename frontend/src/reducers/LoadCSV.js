const initialState = {
  csv_data:null,
};

function LoadCSV(state = initialState, action) {
  switch(action.type) {
    case 'DATA_LOADED':
      return {
        ...state,
        csv_data:action.data,
      }



    default:
      return state;
  }
}//end of LoadCSV

export default LoadCSV