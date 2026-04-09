from datetime import datetime, timezone
import httpx
from app.core.config import get_settings
from app.integrations.microsoft_graph.auth import GraphAuthService


class GraphClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.auth_service: GraphAuthService | None = None

    def _is_graph_configured(self) -> bool:
        required = [
            self.settings.graph_tenant_id.strip(),
            self.settings.graph_client_id.strip(),
            self.settings.graph_client_secret.strip(),
        ]
        if any(not value for value in required):
            return False

        placeholders = {'your-tenant-id', 'your-client-id', 'your-client-secret'}
        return not any(value.lower() in placeholders for value in required)

    @staticmethod
    def _to_graph_datetime(value: datetime) -> str:
        utc_value = value.astimezone(timezone.utc).replace(microsecond=0)
        return utc_value.isoformat().replace('+00:00', 'Z')

    def _headers(self) -> dict[str, str]:
        if self.auth_service is None:
            self.auth_service = GraphAuthService()
        token = self.auth_service.get_access_token()
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    def get_message(self, mailbox_email: str, message_id: str) -> dict:
        if not self._is_graph_configured():
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
        if not self._is_graph_configured():
            return
        url = f"{self.settings.graph_base_url}/users/{mailbox_email}/messages/{message_id}/reply"
        payload = {'comment': comment}
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=self._headers(), json=payload)
            response.raise_for_status()

    def has_sent_reply_in_conversation(self, mailbox_email: str, conversation_id: str) -> bool:
        if not self._is_graph_configured():
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

    def create_message_subscription(
        self,
        *,
        resource: str,
        notification_url: str,
        expiration_datetime: datetime,
        client_state: str | None = None,
        lifecycle_notification_url: str | None = None,
        change_type: str = 'created',
    ) -> dict:
        if not self._is_graph_configured():
            return {
                'id': f'mock-sub-{resource.replace("/", "-")}',
                'resource': resource,
                'changeType': change_type,
                'notificationUrl': notification_url,
                'expirationDateTime': self._to_graph_datetime(expiration_datetime),
                'clientState': client_state,
            }

        payload = {
            'changeType': change_type,
            'notificationUrl': notification_url,
            'resource': resource,
            'expirationDateTime': self._to_graph_datetime(expiration_datetime),
            'latestSupportedTlsVersion': 'v1_2',
        }
        if client_state:
            payload['clientState'] = client_state
        if lifecycle_notification_url:
            payload['lifecycleNotificationUrl'] = lifecycle_notification_url

        url = f'{self.settings.graph_base_url}/subscriptions'
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=self._headers(), json=payload)
            response.raise_for_status()
            return response.json()

    def renew_subscription(self, subscription_id: str, expiration_datetime: datetime) -> dict:
        if not self._is_graph_configured():
            return {
                'id': subscription_id,
                'expirationDateTime': self._to_graph_datetime(expiration_datetime),
            }

        payload = {'expirationDateTime': self._to_graph_datetime(expiration_datetime)}
        url = f'{self.settings.graph_base_url}/subscriptions/{subscription_id}'
        with httpx.Client(timeout=30.0) as client:
            response = client.patch(url, headers=self._headers(), json=payload)
            response.raise_for_status()
            return response.json()

    def delete_subscription(self, subscription_id: str) -> None:
        if not self._is_graph_configured():
            return

        url = f'{self.settings.graph_base_url}/subscriptions/{subscription_id}'
        with httpx.Client(timeout=30.0) as client:
            response = client.delete(url, headers=self._headers())
            if response.status_code == 404:
                return
            response.raise_for_status()
