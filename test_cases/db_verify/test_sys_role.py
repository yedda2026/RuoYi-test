# ===========================================================
# RuoYi 平台接口自动化测试框架
# 系统管理 - 角色模块 测试用例
# ===========================================================
# 作者：ruoyi-test Team
# 版本：v1.0.0
# ===========================================================
# 模块说明：
#   - 测试角色管理 API
#   - 包含：角色列表、角色详情、新增角色、修改角色、删除角色、分配权限等
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


@allure.feature("系统管理")
@allure.story("角色管理")
class TestSysRole:
    """系统角色管理接口测试类"""

    @pytest.fixture(autouse=True)
    def setup(self, login_token):
        self.token = login_token
        self.request_util = RequestUtil()

    # ===========================================================
    # 用例1: 获取角色列表_正常场景
    # ===========================================================
    @allure.title("获取角色列表_正常场景")
    @allure.description("分页查询系统角色列表")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.smoke
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "获取角色列表_正常场景",
            "endpoint": "/system/role/list",
            "method": "get",
            "params": {"pageNum": 1, "pageSize": 10},
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_role_list_success(self, case_data):
        with allure.step("Step 1: 发送获取角色列表请求"):
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
            assert isinstance(rows, list), f"角色列表应为数组，响应: {resp_json}"

    # ===========================================================
    # 用例2: 获取角色详情_正常场景
    # ===========================================================
    @allure.title("获取角色详情_正常场景")
    @allure.description("通过角色ID获取角色详细信息")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.smoke
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "获取角色详情_正常场景",
            "endpoint": "/system/role/{id}",
            "path_id": 1,
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_role_detail_success(self, case_data):
        with allure.step("Step 1: 发送获取角色详情请求"):
            endpoint = case_data["endpoint"].format(id=case_data["path_id"])
            response = self.request_util.get(
                endpoint=endpoint,
                token=self.token
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

    # ===========================================================
    # 用例3: 新增角色_正常场景
    # ===========================================================
    @allure.title("新增角色_正常场景")
    @allure.description("添加一个新角色，验证添加成功")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "新增角色_正常场景",
            "endpoint": "/system/role",
            "method": "post",
            "request_body": {
                "roleName": "测试角色",
                "roleKey": "test_role",
                "roleSort": 1,
                "status": "0",
                "remark": "自动化测试角色"
            },
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_role_add_success(self, case_data):
        with allure.step("Step 1: 发送新增角色请求"):
            response = self.request_util.post(
                endpoint=case_data["endpoint"],
                token=self.token,
                data=case_data["request_body"]
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

    # ===========================================================
    # 用例4: 修改角色_正常场景
    # ===========================================================
    @allure.title("修改角色_正常场景")
    @allure.description("修改指定角色的名称，验证修改成功")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "修改角色_正常场景",
            "endpoint": "/system/role",
            "method": "put",
            "request_body": {
                "roleId": 2,
                "roleName": "测试角色_已修改",
                "roleKey": "test_role",
                "roleSort": 1,
                "status": "0",
                "remark": "自动化测试角色_已修改"
            },
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_role_update_success(self, case_data):
        with allure.step("Step 1: 发送修改角色请求"):
            response = self.request_util.put(
                endpoint=case_data["endpoint"],
                token=self.token,
                data=case_data["request_body"]
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

    # ===========================================================
    # 用例5: 删除角色_正常场景
    # ===========================================================
    @allure.title("删除角色_正常场景")
    @allure.description("删除一个角色，验证删除成功")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "删除角色_正常场景",
            "endpoint": "/system/role/{ids}",
            "path_ids": "100",
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_role_delete_success(self, case_data):
        with allure.step("Step 1: 发送删除角色请求"):
            endpoint = case_data["endpoint"].format(ids=case_data["path_ids"])
            response = self.request_util.delete(
                endpoint=endpoint,
                token=self.token
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

    # ===========================================================
    # 用例6: 角色状态启停_正常场景
    # ===========================================================
    @allure.title("角色状态启停_正常场景")
    @allure.description("禁用/启用角色，验证状态切换成功")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "角色状态启停_正常场景",
            "endpoint": "/system/role/changeStatus",
            "method": "put",
            "request_body": {
                "roleId": 2,
                "status": "1"
            },
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_role_change_status(self, case_data):
        with allure.step("Step 1: 发送切换角色状态请求"):
            response = self.request_util.put(
                endpoint=case_data["endpoint"],
                token=self.token,
                data=case_data["request_body"]
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])


if __name__ == '__main__':
    print("=== 系统角色管理测试用例自测 ===")
    print("  1. test_role_list_success      - 获取角色列表_正常场景")
    print("  2. test_role_detail_success   - 获取角色详情_正常场景")
    print("  3. test_role_add_success       - 新增角色_正常场景")
    print("  4. test_role_update_success   - 修改角色_正常场景")
    print("  5. test_role_delete_success    - 删除角色_正常场景")
    print("  6. test_role_change_status    - 角色状态启停_正常场景")
