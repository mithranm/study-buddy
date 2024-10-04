import React from "react";
const DocumentList = ({ isBackendReady, documents, handleDeleteDocument }) => {
  return (
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
  );
};

export default DocumentList;
