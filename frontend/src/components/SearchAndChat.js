import React, { useState } from "react";
import axios from "axios";

const BACKEND_URL_API = (process.env.REACT_APP_BACKEND_URL ? process.env.REACT_APP_BACKEND_URL + "/api" : "http://localhost:9090/api");

const SearchAndChat = ({ isBackendReady, setError, selectedModel }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [chatResponse, setChatResponse] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [isChatting, setIsChatting] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setIsSearching(true);
    setError(null);
    try {
      const response = await axios.post(`${BACKEND_URL_API}/search`, {
        query: searchQuery,
      });
      setSearchResults(response.data);
    } catch (error) {
      console.error("Error searching:", error);
      setError(
        error.response?.data?.error ||
          "Error performing search. Please try again."
      );
    } finally {
      setIsSearching(false);
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!selectedModel) {
      setError("Please select a model before chatting.");
      return;
    }
    setIsChatting(true);
    setError(null);
    setChatResponse("");
    try {
      console.log("Sending chat request to:", `${BACKEND_URL_API}/chat`);
      const response = await axios.post(`${BACKEND_URL_API}/chat`, {
        prompt: searchQuery,
        model: selectedModel
      });
      console.log("Chat response received:", response.data);
      if (typeof response.data === "object" && response.data.response) {
        setChatResponse(response.data.response);
      } else {
        setChatResponse(JSON.stringify(response.data["message"]));
      }
    } catch (error) {
      console.error("Error in chat:", error);
      let errorMessage = "An unexpected error occurred during the chat.";
      if (error.response) {
        errorMessage = `Server error ${error.response.status}: ${
          error.response.data.error || JSON.stringify(error.response.data)
        }`;
      } else if (error.request) {
        errorMessage =
          "No response received from the server. The chat function might not be implemented correctly.";
      } else {
        errorMessage = error.message;
      }
      setError(errorMessage);
    } finally {
      setIsChatting(false);
    }
  };

  return (
    <div>
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
            disabled={
              !searchQuery || isSearching || isChatting || !isBackendReady
            }
            className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50 mr-2"
          >
            {isSearching ? "Searching..." : "Search"}
          </button>
          <button
            onClick={handleChat}
            disabled={
              !searchQuery || isSearching || isChatting || !isBackendReady || !selectedModel
            }
            className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50"
          >
            {isChatting ? "Chatting..." : "Chat"}
          </button>
        </div>
      </form>

      <div className="mb-4">
        <h2 className="text-xl font-semibold mb-2">Search Results:</h2>
        {isSearching ? (
          <p className="text-gray-600">Searching... Please wait.</p>
        ) : (
          <pre className="bg-gray-100 p-4 rounded overflow-x-auto">
            {JSON.stringify(searchResults, null, 2)}
          </pre>
        )}
      </div>
      {chatResponse && (
        <div className="mb-4">
          <h2 className="text-xl font-semibold mb-2">Chat Response:</h2>
          <div className="bg-gray-100 p-4 rounded whitespace-pre-wrap">
            {chatResponse}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchAndChat;