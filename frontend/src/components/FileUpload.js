import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";

const BACKEND_URL_API = process.env.REACT_APP_BACKEND_URL
  ? process.env.REACT_APP_BACKEND_URL + "/api"
  : "http://localhost:9090/api";

const FileUpload = ({ isBackendReady, fetchDocuments, socket, setError }) => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [processingStatus, setProcessingStatus] = useState("");

  const handleSocketMessage = useCallback(
    (message) => {
      switch (message.type) {
        case "upload_status":
          setUploadStatus(message.status);
          if (message.status === "Upload complete") {
            setIsUploading(false);
          }
          break;
        case "processing_status":
          setProcessingStatus(message.status);
          if (message.status === "Processing complete") {
            fetchDocuments();
          }
          break;
        default:
          console.log("Received unknown message type:", message.type);
      }
    },
    [fetchDocuments]
  );

  useEffect(() => {
    if (socket == null) return;

    socket.on("message", () => {
      console.log("Recieving message from backend through WebSocket");
      handleSocketMessage();
    });
  }, [socket, handleSocketMessage]);

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setIsUploading(true);
    setUploadStatus("Starting upload...");
    setProcessingStatus("");
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${BACKEND_URL_API}/upload`, formData);
      const { filename } = response.data;
      console.log("File uploaded:", filename);
      setUploadStatus("Upload complete. Waiting for processing to start...");
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
    <div className="mb-4">
      <form onSubmit={handleFileUpload} className="mb-2">
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
      </form>
      {uploadStatus && (
        <div className="mt-2 text-sm text-gray-600">
          Upload Status: {uploadStatus}
        </div>
      )}
      {processingStatus && (
        <div className="mt-2 text-sm text-gray-600">
          Processing Status: {processingStatus}
        </div>
      )}
    </div>
  );
};

export default FileUpload;
