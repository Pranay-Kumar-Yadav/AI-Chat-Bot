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

      const responseData = await response.json();

      if (!response.ok) {
        const errorMessage = responseData?.detail || responseData?.error || responseData?.message || `HTTP ${response.status}`;
        throw new Error(errorMessage);
      }

      if (
        responseData &&
        typeof responseData === 'object' &&
        'status' in responseData &&
        'data' in responseData
      ) {
        if (responseData.status !== 'success') {
          throw new Error(responseData.error || responseData.message || 'Unknown API error');
        }
        return responseData.data;
      }

      return responseData;
    } catch (error) {
      console.error(`API Error: ${endpoint}`, error);
      throw error;
    }
  }

  // ==================== Health Checks ====================

  async getHealth() {
    return this.request('/health');
  }

  // ==================== Conversations ====================

  async createConversation(title = 'New Conversation', systemPrompt = '') {
    return this.request('/conversations', {
      method: 'POST',
      body: JSON.stringify({ title, system_prompt: systemPrompt }),
    });
  }

  async listConversations(limit = 50, offset = 0) {
    const params = new URLSearchParams({ limit, offset });
    return this.request(`/conversations?${params}`);
  }

  async getConversation(conversationId) {
    return this.request(`/conversations/${conversationId}`);
  }

  async updateConversation(conversationId, title) {
    return this.request(`/conversations/${conversationId}`, {
      method: 'PATCH',
      body: JSON.stringify({ title }),
    });
  }

  async deleteConversation(conversationId) {
    return this.request(`/conversations/${conversationId}`, {
      method: 'DELETE',
    });
  }

  async getConversationStats(conversationId) {
    return this.request(`/conversations/${conversationId}/stats`);
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
    return this.request(`/documents/${documentId}?${params}`, {
      method: 'DELETE',
    });
  }

  async updateDocumentStatus(documentId, status) {
    const params = new URLSearchParams({ status });
    return this.request(`/documents/${documentId}/status?${params}`, {
      method: 'PATCH',
    });
  }
}

export default new APIClient();
