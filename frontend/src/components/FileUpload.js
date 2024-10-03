import React, { useState } from "react";
import axios from "axios";

const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL || "http://localhost:9090/api";

const FileUpload = ({ isBackendReady, fetchDocuments, setError }) => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setUploadProgress(0);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${BACKEND_URL}/upload`, formData, {
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percentCompleted);
        },
      });
      alert(response.data.message);
      fetchDocuments();
    } catch (error) {
      console.error("Error uploading file:", error);
      setError(
        error.response?.data?.error || "Error uploading file. Please try again."
      );
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
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
          {isUploading ? `Uploading... ${uploadProgress}%` : "Upload"}
        </button>
      </div>
    </form>
  );
};

export default FileUpload;
