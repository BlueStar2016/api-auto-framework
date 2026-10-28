import requests
from requests import Session, Response
from core.config_manager import config
from core.logger import logger


class APIClient:
    """封装 requests，自动处理 Token 和 Base URL"""

    def __init__(self):
        self.session = Session()
        self.base_url = config.get('base_url')
        self.token = None  # 初始无 Token
        self.token_type = None

    def set_token(self, token: str, token_type: str = "Bearer"):
        """设置 Token 到请求头"""
        self.token = token
        self.token_type = token_type
        self.session.headers.update({'Authorization': f'{token_type} {token}'})
        logger.info("Token has been set.")

    def clear_token(self):
        """清除 Token 及请求头中的认证信息"""
        self.token = None
        self.token_type = None
        self.session.headers.pop('Authorization', None)
        logger.info("Token has been cleared.")

    def request(self, method: str, endpoint: str, **kwargs) -> Response:
        """统一请求方法"""
        url = f"{self.base_url}{endpoint}"

        # 添加通用请求头
        headers = kwargs.pop('headers', {})
        headers['Content-Type'] = 'application/json'

        logger.info(f"Sending {method.upper()} request to {url}")

        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()  # 非 2xx 抛出异常
            logger.debug(f"Response status: {response.status_code}, body: {response.text[:200]}")
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def get(self, endpoint: str, **kwargs) -> Response:
        return self.request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Response:
        return self.request('POST', endpoint, **kwargs)

    # 可继续添加 put, delete 等方法