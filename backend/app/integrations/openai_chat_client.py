from typing import Any

import httpx


class OpenAIChatClient:
    def __init__(self, api_key: str, base_url: str, timeout_seconds: float) -> None:
        self.api_key = (api_key or '').strip()
        self.base_url = (base_url or '').strip().rstrip('/')
        self.timeout_seconds = timeout_seconds

    def is_configured(self) -> bool:
        if not self.api_key or not self.base_url:
            return False
        placeholders = {'your-openai-api-key', 'sk-your-key'}
        return self.api_key.lower() not in placeholders

    def complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
    ) -> str | None:
        normalized_model = (model or '').strip()
        if not normalized_model or not self.is_configured():
            return None

        url = f'{self.base_url}/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'model': normalized_model,
            'temperature': temperature,
            'messages': messages,
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except Exception:
            return None

        return self._extract_content(data)

    @staticmethod
    def _extract_content(data: Any) -> str | None:
        if not isinstance(data, dict):
            return None
        choices = data.get('choices')
        if not isinstance(choices, list) or not choices:
            return None
        first_choice = choices[0] if isinstance(choices[0], dict) else {}
        message = first_choice.get('message') if isinstance(first_choice, dict) else None
        if not isinstance(message, dict):
            return None
        content = message.get('content')
        return content if isinstance(content, str) and content.strip() else None
