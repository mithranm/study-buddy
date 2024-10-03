import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:9090';

export default function App() {
  const [file, setFile] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [chatResponse, setChatResponse] = useState('');
  const [documents, setDocuments] = useState([]);
  const [backendStatus, setBackendStatus] = useState({
    nltk_ready: false,
    chroma_ready: false,
    error: null
  });
  const [isUploading, setIsUploading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [isChatting, setIsChatting] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/status`);
        setBackendStatus(response.data);
        if (response.data.nltk_ready && response.data.chroma_ready) {
          fetchDocuments();
        }
      } catch (error) {
        console.error('Error checking backend status:', error);
        setBackendStatus(prev => ({ ...prev, error: 'Unable to connect to the backend' }));
      }
    };

    const statusInterval = setInterval(checkBackendStatus, 5000);
    return () => clearInterval(statusInterval);
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/documents`);
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
      setError('Failed to fetch documents. Please try again.');
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setUploadProgress(0);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${BACKEND_URL}/upload`, formData, {
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });
      alert(response.data.message);
      fetchDocuments();
    } catch (error) {
      console.error('Error uploading file:', error);
      setError(error.response?.data?.error || 'Error uploading file. Please try again.');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
      setFile(null);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setIsSearching(true);
    setError(null);
    try {
      const response = await axios.post(`${BACKEND_URL}/search`, { query: searchQuery });
      setSearchResults(response.data);
    } catch (error) {
      console.error('Error searching:', error);
      setError(error.response?.data?.error || 'Error performing search. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    setIsChatting(true);
    setError(null);
    setChatResponse('');
    try {
      console.log('Sending chat request to:', `${BACKEND_URL}/chat`);
      const response = await axios.post(`${BACKEND_URL}/chat`, { prompt: searchQuery });
      console.log('Chat response received:', response.data);
      if (typeof response.data === 'object' && response.data.response) {
        setChatResponse(response.data.response);
      } else {
        setChatResponse(JSON.stringify(response.data['message']));
      }
    } catch (error) {
      console.error('Error in chat:', error);
      let errorMessage = 'An unexpected error occurred during the chat.';
      if (error.response) {
        errorMessage = `Server error ${error.response.status}: ${error.response.data.error || JSON.stringify(error.response.data)}`;
      } else if (error.request) {
        errorMessage = 'No response received from the server. The chat function might not be implemented correctly.';
      } else {
        errorMessage = error.message;
      }
      setError(errorMessage);
    } finally {
      setIsChatting(false);
    }
  };

  const handleDeleteDocument = async (filename) => {
    try {
      await axios.delete(`${BACKEND_URL}/documents/${filename}`);
      fetchDocuments();
    } catch (error) {
      console.error('Error deleting document:', error);
      setError(error.response?.data?.error || 'Error deleting document. Please try again.');
    }
  };

  const isBackendReady = backendStatus.nltk_ready && backendStatus.chroma_ready;

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <h1 className="text-2xl font-bold mb-5 text-center">Document Management System</h1>
          
          {!isBackendReady && (
            <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative mb-4" role="alert">
              <strong className="font-bold">Backend is initializing. Please wait...</strong>
              {backendStatus.error && <p className="text-sm">{backendStatus.error}</p>}
            </div>
          )}
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
              <strong className="font-bold">Error: </strong>
              <span className="block sm:inline">{error}</span>
            </div>
          )}

          <form onSubmit={handleFileUpload} className="mb-4">
            <div className="flex items-center justify-between">
              <input 
                type="file" 
                onChange={(e) => setFile(e.target.files[0])} 
                disabled={isUploading || !isBackendReady}
                className="text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
              <button 
                type="submit" 
                disabled={!file || isUploading || !isBackendReady}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50"
              >
                {isUploading ? `Uploading... ${uploadProgress}%` : 'Upload'}
              </button>
            </div>
          </form>

          <form onSubmit={handleSearch} className="mb-4">
            <div className="flex items-center">
              <input 
                type="text" 
                value={searchQuery} 
                onChange={(e) => setSearchQuery(e.target.value)} 
                placeholder="Enter search query or chat prompt"
                disabled={isSearching || isChatting || !isBackendReady}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline mr-2"
              />
              <button 
                type="submit" 
                disabled={!searchQuery || isSearching || isChatting || !isBackendReady}
                className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50 mr-2"
              >
                {isSearching ? 'Searching...' : 'Search'}
              </button>
              <button 
                onClick={handleChat}
                disabled={!searchQuery || isSearching || isChatting || !isBackendReady}
                className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50"
              >
                {isChatting ? 'Chatting...' : 'Chat'}
              </button>
            </div>
          </form>

          <div className="mb-4">
            <h2 className="text-xl font-semibold mb-2">Search Results:</h2>
            {isSearching ? (
              <p className="text-gray-600">Searching... Please wait.</p>
            ) : (
              <pre className="bg-gray-100 p-4 rounded overflow-x-auto">{JSON.stringify(searchResults, null, 2)}</pre>
            )}
          </div>

          {chatResponse && (
            <div className="mb-4">
              <h2 className="text-xl font-semibold mb-2">Chat Response:</h2>
              <div className="bg-gray-100 p-4 rounded whitespace-pre-wrap">{chatResponse}</div>
            </div>
          )}

          <div>
            <h2 className="text-xl font-semibold mb-2">Uploaded Documents:</h2>
            <ul className="list-disc list-inside">
              {documents.map((doc, index) => (
                <li key={index} className="flex items-center justify-between mb-2">
                  <span>{doc}</span>
                  <button 
                    onClick={() => handleDeleteDocument(doc)} 
                    disabled={!isBackendReady}
                    className="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded text-xs focus:outline-none focus:shadow-outline disabled:opacity-50"
                  >
                    Delete
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}