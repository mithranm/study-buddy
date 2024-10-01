import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [file, setFile] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [backendStatus, setBackendStatus] = useState({
    nltk_ready: false,
    chroma_ready: false,
    error: null
  });
  const [isUploading, setIsUploading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

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
      }
    };

    const statusInterval = setInterval(checkBackendStatus, 5000); // Check every 5 seconds

    return () => clearInterval(statusInterval);
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/documents`);
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setUploadProgress(0);

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
      alert(error.response?.data?.error || 'Error uploading file');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
      setFile(null); // Reset file input
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setIsSearching(true);
    try {
      const response = await axios.post(`${BACKEND_URL}/search`, { query: searchQuery });
      setSearchResults(response.data);
    } catch (error) {
      console.error('Error searching:', error);
      alert(error.response?.data?.error || 'Error performing search');
    } finally {
      setIsSearching(false);
    }
  };

  const handleDeleteDocument = async (filename) => {
    try {
      await axios.delete(`${BACKEND_URL}/documents/${filename}`);
      fetchDocuments();
    } catch (error) {
      console.error('Error deleting document:', error);
      alert(error.response?.data?.error || 'Error deleting document');
    }
  };

  const isBackendReady = backendStatus.nltk_ready && backendStatus.chroma_ready;

  return (
    <div>
      <h1>Document Management System</h1>
      
      {!isBackendReady && (
        <div style={{color: 'red'}}>
          Backend is initializing. Please wait...
          {backendStatus.error && <p>Error: {backendStatus.error}</p>}
        </div>
      )}
      
      <form onSubmit={handleFileUpload}>
        <input 
          type="file" 
          onChange={(e) => setFile(e.target.files[0])} 
          disabled={isUploading || !isBackendReady}
        />
        <button type="submit" disabled={!file || isUploading || !isBackendReady}>
          {isUploading ? `Uploading... ${uploadProgress}%` : 'Upload'}
        </button>
      </form>

      <form onSubmit={handleSearch}>
        <input 
          type="text" 
          value={searchQuery} 
          onChange={(e) => setSearchQuery(e.target.value)} 
          placeholder="Enter search query"
          disabled={isSearching || !isBackendReady}
        />
        <button type="submit" disabled={!searchQuery || isSearching || !isBackendReady}>
          {isSearching ? 'Searching...' : 'Search'}
        </button>
      </form>

      <div>
        <h2>Search Results:</h2>
        {isSearching ? (
          <p>Searching... Please wait.</p>
        ) : (
          <pre>{JSON.stringify(searchResults, null, 2)}</pre>
        )}
      </div>

      <div>
        <h2>Uploaded Documents:</h2>
        <ul>
          {documents.map((doc, index) => (
            <li key={index}>
              {doc}
              <button onClick={() => handleDeleteDocument(doc)} disabled={!isBackendReady}>Delete</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;