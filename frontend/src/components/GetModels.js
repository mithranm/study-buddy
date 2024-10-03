import React, {useState} from 'react';
import axios from 'axios';

const BACKEND_URL_API = (process.env.REACT_APP_BACKEND_URL ? process.env.REACT_APP_BACKEND_URL + "/api" : "http://localhost:9090/api");

const GetModels = ({isBackendReady}) => {
    const [models, setModels] = useState(null);

    // finish api call method and then start working on writing the component.
    const handleGetModels = async (e) => {
        e.preventDefault();
        const response = axios.get(`${BACKEND_URL_API}/get_models`);
        setModels(response.data);
    }

    return ; // it will return a component.
}

export default GetModels;