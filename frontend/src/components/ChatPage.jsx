/**
 * ChatPage Component
 * Main chat interface combining sidebar, messages, input, and file upload
 */

import React, { useEffect } from 'react';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import MessageInput from './MessageInput';
import FileUpload from './FileUpload';
import useChatStore from '../store/chatStore';

const ChatPage = () => {
  const {
    currentConversationId,
    messages,
    isLoading,
    useRAG,
    conversationStats,
    conversations,
    lastError,
    loadConversations,
    selectConversation,
    newConversation,
    clearConversation,
    sendMessage,
    deleteConversation,
    setRAG
  } = useChatStore();

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  useEffect(() => {
    if (currentConversationId) {
      selectConversation(currentConversationId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentConversationId]);

  const handleNewConversation = async () => {
    await newConversation('New Conversation')
  };

  const handleSelectConversation = async (conversationId) => {
    await selectConversation(conversationId)
  };

  const handleSendMessage = async (content) => {
    if (!currentConversationId || !content.trim()) return;

    try {
      await sendMessage(content)
    } catch (error) {
      alert('Failed to send message. Please try again.')
    }
  };

  const handleClearConversation = async () => {
    if (!currentConversationId) return
    if (!window.confirm('Clear all messages in this conversation?')) return

    await clearConversation()
  };

  const handleRAGToggle = (newValue) => {
    setRAG(newValue)
  };

  return (
    <div className="h-screen flex bg-gray-900">
      {/* Sidebar */}
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={deleteConversation}
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
