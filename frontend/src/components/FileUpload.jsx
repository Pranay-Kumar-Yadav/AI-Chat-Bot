/**
 * FileUpload Component
 * Handles document upload with drag-and-drop and file listing
 */

import React, { useState, useRef, useEffect } from 'react';
import APIClient from '../services/api';

const FileUpload = ({ conversationId }) => {
  const [documents, setDocuments] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const fileInputRef = useRef(null);

  // Load documents when conversation changes
  useEffect(() => {
    if (conversationId) {
      loadDocuments();
    } else {
      setDocuments([]);
    }
  }, [conversationId]);

  const loadDocuments = async () => {
    try {
      if (!conversationId) return;
      const data = await APIClient.listDocuments(conversationId);
      setDocuments(data);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    handleFiles(files);
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    handleFiles(files);
  };

  const handleFiles = async (files) => {
    if (!conversationId) {
      alert('Please create or select a conversation first');
      return;
    }

    const validFiles = Array.from(files).filter(file => {
      const ext = file.name.split('.').pop().toLowerCase();
      return ['pdf', 'txt', 'md'].includes(ext);
    });

    if (validFiles.length === 0) {
      alert('Please upload PDF, TXT, or MD files');
      return;
    }

    setUploading(true);

    for (const file of validFiles) {
      try {
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: 0
        }));

        const formData = new FormData();
        formData.append('file', file);

        await APIClient.uploadDocument(conversationId, formData);

        setUploadProgress(prev => ({
          ...prev,
          [file.name]: 100
        }));

        // Reload documents after successful upload
        await loadDocuments();

        // Clear progress after a delay
        setTimeout(() => {
          setUploadProgress(prev => {
            const newProgress = { ...prev };
            delete newProgress[file.name];
            return newProgress;
          });
        }, 1000);
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: -1
        }));
      }
    }

    setUploading(false);
  };

  const handleDeleteDocument = async (documentId) => {
    if (!window.confirm('Delete this document?')) return;

    try {
      await APIClient.deleteDocument(conversationId, documentId);
      setDocuments(documents.filter(d => d.document_id !== documentId));
    } catch (error) {
      console.error('Failed to delete document:', error);
    }
  };

  return (
    <div className="border-t border-gray-700 p-4">
      {/* Upload Area */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-4 cursor-pointer transition-colors ${
          isDragging
            ? 'border-blue-500 bg-blue-500 bg-opacity-10'
            : 'border-gray-600 hover:border-gray-500'
        }`}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.txt,.md"
          className="hidden"
          onChange={handleFileSelect}
          disabled={!conversationId || uploading}
        />
        <div className="text-center">
          <svg className="w-6 h-6 mx-auto mb-2 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
            <path d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4V5h12v10zm-1-8a1 1 0 11-2 0 1 1 0 012 0zM8 7h-.5v6h7V7h-2V4h-1v3H8z" />
          </svg>
          <p className="text-sm text-gray-300">
            {uploading ? 'Uploading...' : 'Drop files or click to upload'}
          </p>
          <p className="text-xs text-gray-500 mt-1">PDF, TXT, MD only</p>
        </div>
      </div>

      {/* Upload Progress */}
      {Object.keys(uploadProgress).length > 0 && (
        <div className="mt-3 space-y-2">
          {Object.entries(uploadProgress).map(([fileName, progress]) => (
            <div key={fileName} className="flex items-center space-x-2">
              <div className="flex-1 text-xs text-gray-400 truncate">{fileName}</div>
              <div className="flex-1 h-1 bg-gray-700 rounded overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    progress === -1 ? 'bg-red-500' : 'bg-blue-500'
                  }`}
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Documents List */}
      {documents.length > 0 && (
        <div className="mt-4 space-y-2 max-h-40 overflow-y-auto">
          <p className="text-xs text-gray-400 font-semibold">Documents ({documents.length})</p>
          {documents.map(doc => (
            <div
              key={doc.document_id}
              className="flex items-center justify-between bg-gray-700 p-2 rounded text-sm group"
            >
              <div className="flex items-center space-x-2 flex-1 min-w-0">
                <svg className="w-4 h-4 text-gray-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M4 4a2 2 0 012-2h6a1 1 0 01.894.553l2 4H4V4zm0 5v8a2 2 0 002 2h8a2 2 0 002-2V9H4z" />
                </svg>
                <span className="text-gray-200 truncate">{doc.filename}</span>
              </div>
              <button
                onClick={() => handleDeleteDocument(doc.document_id)}
                className="flex-shrink-0 text-gray-500 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity ml-2"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUpload;
