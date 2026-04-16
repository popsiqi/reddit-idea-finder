"""Claude API 客户端"""
from anthropic import Anthropic
from typing import Any


class ClaudeClient:
    """Claude API 客户端封装"""

    def __init__(self, config: dict[str, Any]):
        """初始化 Claude 客户端

        Args:
            config: 包含 Claude API 凭证的配置字典
        """
        self._client = Anthropic(api_key=config["claude"]["api_key"])
        self._model = config["claude"]["model"]

    @property
    def model(self) -> str:
        """获取当前使用的模型名称"""
        return self._model

    def analyze(self, prompt: str, max_tokens: int = 4096) -> str:
        """发送分析请求到 Claude

        Args:
            prompt: 发送给 Claude 的提示内容
            max_tokens: 最大返回 token 数，默认 4096

        Returns:
            Claude 的响应文本
        """
        message = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

    def test_connection(self) -> bool:
        """测试 API 连接是否正常

        Returns:
            True 如果连接正常，False 如果失败
        """
        try:
            # 发送一个简单的测试请求
            self._client.messages.create(
                model=self._model,
                max_tokens=10,
                messages=[
                    {"role": "user", "content": "Hi"}
                ]
            )
            return True
        except Exception:
            return False