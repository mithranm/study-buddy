import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const BACKEND_URL_API = (process.env.REACT_APP_BACKEND_URL ? process.env.REACT_APP_BACKEND_URL + "/api" : "http://localhost:9090/api");

const GetModels = ({ isBackendReady, onModelSelect }) => {
    const [models, setModels] = useState([]);
    const [selectedModel, setSelectedModel] = useState('');
    const [error, setError] = useState(null);

    const handleGetModels = useCallback(async () => {
        try {
            setError(null);
            const response = await axios.get(`${BACKEND_URL_API}/get_models`);
            setModels(response.data.models);
            if (response.data.models.length > 0 && !selectedModel) {
                setSelectedModel(response.data.models[0]);
                onModelSelect(response.data.models[0]);
            }
        } catch (err) {
            setError('Failed to fetch models. Please try again.');
            console.error('Error fetching models:', err);
        }
    }, [onModelSelect, selectedModel]);

    useEffect(() => {
        if (isBackendReady) {
            handleGetModels();
        }
    }, [isBackendReady, handleGetModels]);

    const handleModelChange = (event) => {
        const value = event.target.value;
        setSelectedModel(value);
        onModelSelect(value);
    };

    return (
        <div className="p-4">
            <h2 className="text-xl font-bold mb-4">Select Model</h2>
            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                    <strong className="font-bold">Error:</strong>
                    <span className="block sm:inline"> {error}</span>
                </div>
            )}
            {models.length > 0 ? (
                <select
                    value={selectedModel}
                    onChange={handleModelChange}
                    className="block w-full bg-white border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                >
                    <option value="">Select a model</option>
                    {models.map((model) => (
                        <option key={model} value={model}>
                            {model}
                        </option>
                    ))}
                </select>
            ) : (
                <p className="text-gray-600 mb-4">No models available. {isBackendReady ? 'Please try refreshing.' : 'Waiting for backend to be ready.'}</p>
            )}
        </div>
    );
};

export default GetModels;