# ===========================================================
# RuoYi 平台接口自动化测试框架
# 系统管理 - 菜单/部门/岗位 模块测试用例
# ===========================================================
# 作者：ruoyi-test Team
# 版本：v1.0.0
# ===========================================================
# 模块说明：
#   - 菜单管理：查询菜单树、菜单详情、新增/修改/删除菜单
#   - 部门管理：部门树查询、部门详情、新增/修改/删除部门
#   - 岗位管理：岗位列表、岗位详情、新增/修改/删除岗位
# ===========================================================

import pytest
import allure
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)

from utils.request_util import RequestUtil
from utils.assert_util import AssertUtil


@allure.feature("系统管理")
@allure.story("菜单管理")
class TestSysMenu:
    """菜单管理接口测试类"""

    @pytest.fixture(autouse=True)
    def setup(self, login_token):
        self.token = login_token
        self.request_util = RequestUtil()

    @allure.title("获取菜单列表_正常场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.smoke
    def test_menu_list_success(self):
        with allure.step("Step 1: 发送获取菜单列表请求"):
            response = self.request_util.get(
                endpoint="/system/menu/list",
                token=self.token
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)

        with allure.step("Step 3: 验证返回数据"):
            resp_json = response.json()
            data = resp_json.get('data', [])
            assert isinstance(data, list), f"菜单列表应为数组，响应: {resp_json}"

    @allure.title("获取菜单树_正常场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.smoke
    def test_menu_tree_success(self):
        with allure.step("Step 1: 发送获取菜单树请求"):
            response = self.request_util.get(
                endpoint="/system/menu/treeselect",
                token=self.token
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)

    @allure.title("新增菜单_正常场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    def test_menu_add_success(self):
        with allure.step("Step 1: 发送新增菜单请求"):
            response = self.request_util.post(
                endpoint="/system/menu",
                token=self.token,
                data={
                    "menuName": "测试菜单",
                    "parentId": 1,
                    "orderNum": 1,
                    "path": "/test",
                    "menuType": "C",
                    "visible": "0",
                    "status": "0",
                    "perms": "test:menu:list"
                }
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)

    @allure.title("删除菜单_正常场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    def test_menu_delete_success(self):
        with allure.step("Step 1: 发送删除菜单请求"):
            response = self.request_util.delete(
                endpoint="/system/menu/200",
                token=self.token
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)


@allure.feature("系统管理")
@allure.story("部门管理")
class TestSysDept:
    """部门管理接口测试类"""

    @pytest.fixture(autouse=True)
    def setup(self, login_token):
        self.token = login_token
        self.request_util = RequestUtil()

    @allure.title("获取部门列表_正常场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.smoke
    def test_dept_list_success(self):
        with allure.step("Step 1: 发送获取部门列表请求"):
            response = self.request_util.get(
                endpoint="/system/dept/list",
                token=self.token
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)

    @allure.title("获取部门树_正常场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.smoke
    def test_dept_tree_success(self):
        with allure.step("Step 1: 发送获取部门树请求"):
            response = self.request_util.get(
                endpoint="/system/dept/treeselect",
                token=self.token
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)

    @allure.title("获取部门详情_正常场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.smoke
    def test_dept_detail_success(self):
        with allure.step("Step 1: 发送获取部门详情请求"):
            response = self.request_util.get(
                endpoint="/system/dept/100",
                token=self.token
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)

    @allure.title("新增部门_正常场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    def test_dept_add_success(self):
        with allure.step("Step 1: 发送新增部门请求"):
            response = self.request_util.post(
                endpoint="/system/dept",
                token=self.token,
                data={
                    "deptName": "测试部门",
                    "parentId": 100,
                    "orderNum": 1,
                    "leaderUserId": 1,
                    "status": "0"
                }
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)

    @allure.title("修改部门_正常场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    def test_dept_update_success(self):
        with allure.step("Step 1: 发送修改部门请求"):
            response = self.request_util.put(
                endpoint="/system/dept",
                token=self.token,
                data={
                    "deptId": 100,
                    "deptName": "测试部门_已修改",
                    "parentId": 100,
                    "orderNum": 1,
                    "status": "0"
                }
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)

    @allure.title("删除部门_正常场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    def test_dept_delete_success(self):
        with allure.step("Step 1: 发送删除部门请求"):
            response = self.request_util.delete(
                endpoint="/system/dept/200",
                token=self.token
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)


@allure.feature("系统管理")
@allure.story("岗位管理")
class TestSysPost:
    """岗位管理接口测试类"""

    @pytest.fixture(autouse=True)
    def setup(self, login_token):
        self.token = login_token
        self.request_util = RequestUtil()

    @allure.title("获取岗位列表_正常场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.smoke
    def test_post_list_success(self):
        with allure.step("Step 1: 发送获取岗位列表请求"):
            response = self.request_util.get(
                endpoint="/system/post/list",
                token=self.token,
                params={"pageNum": 1, "pageSize": 10}
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)

    @allure.title("新增岗位_正常场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    def test_post_add_success(self):
        with allure.step("Step 1: 发送新增岗位请求"):
            response = self.request_util.post(
                endpoint="/system/post",
                token=self.token,
                data={
                    "postCode": "test_post",
                    "postName": "测试岗位",
                    "postSort": 1,
                    "status": "0",
                    "remark": "自动化测试岗位"
                }
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)

    @allure.title("修改岗位_正常场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    def test_post_update_success(self):
        with allure.step("Step 1: 发送修改岗位请求"):
            response = self.request_util.put(
                endpoint="/system/post",
                token=self.token,
                data={
                    "postId": 5,
                    "postCode": "test_post",
                    "postName": "测试岗位_已修改",
                    "postSort": 1,
                    "status": "0",
                    "remark": "自动化测试岗位_已修改"
                }
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)

    @allure.title("删除岗位_正常场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.system
    @pytest.mark.regression
    def test_post_delete_success(self):
        with allure.step("Step 1: 发送删除岗位请求"):
            response = self.request_util.delete(
                endpoint="/system/post/10",
                token=self.token
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(200)
            AssertUtil(response).assert_code(200)
