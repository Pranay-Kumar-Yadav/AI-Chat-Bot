/**
 * MessageInput Component
 * Input area for user messages with send button
 */

import React, { useState, useRef } from 'react';

const MessageInput = ({ onSendMessage, isLoading = false, useRAG = false, onRAGToggle }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  const handleSendMessage = async () => {
    if (message.trim() && !isLoading) {
      await onSendMessage(message, useRAG);
      setMessage('');
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleInputChange = (e) => {
    setMessage(e.target.value);
    
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  };

  return (
    <div className="bg-gray-800 border-t border-gray-700 p-6">
      <div className="max-w-4xl mx-auto">
        {/* RAG Toggle */}
        <div className="mb-4 flex items-center space-x-2">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={useRAG}
              onChange={() => onRAGToggle(!useRAG)}
              disabled={isLoading}
              className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-300">Use RAG (document context)</span>
          </label>
        </div>

        {/* Message Input */}
        <div className="flex items-end space-x-3">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Type a message... (Shift+Enter for new line, Enter to send)"
            disabled={isLoading}
            rows="1"
            className="flex-1 bg-gray-700 text-white placeholder-gray-400 rounded-lg border border-gray-600 px-4 py-3 resize-none focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !message.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium flex items-center space-x-2 transition-colors"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Sending...</span>
              </>
            ) : (
              <>
                <span>Send</span>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm3.293-1.293a1 1 0 011.414 0L10 5.586l3.293-3.293a1 1 0 111.414 1.414L11.414 7l3.293 3.293a1 1 0 01-1.414 1.414L10 8.414l-3.293 3.293a1 1 0 01-1.414-1.414L8.586 7 5.293 3.707a1 1 0 010-1.414z" />
                </svg>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default MessageInput;
