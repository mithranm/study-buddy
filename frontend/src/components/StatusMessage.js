import React from "react";

const StatusMessage = ({ isBackendReady, backendStatus, error }) => {
  if (!isBackendReady) {
    return (
      <div
        className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative mb-4"
        role="alert"
      >
        <strong className="font-bold">
          Backend is initializing. Please wait...
        </strong>
        {backendStatus.error && (
          <p className="text-sm">{backendStatus.error}</p>
        )}
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4"
        role="alert"
      >
        <strong className="font-bold">Error: </strong>
        <span className="block sm:inline">{error}</span>
      </div>
    );
  }

  return null;
};

export default StatusMessage;
