import React, { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL_API = process.env.REACT_APP_BACKEND_URL
  ? process.env.REACT_APP_BACKEND_URL + "/api"
  : "http://localhost:9090/api";

const FileUpload = ({ isBackendReady, fetchDocuments, setError }) => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [taskId, setTaskId] = useState(null);  
  const [isAlertShown, setIsAlertShown] = useState(false);  // Add this flag to prevent repeated alerts

  useEffect(() => {
    let pollStatusInterval;

    if (taskId) {
      pollStatusInterval = setInterval(async () => {
        try {
          const response = await axios.get(`${BACKEND_URL_API}/task_status/${taskId}`);
          const { state, status } = response.data;

          setUploadStatus(status);

          if (state === "SUCCESS" || state === "FAILURE") {
            clearInterval(pollStatusInterval);
            setIsUploading(false);

            if (state === "SUCCESS" && !isAlertShown) {
              setIsAlertShown(true);  // Set the flag to true once the alert is shown
              alert("File uploaded and processed successfully");
              fetchDocuments();
            } else if (state === "FAILURE") {
              setError("File processing failed");
            }
          }
        } catch (error) {
          clearInterval(pollStatusInterval);
          console.error("Error fetching task status:", error);
          setError("Error fetching task status");
        }
      }, 1000);
    }

    return () => clearInterval(pollStatusInterval);  
  }, [taskId, fetchDocuments, setError, isAlertShown]);

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setUploadStatus("Starting upload...");
    setError(null);
    setIsAlertShown(false);  // Reset the flag when a new upload begins

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${BACKEND_URL_API}/upload`, formData);
      const { task_id } = response.data;
      setTaskId(task_id);  

    } catch (error) {
      console.error("Error uploading file:", error);
      setError(
        error.response?.data?.error || "Error uploading file. Please try again."
      );
      setIsUploading(false);
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
