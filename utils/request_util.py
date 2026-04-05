# ===========================================================
# RuoYi 平台接口自动化测试框架
# 工具函数模块 - HTTP 请求封装类
# ===========================================================
# 作者：ruoyi-test Team
# 版本：v1.0.0
# ===========================================================
# 模块说明：
#   - 统一管理 HTTP 请求方法（GET/POST/PUT/DELETE）
#   - 自动从配置文件读取 base_url
#   - 自动添加 Authorization 认证头（Bearer Token）
#   - 请求前后打印详细日志
#   - 请求失败自动重试 1 次
# ===========================================================

import time
import requests
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .yaml_util import read_yaml


class RequestUtil:
    """
    HTTP 请求工具类
    封装常用的 HTTP 请求方法，提供统一的调用接口
    """

    # 请求超时时间（秒）
    TIMEOUT = 30

    def __init__(self):
        """
        初始化请求工具类
        从配置文件中加载 base_url 和认证信息
        """
        self.base_url = self._load_base_url()
        self.session = self._create_session()

    def _load_base_url(self) -> str:
        """
        从配置文件加载当前环境的 base_url

        :return: 当前激活环境的 base_url
        :raises KeyError: 配置文件格式错误时抛出异常
        """
        config = read_yaml('config/config.yaml')
        env = config.get('env', 'test')
        env_config = config.get(env, {})

        if not env_config:
            raise KeyError(f"配置文件中未找到环境 '{env}' 的配置")

        return env_config.get('base_url', 'http://localhost:8080')

    def _create_session(self) -> requests.Session:
        """
        创建带重试机制的 requests Session

        :return: 配置好的 Session 对象
        """
        session = requests.Session()

        # 配置重试策略：总共重试 2 次（原始 + 1 次重试）
        retry_strategy = Retry(
            total=2,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """
        构建请求头

        :param token: Bearer Token（可选，不传则不带认证头）
        :return: 请求头字典
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if token:
            headers['Authorization'] = f'Bearer {token}'

        return headers

    def _log_request(self, method: str, url: str, headers: Dict, data: Any = None,
                    params: Dict = None) -> float:
        """
        记录请求开始日志

        :param method: 请求方法
        :param url: 请求 URL
        :param headers: 请求头
        :param data: 请求体数据
        :param params: URL 查询参数
        :return: 请求开始时间戳
        """
        start_time = time.time()
        print(f"\n{'='*60}")
        print(f"[请求信息] {method.upper()} {url}")
        # 脱敏 Authorization 头
        safe_headers = {k: (v[:20] + '...' if k == 'Authorization' and len(v) > 20 else v)
                       for k, v in headers.items()}
        print(f"[请求头] {safe_headers}")
        if params:
            print(f"[查询参数] {params}")
        if data:
            print(f"[请求体] {data}")
        print(f"{'='*60}")
        return start_time

    def _log_response(self, response: requests.Response, elapsed_time: float) -> None:
        """
        记录响应日志

        :param response: 响应对象
        :param elapsed_time: 请求耗时（秒）
        """
        print(f"\n{'='*60}")
        print(f"[响应信息] 状态码: {response.status_code}")
        print(f"[响应时间] {elapsed_time:.3f} 秒")
        print(f"[响应头] Content-Type: {response.headers.get('Content-Type')}")

        try:
            resp_json = response.json()
            resp_str = str(resp_json)
            if len(resp_str) > 500:
                print(f"[响应体] {resp_str[:500]}...")
            else:
                print(f"[响应体] {resp_str}")
        except Exception:
            resp_text = response.text
            if len(resp_text) > 500:
                print(f"[响应体] {resp_text[:500]}...")
            else:
                print(f"[响应体] {resp_text}")

        print(f"{'='*60}\n")

    def _build_url(self, endpoint: str) -> str:
        """
        拼接完整的请求 URL

        :param endpoint: API 端点路径（如 /system/user/list）
        :return: 完整的 URL
        """
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint

        return f"{self.base_url}{endpoint}"

    def _request(self, method: str, endpoint: str,
                token: Optional[str] = None,
                data: Optional[Dict] = None,
                params: Optional[Dict] = None,
                **kwargs) -> requests.Response:
        """
        通用请求方法（内部使用）

        :param method: 请求方法
        :param endpoint: API 端点
        :param token: Bearer Token（可选）
        :param data: 请求体数据
        :param params: URL 查询参数
        :param kwargs: 其他传递给 requests 的参数
        :return: 响应对象
        """
        url = self._build_url(endpoint)
        headers = self._get_headers(token)

        start_time = self._log_request(method, url, headers, data, params)

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=self.TIMEOUT,
                **kwargs
            )
        except requests.exceptions.RequestException as e:
            elapsed_time = time.time() - start_time
            print(f"\n[X 请求异常] {method.upper()} {url}")
            print(f"[异常信息] {type(e).__name__}: {e}")
            print(f"[耗时] {elapsed_time:.3f} 秒")
            raise

        elapsed_time = time.time() - start_time
        self._log_response(response, elapsed_time)

        return response

    # ===========================================================
    # 公开的请求方法
    # ===========================================================

    def get(self, endpoint: str, token: Optional[str] = None,
           params: Optional[Dict] = None, **kwargs) -> requests.Response:
        """
        发送 GET 请求

        :param endpoint: API 端点路径
        :param token: Bearer Token（可选）
        :param params: URL 查询参数（字典）
        :param kwargs: 其他传递给 requests 的参数
        :return: 响应对象

        使用示例：
            response = request_util.get('/system/user/list', token=token, params={'pageNum': 1, 'pageSize': 10})
        """
        return self._request('GET', endpoint, token=token, params=params, **kwargs)

    def post(self, endpoint: str, token: Optional[str] = None,
            data: Optional[Dict] = None, **kwargs) -> requests.Response:
        """
        发送 POST 请求

        :param endpoint: API 端点路径
        :param token: Bearer Token（可选）
        :param data: 请求体数据（字典，会自动序列化为 JSON）
        :param kwargs: 其他传递给 requests 的参数
        :return: 响应对象

        使用示例：
            response = request_util.post('/login', data={'username': 'admin', 'password': 'admin123'})
        """
        return self._request('POST', endpoint, token=token, data=data, **kwargs)

    def put(self, endpoint: str, token: Optional[str] = None,
           data: Optional[Dict] = None, **kwargs) -> requests.Response:
        """
        发送 PUT 请求

        :param endpoint: API 端点路径
        :param token: Bearer Token（可选）
        :param data: 请求体数据（字典）
        :param kwargs: 其他传递给 requests 的参数
        :return: 响应对象
        """
        return self._request('PUT', endpoint, token=token, data=data, **kwargs)

    def delete(self, endpoint: str, token: Optional[str] = None,
              **kwargs) -> requests.Response:
        """
        发送 DELETE 请求

        :param endpoint: API 端点路径
        :param token: Bearer Token（可选）
        :param kwargs: 其他传递给 requests 的参数
        :return: 响应对象
        """
        return self._request('DELETE', endpoint, token=token, **kwargs)


if __name__ == '__main__':
    print("=== RequestUtil 请求工具类自测 ===")

    util = RequestUtil()
    print(f"当前 base_url: {util.base_url}")
    print(f"超时时间: {util.TIMEOUT} 秒")

    test_url = util._build_url('/login')
    print(f"测试 URL 构建: {test_url}")

    headers_without_token = util._get_headers()
    print(f"无 Token 请求头: {headers_without_token}")

    headers_with_token = util._get_headers('test_token')
    print(f"带 Token 请求头: {headers_with_token}")
