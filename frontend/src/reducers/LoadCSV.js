const initialState = {
  csv_data:null,
  plot_data:null,
};

function LoadCSV(state = initialState, action) {
  switch(action.type) {
    case 'DATA_LOADED':
      return {
        ...state,
        csv_data:action.data,
      }
    case 'DATA_PLOT':
        return {
          ...state,
          plot_data:action.values,
        }



    default:
      return state;
  }
}//end of LoadCSV

export default LoadCSV