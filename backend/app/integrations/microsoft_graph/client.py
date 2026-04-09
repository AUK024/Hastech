import httpx
from app.core.config import get_settings
from app.integrations.microsoft_graph.auth import GraphAuthService


class GraphClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.auth_service = GraphAuthService()

    def _headers(self) -> dict[str, str]:
        token = self.auth_service.get_access_token()
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    def get_message(self, mailbox_email: str, message_id: str) -> dict:
        if not self.settings.graph_tenant_id:
            return {
                'id': message_id,
                'internet_message_id': f'<{message_id}@local.mock>',
                'conversation_id': f'conv-{message_id}',
                'sender_name': 'Mock Sender',
                'sender_email': 'external@example.com',
                'subject': 'Test request',
                'body_preview': 'Hello, I need product information.',
            }
        url = f"{self.settings.graph_base_url}/users/{mailbox_email}/messages/{message_id}"
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=self._headers())
            response.raise_for_status()
            data = response.json()
        return {
            'id': data.get('id', message_id),
            'internet_message_id': data.get('internetMessageId'),
            'conversation_id': data.get('conversationId', message_id),
            'sender_name': data.get('from', {}).get('emailAddress', {}).get('name'),
            'sender_email': data.get('from', {}).get('emailAddress', {}).get('address', ''),
            'subject': data.get('subject', ''),
            'body_preview': data.get('bodyPreview', ''),
        }

    def send_reply(self, mailbox_email: str, message_id: str, comment: str) -> None:
        if not self.settings.graph_tenant_id:
            return
        url = f"{self.settings.graph_base_url}/users/{mailbox_email}/messages/{message_id}/reply"
        payload = {'comment': comment}
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=self._headers(), json=payload)
            response.raise_for_status()

    def has_sent_reply_in_conversation(self, mailbox_email: str, conversation_id: str) -> bool:
        if not self.settings.graph_tenant_id:
            return False

        escaped_conversation_id = conversation_id.replace("'", "''")
        params = {
            '$top': '1',
            '$select': 'id,conversationId',
            '$filter': f"conversationId eq '{escaped_conversation_id}'",
        }
        url = f'{self.settings.graph_base_url}/users/{mailbox_email}/mailFolders/SentItems/messages'
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=self._headers(), params=params)
            response.raise_for_status()
            data = response.json()

        return len(data.get('value', [])) > 0
