# ===========================================================
# RuoYi 平台接口自动化测试框架
# 工作流操作类 - 驳回/撤回/转交/加签/终止 测试用例
# ===========================================================
# 作者：ruoyi-test Team
# 版本：v1.0.0
# ===========================================================
# 模块说明：
#   - 测试工作流各类操作：驳回、撤回、转交、加签、终止等
#   - 与 test_data_permission.py 中的「发起」「审批」形成互补
# ===========================================================

import pytest
import allure
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)

from utils.request_util import RequestUtil
from utils.assert_util import AssertUtil


@allure.feature("工作流")
@allure.story("流程操作")
class TestWorkflowOps:
    """工作流操作接口测试类"""

    @pytest.fixture(autouse=True)
    def setup(self, login_token):
        self.token = login_token
        self.request_util = RequestUtil()

    # ===========================================================
    # 用例1: 驳回任务_正常场景
    # ===========================================================
    @allure.title("驳回任务_正常场景")
    @allure.description("审批人对任务执行驳回操作，验证驳回成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.workflow
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "驳回任务_正常场景",
            "endpoint": "/workflow/task/reject",
            "method": "post",
            "request_body": {
                "taskId": 1,
                "vars": {
                    "message": "材料不全，驳回补充"
                }
            },
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_workflow_reject_success(self, case_data):
        with allure.step("Step 1: 发送驳回任务请求"):
            response = self.request_util.post(
                endpoint=case_data["endpoint"],
                token=self.token,
                data=case_data["request_body"]
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

    # ===========================================================
    # 用例2: 撤回流程_正常场景
    # ===========================================================
    @allure.title("撤回流程_正常场景")
    @allure.description("流程发起人撤回自己发起的流程，验证撤回成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.workflow
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "撤回流程_正常场景",
            "endpoint": "/workflow/process/cancel",
            "method": "put",
            "request_body": {
                "procInstId": 1,
                "reason": "申请有误，主动撤回"
            },
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_workflow_cancel_success(self, case_data):
        with allure.step("Step 1: 发送撤回流程请求"):
            response = self.request_util.put(
                endpoint=case_data["endpoint"],
                token=self.token,
                data=case_data["request_body"]
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

    # ===========================================================
    # 用例3: 转交任务_正常场景
    # ===========================================================
    @allure.title("转交任务_正常场景")
    @allure.description("将待办任务转交给其他用户处理")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.workflow
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "转交任务_正常场景",
            "endpoint": "/workflow/task/delegate",
            "method": "post",
            "request_body": {
                "taskId": 1,
                "delegateUserId": 2,
                "reason": "临时外出，转交处理"
            },
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_workflow_delegate_success(self, case_data):
        with allure.step("Step 1: 发送转交任务请求"):
            response = self.request_util.post(
                endpoint=case_data["endpoint"],
                token=self.token,
                data=case_data["request_body"]
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

    # ===========================================================
    # 用例4: 加签（向前加签）_正常场景
    # ===========================================================
    @allure.title("向前加签_正常场景")
    @allure.description("在当前审批节点前增加一个审批人")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.workflow
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "向前加签_正常场景",
            "endpoint": "/workflow/task/addSign",
            "method": "post",
            "request_body": {
                "taskId": 1,
                "userId": 3,
                "position": "before"
            },
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_workflow_add_sign_before_success(self, case_data):
        with allure.step("Step 1: 发送向前加签请求"):
            response = self.request_util.post(
                endpoint=case_data["endpoint"],
                token=self.token,
                data=case_data["request_body"]
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

    # ===========================================================
    # 用例5: 减签_正常场景
    # ===========================================================
    @allure.title("减签_正常场景")
    @allure.description("从当前审批节点中移除一个审批人")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.workflow
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "减签_正常场景",
            "endpoint": "/workflow/task/deleteSign",
            "method": "post",
            "request_body": {
                "taskId": 1,
                "userId": 3
            },
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_workflow_delete_sign_success(self, case_data):
        with allure.step("Step 1: 发送减签请求"):
            response = self.request_util.post(
                endpoint=case_data["endpoint"],
                token=self.token,
                data=case_data["request_body"]
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

    # ===========================================================
    # 用例6: 终止流程实例_正常场景
    # ===========================================================
    @allure.title("终止流程实例_正常场景")
    @allure.description("管理员终止一个运行中的流程实例")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.workflow
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "终止流程实例_正常场景",
            "endpoint": "/workflow/process/stop",
            "method": "put",
            "request_body": {
                "procInstId": 1,
                "reason": "流程异常，管理员强制终止"
            },
            "expected_status": 200,
            "expected_code": 200,
        }
    ])
    def test_workflow_stop_success(self, case_data):
        with allure.step("Step 1: 发送终止流程请求"):
            response = self.request_util.put(
                endpoint=case_data["endpoint"],
                token=self.token,
                data=case_data["request_body"]
            )

        with allure.step("Step 2: 断言响应"):
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])


if __name__ == '__main__':
    print("=== 工作流操作测试用例自测 ===")
    print("  1. test_workflow_reject_success         - 驳回任务_正常场景")
    print("  2. test_workflow_cancel_success        - 撤回流程_正常场景")
    print("  3. test_workflow_delegate_success       - 转交任务_正常场景")
    print("  4. test_workflow_add_sign_before_success - 向前加签_正常场景")
    print("  5. test_workflow_delete_sign_success    - 减签_正常场景")
    print("  6. test_workflow_stop_success          - 终止流程实例_正常场景")
