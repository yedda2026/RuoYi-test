# ===========================================================
# RuoYi 平台接口自动化测试框架
# 登录鉴权模块 - 测试用例
# ===========================================================
# 作者：ruoyi-test Team
# 版本：v1.0.0
# ===========================================================
# 模块说明：
#   - 测试登录认证类 API
#   - 包含：正常登录、错误密码、Token 过期/无效、刷新 Token、登出等
# ===========================================================

import pytest
import allure
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)

from utils.request_util import RequestUtil
from utils.yaml_util import read_yaml
from utils.assert_util import AssertUtil


def load_auth_test_data():
    return read_yaml('config/config.yaml')


@allure.feature("登录鉴权")
@allure.story("认证模块")
class TestAuth:
    """登录鉴权接口测试类"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.request_util = RequestUtil()
        self.config = load_auth_test_data()

    # ===========================================================
    # 用例1: 正常登录
    # ===========================================================
    @allure.title("正常登录_成功")
    @allure.description("使用正确账密登录，验证获取 Token")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.auth
    @pytest.mark.smoke
    def test_login_success(self):
        with allure.step("Step 1: 发送登录请求"):
            env = self.config.get('env', 'test')
            env_cfg = self.config.get(env, {})
            response = self.request_util.post(
                endpoint="/auth/login",
                data={
                    "username": env_cfg.get('username', 'admin'),
                    "password": env_cfg.get('password', 'admin123')
                }
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)

        with allure.step("Step 3: 验证返回 Token"):
            resp_json = response.json()
            data = resp_json.get('data', {})
            assert 'token' in str(data) or 'access_token' in str(data), \
                f"登录成功应返回 Token，响应: {resp_json}"

    # ===========================================================
    # 用例2: 登录_密码错误
    # ===========================================================
    @allure.title("登录_密码错误")
    @allure.description("使用错误密码登录，验证返回认证失败")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.auth
    @pytest.mark.regression
    def test_login_wrong_password(self):
        with allure.step("Step 1: 发送错误密码登录请求"):
            response = self.request_util.post(
                endpoint="/auth/login",
                data={
                    "username": "admin",
                    "password": "wrongpassword999"
                }
            )

        with allure.step("Step 2: 断言认证失败"):
            resp_json = response.json()
            code = resp_json.get('code')
            assert code != 200, f"错误密码不应登录成功，响应: {resp_json}"

    # ===========================================================
    # 用例3: 登录_账号不存在
    # ===========================================================
    @allure.title("登录_账号不存在")
    @allure.description("使用不存在的账号登录，验证返回错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.auth
    @pytest.mark.regression
    def test_login_user_not_exist(self):
        with allure.step("Step 1: 发送不存在账号登录请求"):
            response = self.request_util.post(
                endpoint="/auth/login",
                data={
                    "username": "nonexistuser99999",
                    "password": "anypassword"
                }
            )

        with allure.step("Step 2: 断言认证失败"):
            resp_json = response.json()
            code = resp_json.get('code')
            assert code != 200, f"不存在账号不应登录成功，响应: {resp_json}"

    # ===========================================================
    # 用例4: Token无效访问受保护接口
    # ===========================================================
    @allure.title("Token无效_访问受保护接口")
    @allure.description("使用伪造的无效 Token 访问接口，验证返回 401")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.auth
    @pytest.mark.regression
    def test_access_with_invalid_token(self):
        with allure.step("Step 1: 发送携带无效 Token 的请求"):
            response = self.request_util.get(
                endpoint="/system/user/list",
                token="Bearer invalid_token_abc123xyz"
            )

        with allure.step("Step 2: 断言返回未授权"):
            actual_status = response.status_code
            assert actual_status == 401, \
                f"无效 Token 应返回 401，实际: {actual_status}"

    # ===========================================================
    # 用例5: 不带Token访问受保护接口
    # ===========================================================
    @allure.title("不带Token_访问受保护接口")
    @allure.description("不带 Token 访问需要认证的接口，验证返回 401")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.auth
    @pytest.mark.regression
    def test_access_without_token(self):
        with allure.step("Step 1: 发送不带 Token 的请求"):
            response = self.request_util.get(
                endpoint="/system/user/list"
            )

        with allure.step("Step 2: 断言返回未授权"):
            actual_status = response.status_code
            assert actual_status == 401, \
                f"不带 Token 应返回 401，实际: {actual_status}"

    # ===========================================================
    # 用例6: 登录_缺少密码参数
    # ===========================================================
    @allure.title("登录_缺少密码参数")
    @allure.description("登录时缺少密码字段，验证返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.auth
    @pytest.mark.regression
    def test_login_missing_password(self):
        with allure.step("Step 1: 发送缺少密码的登录请求"):
            response = self.request_util.post(
                endpoint="/auth/login",
                data={
                    "username": "admin"
                }
            )

        with allure.step("Step 2: 断言参数错误"):
            resp_json = response.json()
            code = resp_json.get('code')
            assert code != 200, f"缺少密码不应登录成功，响应: {resp_json}"


if __name__ == '__main__':
    print("=== 登录鉴权测试用例自测 ===")
    print("  1. test_login_success              - 正常登录_成功")
    print("  2. test_login_wrong_password      - 登录_密码错误")
    print("  3. test_login_user_not_exist      - 登录_账号不存在")
    print("  4. test_access_with_invalid_token  - Token无效_访问受保护接口")
    print("  5. test_access_without_token      - 不带Token_访问受保护接口")
    print("  6. test_login_missing_password    - 登录_缺少密码参数")
