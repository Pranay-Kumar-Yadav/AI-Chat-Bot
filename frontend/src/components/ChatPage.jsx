/**
 * ChatPage Component
 * Main chat interface combining sidebar, messages, input, and file upload
 */

import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import MessageInput from './MessageInput';
import FileUpload from './FileUpload';
import APIClient from '../services/api';

const ChatPage = () => {
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [useRAG, setUseRAG] = useState(true);
  const [conversationStats, setConversationStats] = useState(null);

  // Load messages when conversation changes
  useEffect(() => {
    if (currentConversationId) {
      loadMessages();
      loadStats();
    } else {
      setMessages([]);
      setConversationStats(null);
    }
  }, [currentConversationId]);

  const loadMessages = async () => {
    try {
      const data = await APIClient.getMessageHistory(currentConversationId);
      setMessages(data);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const loadStats = async () => {
    try {
      const stats = await APIClient.getConversationStats(currentConversationId);
      setConversationStats(stats);
    } catch (error) {
      console.error('Failed to load conversation stats:', error);
    }
  };

  const handleNewConversation = async (conversationId) => {
    if (conversationId) {
      setCurrentConversationId(conversationId);
    }
  };

  const handleSelectConversation = (conversationId) => {
    setCurrentConversationId(conversationId);
  };

  const handleSendMessage = async (content) => {
    if (!currentConversationId || !content.trim()) return;

    // Optimistic update - add user message immediately
    const userMessage = {
      message_id: `temp-${Date.now()}`,
      conversation_id: currentConversationId,
      role: 'user',
      content: content,
      timestamp: new Date().toISOString(),
      tokens_used: 0,
      model: null
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await APIClient.sendMessage(currentConversationId, {
        content: content,
        use_rag: useRAG
      });

      // Remove temp message and add real messages
      setMessages(prev => 
        prev.filter(m => m.message_id !== userMessage.message_id)
      );

      // Reload messages to get complete conversation with assistant response
      await loadMessages();
      await loadStats();
    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove temp message on error
      setMessages(prev =>
        prev.filter(m => m.message_id !== userMessage.message_id)
      );
      // Show error to user - in production, use a toast notification
      alert('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearConversation = async () => {
    if (!currentConversationId) return;
    if (!window.confirm('Clear all messages in this conversation?')) return;

    try {
      await APIClient.clearConversation(currentConversationId);
      setMessages([]);
      await loadStats();
    } catch (error) {
      console.error('Failed to clear conversation:', error);
    }
  };

  const handleRAGToggle = (newValue) => {
    setUseRAG(newValue);
  };

  return (
    <div className="h-screen flex bg-gray-900">
      {/* Sidebar */}
      <Sidebar
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        {currentConversationId && (
          <div className="border-b border-gray-700 bg-gray-800 p-4 flex justify-between items-center">
            <div>
              <h1 className="text-xl font-semibold text-white">Chat</h1>
              {conversationStats && (
                <p className="text-sm text-gray-400">
                  {conversationStats.message_count} messages • {conversationStats.token_count} tokens
                </p>
              )}
            </div>
            <button
              onClick={handleClearConversation}
              className="text-gray-400 hover:text-red-400 transition-colors p-2 rounded hover:bg-gray-700"
              title="Clear conversation"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" />
              </svg>
            </button>
          </div>
        )}

        {/* Chat Messages */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {!currentConversationId ? (
            <div className="flex-1 flex items-center justify-center text-center">
              <div>
                <svg className="w-16 h-16 mx-auto mb-4 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5z" />
                  <path d="M6.5 7a1.5 1.5 0 100-3 1.5 1.5 0 000 3zM2 13l4-4m6 0l4 4" strokeWidth={2} stroke="currentColor" fill="none" />
                </svg>
                <h2 className="text-2xl font-semibold text-gray-400">No Conversation Selected</h2>
                <p className="text-gray-500 mt-2">Create or select a conversation to start chatting</p>
              </div>
            </div>
          ) : (
            <ChatWindow messages={messages} isLoading={isLoading} />
          )}
        </div>

        {/* Input Area */}
        {currentConversationId && (
          <>
            <MessageInput
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              useRAG={useRAG}
              onRAGToggle={handleRAGToggle}
            />
            <FileUpload conversationId={currentConversationId} />
          </>
        )}
      </div>
    </div>
  );
};

export default ChatPage;
