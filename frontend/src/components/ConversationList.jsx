/**
 * ConversationList Component
 * Displays list of conversations in sidebar
 */

import React, { useState } from 'react';

const ConversationList = ({ 
  conversations = [], 
  currentConversationId = null,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  onRenameConversation
}) => {
  const [editingId, setEditingId] = useState(null)
  const [draftTitle, setDraftTitle] = useState('')

  const startEdit = (conv) => {
    setEditingId(conv.conversation_id)
    setDraftTitle(conv.title || 'New Conversation')
  }

  const saveEdit = async () => {
    if (!editingId || !draftTitle.trim()) return
    await onRenameConversation(editingId, draftTitle.trim())
    setEditingId(null)
    setDraftTitle('')
  }

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

      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-400">
            <p className="text-sm">No conversations yet</p>
          </div>
        ) : (
          <div className="space-y-2 p-4">
            {conversations.map((conv) => {
              const active = currentConversationId === conv.conversation_id
              return (
                <div
                  key={conv.conversation_id}
                  className={`p-3 rounded-lg transition-colors ${
                    active
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-100 hover:bg-gray-600'
                  }`}
                >
                  <div className="flex justify-between items-center gap-2">
                    {editingId === conv.conversation_id ? (
                      <input
                        type="text"
                        value={draftTitle}
                        onChange={(e) => setDraftTitle(e.target.value)}
                        className="w-full bg-gray-900 border border-gray-600 text-white rounded px-2 py-1"
                        onKeyDown={(e) => e.key === 'Enter' && saveEdit()}
                      />
                    ) : (
                      <button
                        className="text-left w-full truncate font-medium text-sm"
                        onClick={() => onSelectConversation(conv.conversation_id)}
                      >
                        {conv.title || 'Untitled Conversation'}
                      </button>
                    )}

                    <div className="flex items-center gap-1">
                      {editingId === conv.conversation_id ? (
                        <button
                          onClick={saveEdit}
                          className="text-xs bg-green-500 hover:bg-green-600 px-2 py-1 rounded"
                        >
                          Save
                        </button>
                      ) : (
                        <button
                          onClick={() => startEdit(conv)}
                          className="text-xs bg-yellow-500 hover:bg-yellow-600 px-2 py-1 rounded"
                        >
                          Edit
                        </button>
                      )}
                      <button
                        onClick={() => onDeleteConversation(conv.conversation_id)}
                        className="text-xs bg-red-500 hover:bg-red-600 px-2 py-1 rounded"
                        title="Delete conversation"
                      >
                        Del
                      </button>
                    </div>
                  </div>
                  <div className="text-xs opacity-70">
                    {conv.message_count || 0} messages
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      <div className="border-t border-gray-700 p-4 space-y-2">
        <button className="w-full text-left text-gray-300 hover:text-white text-sm px-3 py-2 rounded hover:bg-gray-700 transition-colors">
          Settings
        </button>
        <button className="w-full text-left text-gray-300 hover:text-white text-sm px-3 py-2 rounded hover:bg-gray-700 transition-colors">
          Help
        </button>
      </div>
    </div>
  )
}

export default ConversationList;
