#!/usr/bin/env python3
"""
API Endpoint testing script for Checkpoint 3.

Tests all conversation, message, and document endpoints.

Usage:
    python scripts/test_api.py
"""

import asyncio
import httpx
import json
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000/api"


class APITester:
    """Test API endpoints."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.test_conversation_id = None
        self.test_document_id = None

    async def run_all_tests(self):
        """Run all test cases."""
        print("\n" + "=" * 60)
        print("AI CHATBOT API - CHECKPOINT 3 TESTS")
        print("=" * 60 + "\n")

        try:
            # Health checks
            print("📋 HEALTH CHECKS")
            print("-" * 60)
            await self.test_health_check()
            await self.test_health_db()

            # Conversation endpoints
            print("\n📝 CONVERSATION ENDPOINTS")
            print("-" * 60)
            await self.test_create_conversation()
            await self.test_list_conversations()
            await self.test_get_conversation()
            await self.test_update_conversation_title()
            await self.test_get_conversation_stats()

            # Message endpoints
            print("\n💬 MESSAGE ENDPOINTS")
            print("-" * 60)
            await self.test_send_message()
            await self.test_get_history()
            await self.test_get_recent_messages()
            await self.test_search_messages()

            # Document endpoints
            print("\n📄 DOCUMENT ENDPOINTS")
            print("-" * 60)
            await self.test_list_documents()

            # Export
            print("\n📥 EXPORT ENDPOINT")
            print("-" * 60)
            await self.test_export_conversation()

            # Cleanup
            print("\n🧹 CLEANUP")
            print("-" * 60)
            await self.test_delete_conversation()

            print("\n" + "=" * 60)
            print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
            print("=" * 60 + "\n")

        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
        finally:
            await self.client.aclose()

    # ==================== Health Checks ====================

    async def test_health_check(self):
        """Test health check endpoint."""
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            print(f"✓ GET /api/health")
            print(f"  Status: {data.get('status')}")
            print(f"  Service: {data.get('service')}")
        except Exception as e:
            print(f"✗ Health check failed: {e}")
            raise

    async def test_health_db(self):
        """Test database health check."""
        try:
            response = await self.client.get(f"{BASE_URL}/health/db")
            assert response.status_code == 200
            data = response.json()
            print(f"✓ GET /api/health/db")
            print(f"  Status: {data.get('status')}")
            print(f"  Database: {data.get('database')}")
        except Exception as e:
            print(f"✗ Database health check failed: {e}")
            raise

    # ==================== Conversation Endpoints ====================

    async def test_create_conversation(self):
        """Test conversation creation."""
        try:
            response = await self.client.post(
                f"{BASE_URL}/conversations",
                params={"system_prompt": "You are a helpful AI assistant"}
            )
            assert response.status_code == 200
            data = response.json()
            self.test_conversation_id = data.get("conversation_id")
            print(f"✓ POST /api/conversations")
            print(f"  Conversation ID: {self.test_conversation_id}")
            print(f"  Created at: {data.get('created_at')}")
        except Exception as e:
            print(f"✗ Create conversation failed: {e}")
            raise

    async def test_list_conversations(self):
        """Test listing conversations."""
        try:
            response = await self.client.get(
                f"{BASE_URL}/conversations",
                params={"skip": 0, "limit": 10}
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✓ GET /api/conversations")
            print(f"  Total conversations: {data['data']['count']}")
        except Exception as e:
            print(f"✗ List conversations failed: {e}")
            raise

    async def test_get_conversation(self):
        """Test getting a specific conversation."""
        try:
            response = await self.client.get(
                f"{BASE_URL}/conversations/{self.test_conversation_id}"
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✓ GET /api/conversations/{{conversation_id}}")
            print(f"  Conversation ID: {data['conversation_id']}")
            print(f"  Messages: {len(data['messages'])}")
        except Exception as e:
            print(f"✗ Get conversation failed: {e}")
            raise

    async def test_update_conversation_title(self):
        """Test updating conversation title."""
        try:
            response = await self.client.patch(
                f"{BASE_URL}/conversations/{self.test_conversation_id}",
                params={"title": "My Test Conversation"}
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✓ PATCH /api/conversations/{{conversation_id}}")
            print(f"  New title: {data['data']['title']}")
        except Exception as e:
            print(f"✗ Update conversation failed: {e}")
            raise

    async def test_get_conversation_stats(self):
        """Test getting conversation statistics."""
        try:
            response = await self.client.get(
                f"{BASE_URL}/conversations/{self.test_conversation_id}/stats"
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✓ GET /api/conversations/{{conversation_id}}/stats")
            stats = data['data']
            print(f"  Message count: {stats.get('message_count', 0)}")
            print(f"  Total tokens: {stats.get('total_tokens', 0)}")
        except Exception as e:
            print(f"✗ Get stats failed: {e}")
            raise

    # ==================== Message Endpoints ====================

    async def test_send_message(self):
        """Test sending a message."""
        try:
            request_data = {
                "message": "Hello, what is Python?",
                "conversation_id": self.test_conversation_id,
                "model": "gpt-3.5-turbo",
                "temperature": 0.7
            }
            response = await self.client.post(
                f"{BASE_URL}/message/send",
                json=request_data
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✓ POST /api/message/send")
            print(f"  User message: 'Hello, what is Python?'")
            print(f"  Response: '{data['message'][:80]}...'")
        except Exception as e:
            print(f"✗ Send message failed: {e}")
            raise

    async def test_get_history(self):
        """Test getting message history."""
        try:
            response = await self.client.get(
                f"{BASE_URL}/conversations/{self.test_conversation_id}/messages",
                params={"skip": 0, "limit": 50}
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✓ GET /api/conversations/{{conversation_id}}/messages")
            print(f"  Total messages: {data['data']['total_count']}")
            print(f"  Retrieved: {len(data['data']['messages'])}")
        except Exception as e:
            print(f"✗ Get history failed: {e}")
            raise

    async def test_get_recent_messages(self):
        """Test getting recent messages."""
        try:
            response = await self.client.get(
                f"{BASE_URL}/conversations/{self.test_conversation_id}/recent",
                params={"count": 5}
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✓ GET /api/conversations/{{conversation_id}}/recent")
            print(f"  Recent messages: {data['data']['count']}")
        except Exception as e:
            print(f"✗ Get recent messages failed: {e}")
            raise

    async def test_search_messages(self):
        """Test searching messages."""
        try:
            response = await self.client.get(
                f"{BASE_URL}/conversations/{self.test_conversation_id}/search",
                params={"query": "Python", "limit": 10}
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✓ GET /api/conversations/{{conversation_id}}/search")
            print(f"  Query: 'Python'")
            print(f"  Results: {data['data']['count']}")
        except Exception as e:
            print(f"✗ Search messages failed: {e}")
            raise

    # ==================== Document Endpoints ====================

    async def test_list_documents(self):
        """Test listing documents."""
        try:
            response = await self.client.get(
                f"{BASE_URL}/documents",
                params={"skip": 0, "limit": 10}
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✓ GET /api/documents")
            print(f"  Total documents: {data['data']['count']}")
        except Exception as e:
            print(f"✗ List documents failed: {e}")
            raise

    # ==================== Export ====================

    async def test_export_conversation(self):
        """Test exporting conversation."""
        try:
            response = await self.client.get(
                f"{BASE_URL}/conversations/{self.test_conversation_id}/export"
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✓ GET /api/conversations/{{conversation_id}}/export")
            export_data = data['data']
            print(f"  Conversation title: {export_data['conversation'].get('title')}")
            print(f"  Total messages: {len(export_data['messages'])}")
        except Exception as e:
            print(f"✗ Export conversation failed: {e}")
            raise

    # ==================== Cleanup ====================

    async def test_delete_conversation(self):
        """Test deleting conversation."""
        try:
            response = await self.client.delete(
                f"{BASE_URL}/conversations/{self.test_conversation_id}"
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✓ DELETE /api/conversations/{{conversation_id}}")
            print(f"  Deleted conversation: {data['data']['conversation_id']}")
        except Exception as e:
            print(f"✗ Delete conversation failed: {e}")
            raise


async def main():
    """Run tests."""
    tester = APITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
