/**
 * Sidebar Component
 * Main sidebar containing conversation list and navigation
 */

import React, { useState, useEffect } from 'react';
import ConversationList from './ConversationList';
import APIClient from '../services/api';

const Sidebar = ({ 
  currentConversationId = null,
  onSelectConversation,
  onNewConversation,
  isLoading = false
}) => {
  const [conversations, setConversations] = useState([]);
  const [loadingConversations, setLoadingConversations] = useState(true);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setLoadingConversations(true);
      const data = await APIClient.listConversations();
      setConversations(data);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoadingConversations(false);
    }
  };

  const handleNewConversation = async () => {
    try {
      const newConversation = await APIClient.createConversation({
        title: 'New Conversation'
      });
      setConversations([newConversation, ...conversations]);
      onNewConversation(newConversation.conversation_id);
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleSelectConversation = (conversationId) => {
    onSelectConversation(conversationId);
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      await APIClient.deleteConversation(conversationId);
      setConversations(conversations.filter(c => c.conversation_id !== conversationId));
      if (currentConversationId === conversationId) {
        onNewConversation(null);
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      <ConversationList
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
      />
    </div>
  );
};

export default Sidebar;
