# ===========================================================
# RuoYi 平台接口自动化测试框架
# 系统管理 - 用户模块 测试用例
# ===========================================================
# 作者：ruoyi-test Team
# 版本：v1.0.0
# ===========================================================
# 模块说明：
#   - 测试系统用户管理 API
#   - 包含：用户列表、用户详情、新增用户、修改用户、删除用户等
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


def load_sys_user_test_data():
    return read_yaml('data/sys_user_data.yaml')


@allure.feature("系统管理")
@allure.story("用户管理")
class TestSysUser:
    """系统用户管理接口测试类"""

    @pytest.fixture(autouse=True)
    def setup(self, login_token):
        self.token = login_token
        self.request_util = RequestUtil()

    # ===========================================================
    # 用例1: 获取用户列表_正常场景
    # ===========================================================
    @allure.title("获取用户列表_正常场景")
    @allure.description("分页查询系统用户列表，验证返回用户数据")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.smoke
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "获取用户列表_正常场景",
            "endpoint": "/system/user/list",
            "method": "get",
            "params": {"pageNum": 1, "pageSize": 10},
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_user_list_success(self, case_data):
        with allure.step("Step 1: 发送获取用户列表请求"):
            response = self.request_util.get(
                endpoint=case_data["endpoint"],
                token=self.token,
                params=case_data["params"]
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

        with allure.step("Step 3: 验证返回数据"):
            resp_json = response.json()
            data = resp_json.get('data', {})
            rows = data.get('rows', []) if isinstance(data, dict) else []
            assert isinstance(rows, list), f"用户列表应为数组，响应: {resp_json}"

    # ===========================================================
    # 用例2: 获取用户详情_正常场景
    # ===========================================================
    @allure.title("获取用户详情_正常场景")
    @allure.description("通过用户ID获取用户详细信息")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.smoke
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "获取用户详情_正常场景",
            "endpoint": "/system/user/{id}",
            "path_id": 1,
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_user_detail_success(self, case_data):
        with allure.step("Step 1: 发送获取用户详情请求"):
            endpoint = case_data["endpoint"].format(id=case_data["path_id"])
            response = self.request_util.get(
                endpoint=endpoint,
                token=self.token
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

        with allure.step("Step 3: 验证返回数据"):
            resp_json = response.json()
            data = resp_json.get('data', {})
            assert isinstance(data, dict), f"用户详情应为对象，响应: {resp_json}"

    # ===========================================================
    # 用例3: 新增用户_正常场景
    # ===========================================================
    @allure.title("新增用户_正常场景")
    @allure.description("添加一个新用户，验证添加成功")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "新增用户_正常场景",
            "endpoint": "/system/user",
            "method": "post",
            "request_body": {
                "userName": "test_user",
                "nickName": "测试用户",
                "deptId": 100,
                "phonenumber": "13800138001",
                "email": "test@example.com",
                "sex": "1",
                "status": "0",
                "roleIds": [2]
            },
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_user_add_success(self, case_data):
        with allure.step("Step 1: 发送新增用户请求"):
            response = self.request_util.post(
                endpoint=case_data["endpoint"],
                token=self.token,
                data=case_data["request_body"]
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

        with allure.step("Step 3: 验证返回"):
            resp_json = response.json()
            assert resp_json.get('code') == 200, f"新增用户失败，响应: {resp_json}"

    # ===========================================================
    # 用例4: 修改用户_正常场景
    # ===========================================================
    @allure.title("修改用户_正常场景")
    @allure.description("修改指定用户的昵称，验证修改成功")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "修改用户_正常场景",
            "endpoint": "/system/user",
            "method": "put",
            "request_body": {
                "userId": 1,
                "nickName": "管理员_已修改",
                "phonenumber": "13800138000",
                "email": "admin@example.com",
                "sex": "1",
                "status": "0"
            },
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_user_update_success(self, case_data):
        with allure.step("Step 1: 发送修改用户请求"):
            response = self.request_util.put(
                endpoint=case_data["endpoint"],
                token=self.token,
                data=case_data["request_body"]
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

    # ===========================================================
    # 用例5: 删除用户_正常场景
    # ===========================================================
    @allure.title("删除用户_正常场景")
    @allure.description("删除一个用户，验证删除成功")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "删除用户_正常场景",
            "endpoint": "/system/user/{ids}",
            "path_ids": "100",
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_user_delete_success(self, case_data):
        with allure.step("Step 1: 发送删除用户请求"):
            endpoint = case_data["endpoint"].format(ids=case_data["path_ids"])
            response = self.request_util.delete(
                endpoint=endpoint,
                token=self.token
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

    # ===========================================================
    # 用例6: 重置用户密码_正常场景
    # ===========================================================
    @allure.title("重置用户密码_正常场景")
    @allure.description("重置指定用户的密码，验证操作成功")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "重置用户密码_正常场景",
            "endpoint": "/system/user/resetPwd",
            "method": "put",
            "request_body": {
                "userId": 1,
                "password": "123456"
            },
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_user_reset_password(self, case_data):
        with allure.step("Step 1: 发送重置密码请求"):
            response = self.request_util.put(
                endpoint=case_data["endpoint"],
                token=self.token,
                data=case_data["request_body"]
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])


if __name__ == '__main__':
    print("=== 系统用户管理测试用例自测 ===")
    print("  1. test_user_list_success    - 获取用户列表_正常场景")
    print("  2. test_user_detail_success  - 获取用户详情_正常场景")
    print("  3. test_user_add_success     - 新增用户_正常场景")
    print("  4. test_user_update_success  - 修改用户_正常场景")
    print("  5. test_user_delete_success  - 删除用户_正常场景")
    print("  6. test_user_reset_password  - 重置用户密码_正常场景")
