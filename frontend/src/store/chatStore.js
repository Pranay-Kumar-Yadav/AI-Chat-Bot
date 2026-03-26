import { create } from 'zustand'
import APIClient from '../services/api'

const hydrateState = () => {
  if (typeof window === 'undefined') return {}
  try {
    const saved = localStorage.getItem('chatStore')
    if (!saved) return {}
    return JSON.parse(saved)
  } catch (error) {
    console.warn('Failed to hydrate chat store', error)
    return {}
  }
}

const persistedData = hydrateState()

const persistState = (state) => {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(
      'chatStore',
      JSON.stringify({
        conversations: state.conversations,
        currentConversationId: state.currentConversationId,
        useRAG: state.useRAG
      })
    )
  } catch (error) {
    console.warn('Failed to persist chat store', error)
  }
}

const useChatStore = create((set, get) => ({
  conversations: persistedData.conversations || [],
  currentConversationId: persistedData.currentConversationId || null,
  messages: [],
  conversationStats: null,
  isLoading: false,
  useRAG: persistedData.useRAG ?? true,
  lastError: null,

  loadConversations: async () => {
    set({ isLoading: true, lastError: null })
    try {
      const conversations = await APIClient.listConversations()
      set({ conversations })
      persistState(get())
      return conversations
    } catch (error) {
      console.error('loadConversations error', error)
      set({ lastError: error })
    } finally {
      set({ isLoading: false })
    }
  },

  selectConversation: async (conversationId) => {
    set({ currentConversationId: conversationId, isLoading: true, lastError: null })
    persistState(get())
    try {
      const [messages, conversationStats] = await Promise.all([
        APIClient.getMessageHistory(conversationId),
        APIClient.getConversationStats(conversationId)
      ])
      set({ messages, conversationStats })
    } catch (error) {
      console.error('selectConversation error', error)
      set({ lastError: error })
    } finally {
      set({ isLoading: false })
    }
  },

  newConversation: async (title = 'New Conversation') => {
    set({ isLoading: true, lastError: null })
    try {
      const conv = await APIClient.createConversation({ title })
      set((state) => ({ conversations: [conv, ...state.conversations], currentConversationId: conv.conversation_id }))
      persistState(get())
      await get().selectConversation(conv.conversation_id)
      return conv
    } catch (error) {
      console.error('newConversation error', error)
      set({ lastError: error })
    } finally {
      set({ isLoading: false })
    }
  },

  deleteConversation: async (conversationId) => {
    set({ isLoading: true, lastError: null })
    try {
      await APIClient.deleteConversation(conversationId)
      set((state) => {
        const updatedConversations = state.conversations.filter((c) => c.conversation_id !== conversationId)
        const nuCurrent = state.currentConversationId === conversationId ? (updatedConversations[0]?.conversation_id ?? null) : state.currentConversationId
        return {
          conversations: updatedConversations,
          currentConversationId: nuCurrent
        }
      })
      persistState(get())
      if (get().currentConversationId) {
        await get().selectConversation(get().currentConversationId)
      } else {
        set({ messages: [], conversationStats: null })
      }
    } catch (error) {
      console.error('deleteConversation error', error)
      set({ lastError: error })
    } finally {
      set({ isLoading: false })
    }
  },

  clearConversation: async () => {
    const conversationId = get().currentConversationId
    if (!conversationId) return

    set({ isLoading: true, lastError: null })
    try {
      await APIClient.clearConversation(conversationId)
      set({ messages: [], conversationStats: null })
    } catch (error) {
      console.error('clearConversation error', error)
      set({ lastError: error })
    } finally {
      set({ isLoading: false })
    }
  },

  sendMessage: async (content) => {
    const { currentConversationId, useRAG, messages } = get()
    if (!currentConversationId || !content.trim()) return

    const tempMessage = {
      message_id: `temp-${Date.now()}`,
      conversation_id: currentConversationId,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
      tokens_used: 0,
      model: null
    }

    set({ messages: [...messages, tempMessage], isLoading: true, lastError: null })

    try {
      await APIClient.sendMessage(currentConversationId, { content, use_rag: useRAG })
      const updatedMessages = await APIClient.getMessageHistory(currentConversationId)
      const updatedStats = await APIClient.getConversationStats(currentConversationId)
      set({ messages: updatedMessages, conversationStats: updatedStats })
    } catch (error) {
      console.error('sendMessage error', error)
      set ({
        messages: get().messages.filter((m) => m.message_id !== tempMessage.message_id),
        lastError: error
      })
      throw error
    } finally {
      set({ isLoading: false })
    }
  },

  setRAG: (value) => {
    set({ useRAG: value })
    persistState(get())
  }
}))

export default useChatStore
