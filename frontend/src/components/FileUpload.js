import React, { useState } from "react";
import axios from "axios";

const BACKEND_URL_API = process.env.REACT_APP_BACKEND_URL
  ? process.env.REACT_APP_BACKEND_URL + "/api"
  : "http://localhost:9090/api";

const FileUpload = ({ isBackendReady, fetchDocuments, setError }) => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setUploadStatus("Starting upload...");
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${BACKEND_URL_API}/upload`, formData);
      const { filename } = response.data
      console.log(filename)
      
      const eventSource = new EventSource(
        `${BACKEND_URL_API}/upload/stream-status/${filename}`
      );

      console.log("hello")

      eventSource.onmessage = (event) => {
        setUploadStatus(event.data);
        if (event.data === "completed") {
          eventSource.close();
          setIsUploading(false);
          alert("File uploaded and embedded successfully");
          fetchDocuments();
        }
      };

      eventSource.onerror = (event) => {
        eventSource.close();
        setIsUploading(false);
        setError("Error occurred while tracking upload progress");
      };

    } catch (error) {
      console.error("Error uploading file:", error);
      setError(
        error.response?.data?.error || "Error uploading file. Please try again."
      );
    } finally {
      setFile(null);
    }
  };

  return (
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
          {isUploading ? "Uploading..." : "Upload"}
        </button>
      </div>
      {isUploading && (
        <div className="mt-2 text-sm text-gray-600">Status: {uploadStatus}</div>
      )}
    </form>
  );
};

export default FileUpload;
