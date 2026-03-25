/**
 * ConversationList Component
 * Displays list of conversations in sidebar
 */

import React from 'react';

const ConversationList = ({ 
  conversations = [], 
  currentConversationId = null,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation
}) => {
  return (
    <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <button
          onClick={onNewConversation}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10.5 1.5H19V10.5a8.5 8.5 0 1 1-17 0V1.5h8.5m0-1H2a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2z" />
          </svg>
          <span>New Chat</span>
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-400">
            <p className="text-sm">No conversations yet</p>
          </div>
        ) : (
          <div className="space-y-2 p-4">
            {conversations.map((conv) => (
              <div
                key={conv.conversation_id}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  currentConversationId === conv.conversation_id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-100 hover:bg-gray-600'
                }`}
                onClick={() => onSelectConversation(conv.conversation_id)}
              >
                <div className="truncate font-medium text-sm">{conv.title}</div>
                <div className="text-xs opacity-70">
                  {conv.message_count || 0} messages
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-gray-700 p-4 space-y-2">
        <button className="w-full text-left text-gray-300 hover:text-white text-sm px-3 py-2 rounded hover:bg-gray-700 transition-colors">
          Settings
        </button>
        <button className="w-full text-left text-gray-300 hover:text-white text-sm px-3 py-2 rounded hover:bg-gray-700 transition-colors">
          Help
        </button>
      </div>
    </div>
  );
};

export default ConversationList;
