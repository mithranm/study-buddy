import React, { useState, useEffect } from "react";
import axios from "axios";
import { io } from "socket.io-client";

/* COMPONENTS */
import FileUpload from "./components/FileUpload";
import SearchAndChat from "./components/SearchAndChat";
import StatusMessage from "./components/StatusMessage";
import DocumentList from "./components/DocumentList";
import GetModels from "./components/GetModels";

const BACKEND_URL_API = process.env.REACT_APP_BACKEND_URL
  ? process.env.REACT_APP_BACKEND_URL + "/api"
  : "http://localhost:9090/api";
const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || "http://localhost:9090";

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [backendStatus, setBackendStatus] = useState({
    nltk_ready: false,
    chroma_ready: false,
    error: null,
  });
  const [error, setError] = useState(null);
  const [selectedModel, setSelectedModel] = useState("");
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const newSocket = io(SOCKET_URL, {
      transports: ["websocket"],
      cors: {
        origin: "http://localhost:9091/",
      },
      upgrade: false,
    });

    newSocket.on("connect", () => {
      console.log("Socket.IO connection established");
    });

    newSocket.on("connect_error", (error) => {
      console.error("Socket.IO connection error:", error);
      setError("Socket.IO connection error");
    });

    setSocket(newSocket);
    const checkBackendStatus = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL_API}/status`);
        setBackendStatus(response.data);
        if (response.data.nltk_ready && response.data.chroma_ready) {
          fetchDocuments();
        }
      } catch (error) {
        console.error("Error checking backend status:", error);
        setBackendStatus((prev) => ({
          ...prev,
          error: "Unable to connect to the backend",
        }));
      }
    };

    const statusInterval = setInterval(checkBackendStatus, 5000);
    return () => {
      newSocket.disconnect();
      clearInterval(statusInterval)
    };
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL_API}/documents`);
      setDocuments(response.data);
    } catch (error) {
      console.error("Error fetching documents:", error);
      setError("Failed to fetch documents. Please try again.");
    }
  };

  const handleDeleteDocument = async (filename) => {
    try {
      console.log(filename);
      await axios.delete(`${BACKEND_URL_API}/documents/${filename}`);
      fetchDocuments();
    } catch (error) {
      console.error("Error deleting document:", error);
      setError(
        error.response?.data?.error ||
          "Error deleting document. Please try again."
      );
    }
  };

  const handleModelSelect = (model) => {
    setSelectedModel(model);
  };

  const isBackendReady = backendStatus.nltk_ready && backendStatus.chroma_ready;

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <h1 className="text-2xl font-bold mb-5 text-center">
            Document Management System
          </h1>

          <StatusMessage
            isBackendReady={isBackendReady}
            backendStatus={backendStatus}
            error={error}
          />

          <GetModels
            isBackendReady={isBackendReady}
            onModelSelect={handleModelSelect}
          />

          <FileUpload
            isBackendReady={isBackendReady}
            fetchDocuments={fetchDocuments}
            socket={socket}
            setError={setError}
          />

          <SearchAndChat
            isBackendReady={isBackendReady}
            setError={setError}
            selectedModel={selectedModel}
          />

          <DocumentList
            isBackendReady={isBackendReady}
            documents={documents}
            handleDeleteDocument={handleDeleteDocument}
          />
        </div>
      </div>
    </div>
  );
}