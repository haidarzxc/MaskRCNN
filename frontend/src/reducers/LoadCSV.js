const initialState = {

};

function LoadCSV(state = initialState, action) {
  switch(action.type) {
    case 'SHOW_LOGIN_MODAL':
      return {
        ...state,
      }



    default:
      return state;
  }
}//end of LoadCSV

export default LoadCSV