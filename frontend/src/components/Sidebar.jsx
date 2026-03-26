/**
 * Sidebar Component
 * Main sidebar containing conversation list and navigation
 */

import React from 'react';
import ConversationList from './ConversationList';

const Sidebar = ({
  conversations = [],
  currentConversationId = null,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  isLoading = false
}) => {
  const handleNewConversation = async () => {
    await onNewConversation()
  }

  const handleSelectConversation = (conversationId) => {
    onSelectConversation(conversationId)
  }

  const handleDeleteConversation = async (conversationId) => {
    if (!window.confirm('Delete this conversation?')) return
    await onDeleteConversation(conversationId)
  }

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
