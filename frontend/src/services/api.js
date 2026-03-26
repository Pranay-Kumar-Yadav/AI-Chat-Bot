/**
 * API service for backend communication
 * Handles all HTTP requests to the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class APIClient {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error: ${endpoint}`, error);
      throw error;
    }
  }

  // ==================== Health Checks ====================

  async getHealth() {
    return this.request('/health/status');
  }

  // ==================== Conversations ====================

  async createConversation(title = 'New Conversation', systemPrompt = '') {
    return this.request('/chat/conversations', {
      method: 'POST',
      body: JSON.stringify({ title, system_prompt: systemPrompt }),
    });
  }

  async listConversations(limit = 50, offset = 0) {
    const params = new URLSearchParams({ limit, offset });
    return this.request(`/chat/conversations?${params}`);
  }

  async getConversation(conversationId) {
    return this.request(`/chat/conversations/${conversationId}`);
  }

  async updateConversation(conversationId, title) {
    return this.request(`/chat/conversations/${conversationId}`, {
      method: 'PATCH',
      body: JSON.stringify({ title }),
    });
  }

  async deleteConversation(conversationId) {
    return this.request(`/chat/conversations/${conversationId}`, {
      method: 'DELETE',
    });
  }

  async getConversationStats(conversationId) {
    return this.request(`/chat/conversations/${conversationId}/stats`);
  }

  // ==================== Messages ====================

  async sendMessage(message, conversationId = null, useRAG = false, systemPrompt = '', model = '') {
    const body = {
      message,
      conversation_id: conversationId,
      use_rag: useRAG,
    }

    if (systemPrompt) body.system_prompt = systemPrompt
    if (model) body.model = model

    return this.request('/message/send', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async getMessageHistory(conversationId, limit = 50, offset = 0) {
    const params = new URLSearchParams({ conversation_id: conversationId, limit, offset });
    return this.request(`/message/history?${params}`);
  }

  async clearConversation(conversationId) {
    const params = new URLSearchParams({ conversation_id: conversationId });
    return this.request(`/message/clear?${params}`, {
      method: 'POST',
    });
  }

  // ==================== Documents ====================

  async uploadDocument(file, conversationId) {
    const formData = new FormData();
    formData.append('file', file);

    return fetch(`${API_BASE_URL}/documents/upload?conversation_id=${conversationId}`, {
      method: 'POST',
      body: formData,
    })
      .then(res => {
        if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
        return res.json();
      })
      .catch(error => {
        console.error('Document upload error:', error);
        throw error;
      });
  }

  async listDocuments(conversationId, limit = 50) {
    const params = new URLSearchParams({ conversation_id: conversationId, limit });
    return this.request(`/documents?${params}`);
  }

  async getDocument(documentId) {
    return this.request(`/documents/${documentId}`);
  }

  async deleteDocument(documentId, conversationId) {
    const params = new URLSearchParams({ conversation_id: conversationId });
    return this.request(`/documents/${documentId}`, {
      method: 'DELETE',
    });
  }

  async updateDocumentStatus(documentId, status) {
    const params = new URLSearchParams({ status });
    return this.request(`/documents/${documentId}/status`, {
      method: 'PATCH',
    });
  }
}

export default new APIClient();
