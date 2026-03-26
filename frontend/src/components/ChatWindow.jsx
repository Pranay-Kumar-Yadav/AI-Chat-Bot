/**
 * ChatWindow Component
 * Displays the conversation history and message list
 */

import React, { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';

const ChatWindow = ({ messages = [], isLoading = false, onDeleteMessage, onRetryMessage }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto bg-gray-900 p-6 space-y-4">
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-400">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-2">Welcome to AI Chatbot</h2>
            <p>Start a conversation or upload a document to get started</p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((msg, index) => (
            <div key={msg.message_id || index} className="relative group">
              <ChatMessage
                message={msg}
                isUser={msg.role === 'user'}
              />
              <div className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity flex space-x-1">
                {msg.role === 'user' && onRetryMessage && (
                  <button
                    onClick={() => onRetryMessage(msg.message_id)}
                    className="text-xs text-blue-400 hover:text-white bg-black/50 hover:bg-blue-500 px-2 py-1 rounded"
                  >
                    Retry
                  </button>
                )}
                {onDeleteMessage && (
                  <button
                    onClick={() => onDeleteMessage(msg.message_id)}
                    className="text-xs text-red-400 hover:text-white bg-black/50 hover:bg-red-500 px-2 py-1 rounded"
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-700 text-gray-100 rounded-lg rounded-bl-none px-4 py-3">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
};

export default ChatWindow;
