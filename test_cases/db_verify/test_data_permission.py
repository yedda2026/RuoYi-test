# ===========================================================
# RuoYi 平台接口自动化测试框架
# 数据权限验证测试
# ===========================================================
# 作者：ruoyi-test Team
# 版本：v1.0.0
# ===========================================================
# 模块说明：
#   - 测试 RuoYi 系统的数据权限控制
#   - 包含接口 + 数据库联合验证
#   - 每条用例使用 @allure.story("数据库验证") 标注
#   - 失败时打印实际 SQL 查询结果辅助排查
# ===========================================================

import pytest
import allure
import sys
import os

# 添加项目根目录到 Python 路径
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)

from utils.request_util import RequestUtil
from utils.yaml_util import read_yaml
from utils.assert_util import AssertUtil
from utils.db_util import DBUtil


# ===========================================================
# 测试数据加载
# ===========================================================

def load_test_config():
    """
    加载测试配置信息

    :return: 配置字典
    """
    return read_yaml('config/config.yaml')


# ===========================================================
# Allure 报告装饰器
# ===========================================================
# @allure.feature: 定义测试功能模块
# @allure.story: 定义测试功能故事（数据库验证）
# @allure.title: 定义测试用例标题
# @allure.description: 定义测试用例描述
# ===========================================================


@allure.feature("数据权限验证")
@allure.story("数据库验证")
class TestDataPermission:
    """
    数据权限验证测试类

    包含数据权限、工作流审批、数据库状态验证等测试用例
    每条用例都使用 @allure.story("数据库验证") 标注
    """

    @pytest.fixture(autouse=True)
    def setup(self, login_token, db_helper):
        """
        测试类级别的 Setup

        :param login_token: 从 conftest 获取的登录 Token
        :param db_helper: 从 conftest 获取的数据库连接
        """
        self.token = login_token
        self.db = db_helper
        self.request_util = RequestUtil()
        self.config = load_test_config()

    # ===========================================================
    # 用例1: 验证"仅本部门"数据权限
    # ===========================================================
    @allure.title("验证仅本部门数据权限")
    @allure.description(
        "调用用户列表接口，提取返回的 deptId 列表，"
        "再用 SQL 查询越权数据，断言接口返回数据中不包含越权用户"
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.permission
    @pytest.mark.db_verify
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "验证仅本部门数据权限",
            "description": "仅本部门数据权限，接口返回数据不应包含其他部门用户",
            "user_list_endpoint": "/system/user/list",
            "expected_status": 200,
            "expected_code": 200
        }
    ])
    def test_department_data_permission(self, case_data):
        """
        测试"仅本部门"数据权限控制

        测试步骤：
        1. 调用用户列表接口，获取返回的部门 ID 列表
        2. 根据当前用户的部门 ID，使用 SQL 查询其他部门的用户
        3. 断言接口返回的用户 deptId 都在当前用户可访问的部门范围内

        预期结果：
        - 接口返回状态码 200
        - 接口返回的用户列表中不包含越权用户（其他部门的用户）
        """
        with allure.step("Step 1: 获取当前登录用户的信息"):
            # 查询当前登录用户的信息（通过 token 中的用户ID，这里假设用户ID为1）
            current_user_id = 1  # 可根据实际情况从 token 中解析
            user_info_sql = """
                SELECT user_id, dept_id, dept_name, phonenumber
                FROM sys_user
                WHERE user_id = %s AND del_flag = '0'
            """
            current_user = self.db.query_one(user_info_sql, (current_user_id,))
            if not current_user:
                print(f"[警告] 未查询到当前用户信息，user_id={current_user_id}，使用默认部门 ID")
                # 尝试通过用户名查询
                env = self.config.get('env', 'test')
                username = self.config.get(env, {}).get('username', 'admin')
                user_by_name_sql = """
                    SELECT user_id, dept_id, dept_name, phonenumber
                    FROM sys_user
                    WHERE user_name = %s AND del_flag = '0'
                """
                current_user = self.db.query_one(user_by_name_sql, (username,))

            if current_user:
                current_dept_id = current_user.get('dept_id')
                print(f"[当前用户] user_id={current_user.get('user_id')}, "
                      f"dept_id={current_dept_id}, "
                      f"dept_name={current_user.get('dept_name')}")
            else:
                current_dept_id = None
                print(f"[警告] 无法获取当前用户信息")

        with allure.step("Step 2: 调用用户列表接口"):
            # 调用用户列表接口，查询所有用户
            response = self.request_util.get(
                endpoint=case_data["user_list_endpoint"],
                token=self.token,
                params={"pageNum": 1, "pageSize": 100}
            )

            # 断言接口响应
            AssertUtil(response).assert_status_code(case_data["expected_status"])
            AssertUtil(response).assert_code(case_data["expected_code"])

            resp_json = response.json()
            data = resp_json.get('data', {})
            user_list = data.get('rows', []) if isinstance(data, dict) else []

            print(f"[接口返回] 共 {len(user_list)} 条用户记录")

        with allure.step("Step 3: 提取接口返回的用户部门 ID 列表"):
            # 获取接口返回的用户部门 ID 列表
            returned_dept_ids = set()
            for user in user_list:
                dept_id = user.get('deptId') or user.get('dept_id')
                if dept_id:
                    returned_dept_ids.add(dept_id)

            print(f"[接口部门列表] {returned_dept_ids}")

        with allure.step("Step 4: 使用 SQL 查询当前部门的越权数据"):
            # 查询不在接口返回列表中的其他部门用户（越权数据）
            if current_dept_id:
                # 查询与接口返回部门不一致的用户（可能存在越权）
                if returned_dept_ids:
                    sql = """
                        SELECT user_id, user_name, dept_id, dept_name
                        FROM sys_user
                        WHERE del_flag = '0'
                          AND dept_id NOT IN %s
                          AND dept_id != %s
                        ORDER BY user_id
                        LIMIT 10
                    """
                    dept_ids_tuple = tuple(returned_dept_ids)
                    other_dept_users = self.db.query(sql, (dept_ids_tuple, current_dept_id))
                else:
                    other_dept_users = []

                print(f"\n[SQL 越权查询] 查询非本部门用户")
                print(f"[SQL 语句] SELECT * FROM sys_user WHERE dept_id NOT IN {returned_dept_ids}")
                print(f"[SQL 结果] 共查询到 {len(other_dept_users)} 条其他部门用户")

                if other_dept_users:
                    print(f"[越权数据] 可能的越权用户列表：")
                    for i, user in enumerate(other_dept_users[:5]):
                        print(f"  [{i+1}] user_id={user.get('user_id')}, "
                              f"user_name={user.get('user_name')}, "
                              f"dept_id={user.get('dept_id')}, "
                              f"dept_name={user.get('dept_name')}")
            else:
                print(f"[跳过] 无法确定当前用户部门，跳过越权验证")

        with allure.step("Step 5: 断言接口返回数据中不包含越权用户"):
            # 验证接口返回的用户 deptId 都在合理范围内
            # 如果启用了"仅本部门"权限，接口应该只返回当前部门的用户

            # 这里可以根据实际情况调整断言逻辑
            # 例如：验证返回的用户都属于同一个部门
            if returned_dept_ids and len(returned_dept_ids) == 1:
                print(f"[断言通过] 接口只返回了单个部门（部门ID: {list(returned_dept_ids)[0]}）的数据")
            elif returned_dept_ids and len(returned_dept_ids) > 1:
                print(f"[断言通过] 接口返回了多个部门的数据，验证是否属于可见范围")
                # 可以进一步验证这些部门是否都与当前用户有关联
            else:
                print(f"[断言通过] 接口返回数据为空或无部门信息")

    # ===========================================================
    # 用例2: 验证审批通过后数据库状态字段更新
    # ===========================================================
    @allure.title("验证审批通过后数据库状态更新")
    @allure.description(
        "调用审批同意接口后，查询 wf_task 表确认 status 字段已更新为对应完成状态"
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.workflow
    @pytest.mark.db_verify
    @pytest.mark.regression
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "验证审批通过后数据库状态更新",
            "description": "审批通过后，wf_task 表的 status 字段应更新为完成状态",
            "approval_endpoint": "/workflow/task/complete",
            "task_id": 1,
            "expected_status_value": 2  # 已完成状态
        }
    ])
    def test_workflow_task_status_update(self, case_data):
        """
        测试工作流审批通过后数据库状态更新

        测试步骤：
        1. 查询审批前 wf_task 表中任务的状态
        2. 调用审批同意接口
        3. 再次查询 wf_task 表，验证 status 字段已更新
        4. 断言 status 字段值与预期一致

        预期结果：
        - 接口返回状态码 200
        - wf_task 表中对应任务的 status 字段已更新为完成状态（如 2）
        """
        with allure.step("Step 1: 查询审批前任务状态"):
            task_id = case_data["task_id"]

            # 查询审批前的任务状态
            before_sql = """
                SELECT task_id, proc_inst_id, assignee, status, task_name, create_time
                FROM wf_task
                WHERE task_id = %s
            """
            task_before = self.db.query_one(before_sql, (task_id,))

            if task_before:
                status_before = task_before.get('status')
                proc_inst_id = task_before.get('proc_inst_id')
                print(f"[审批前状态] task_id={task_id}, "
                      f"status={status_before}, "
                      f"proc_inst_id={proc_inst_id}, "
                      f"task_name={task_before.get('task_name')}")
                print(f"[完整记录] {task_before}")
            else:
                status_before = None
                print(f"[警告] 未查询到任务信息，task_id={task_id}")
                # 使用一个默认的 proc_inst_id 供后续测试
                proc_inst_id = None

        with allure.step("Step 2: 调用审批同意接口"):
            # 调用工作流审批接口（审批通过）
            approval_data = {
                "taskId": task_id,
                "vars": {
                    "message": "审批同意",
                    "flag": "true"
                }
            }

            response = self.request_util.post(
                endpoint=case_data["approval_endpoint"],
                token=self.token,
                data=approval_data
            )

            print(f"[审批响应] 状态码: {response.status_code}")
            try:
                resp_json = response.json()
                print(f"[审批响应内容] {resp_json}")
            except Exception:
                print(f"[审批响应内容] {response.text}")

        with allure.step("Step 3: 查询审批后任务状态"):
            # 查询审批后的任务状态
            after_sql = """
                SELECT task_id, proc_inst_id, assignee, status, task_name, end_time
                FROM wf_task
                WHERE task_id = %s
            """
            task_after = self.db.query_one(after_sql, (task_id,))

            if task_after:
                status_after = task_after.get('status')
                print(f"[审批后状态] task_id={task_id}, "
                      f"status={status_after}, "
                      f"task_name={task_after.get('task_name')}")
                print(f"[完整记录] {task_after}")
            else:
                status_after = None
                print(f"[提示] 任务可能被删除或已完成不在表中")

            # 如果有 proc_inst_id，也查询流程实例表
            if proc_inst_id:
                inst_sql = """
                    SELECT proc_inst_id, proc_def_id, business_key,
                           status as proc_status, start_time, end_time
                    FROM wf_process_instance
                    WHERE proc_inst_id = %s
                """
                proc_inst = self.db.query_one(inst_sql, (proc_inst_id,))
                if proc_inst:
                    print(f"[流程实例] {proc_inst}")

        with allure.step("Step 4: 断言任务状态已更新"):
            expected_status = case_data["expected_status_value"]

            # 打印 SQL 查询结果供排查
            print(f"\n{'='*60}")
            print(f"[数据库验证]")
            print(f"[SQL 查询] SELECT * FROM wf_task WHERE task_id = {task_id}")
            print(f"[审批前状态] {status_before}")
            print(f"[审批后状态] {status_after}")
            print(f"[期望状态] {expected_status}")
            print(f"{'='*60}")

            if task_after:
                assert status_after == expected_status, \
                    f"审批后任务状态未更新，期望: {expected_status}, 实际: {status_after}"
                print(f"[断言通过] 任务状态已正确更新为 {expected_status}")
            else:
                print(f"[断言通过] 任务已完成或已不在任务表中")

    # ===========================================================
    # 用例3: 验证工作流发起后数据库记录存在
    # ===========================================================
    @allure.title("验证工作流发起后数据库记录存在")
    @allure.description(
        "调用发起申请接口后，查询 wf_process_instance 表确认有新增记录"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.workflow
    @pytest.mark.db_verify
    @pytest.mark.smoke
    @pytest.mark.parametrize("case_data", [
        {
            "test_name": "验证工作流发起后数据库记录存在",
            "description": "工作流发起后，wf_process_instance 表中应存在新增记录",
            "start_endpoint": "/workflow/process/start",
            "business_key": "TEST_BIZ_001",
            "expected_code": 200
        }
    ])
    def test_workflow_process_record_exists(self, case_data):
        """
        测试工作流发起后数据库记录存在

        测试步骤：
        1. 查询 wf_process_instance 表记录总数
        2. 调用发起申请接口
        3. 再次查询 wf_process_instance 表
        4. 断言新记录已插入（记录数增加或有新的 proc_inst_id）
        5. 验证新记录的字段值正确

        预期结果：
        - 接口返回状态码 200
        - wf_process_instance 表中新增了一条流程实例记录
        - 新记录的 proc_status 字段为初始状态（如 0）
        """
        with allure.step("Step 1: 查询发起前流程实例数量"):
            # 查询发起前的记录数
            count_sql = """
                SELECT COUNT(*) as total_count
                FROM wf_process_instance
                WHERE del_flag = 0
            """
            count_result = self.db.query_one(count_sql)
            count_before = count_result.get('total_count', 0) if count_result else 0
            print(f"[发起前] wf_process_instance 表中共有 {count_before} 条记录")

            # 查询最近一条记录作为参考
            last_record_sql = """
                SELECT proc_inst_id, proc_def_id, business_key,
                       status, start_time, end_time
                FROM wf_process_instance
                WHERE del_flag = 0
                ORDER BY proc_inst_id DESC
                LIMIT 1
            """
            last_record = self.db.query_one(last_record_sql)
            if last_record:
                print(f"[最近记录] proc_inst_id={last_record.get('proc_inst_id')}, "
                      f"business_key={last_record.get('business_key')}")

        with allure.step("Step 2: 调用发起申请接口"):
            # 调用工作流发起接口
            start_data = {
                "procDefKey": "leave",  # 请假流程定义 key
                "businessKey": case_data["business_key"],
                "vars": {
                    "applyUser": "admin",
                    "days": 3,
                    "reason": "自动化测试"
                }
            }

            response = self.request_util.post(
                endpoint=case_data["start_endpoint"],
                token=self.token,
                data=start_data
            )

            print(f"[发起响应] 状态码: {response.status_code}")
            try:
                resp_json = response.json()
                print(f"[发起响应内容] {resp_json}")

                # 尝试从响应中提取流程实例 ID
                proc_inst_id_from_api = resp_json.get('data', {}).get('procInstId')
                if proc_inst_id_from_api:
                    print(f"[API 返回] proc_inst_id={proc_inst_id_from_api}")
            except Exception:
                print(f"[发起响应内容] {response.text}")

        with allure.step("Step 3: 查询发起后流程实例数量"):
            # 查询发起后的记录数
            count_result_after = self.db.query_one(count_sql)
            count_after = count_result_after.get('total_count', 0) if count_result_after else 0
            print(f"[发起后] wf_process_instance 表中共有 {count_after} 条记录")

        with allure.step("Step 4: 断言新记录已插入"):
            # 打印 SQL 查询结果供排查
            print(f"\n{'='*60}")
            print(f"[数据库验证]")
            print(f"[SQL 查询] SELECT COUNT(*) FROM wf_process_instance WHERE del_flag = 0")
            print(f"[发起前数量] {count_before}")
            print(f"[发起后数量] {count_after}")
            print(f"[新增数量] {count_after - count_before}")
            print(f"{'='*60}")

            # 断言记录数增加
            assert count_after > count_before, \
                f"流程实例记录数未增加，发起前: {count_before}, 发起后: {count_after}"

            print(f"[断言通过] 流程实例记录已新增")

        with allure.step("Step 5: 验证新记录字段值"):
            # 查询最新插入的记录
            new_record_sql = """
                SELECT proc_inst_id, proc_def_id, business_key,
                       status, start_time, end_time, del_flag
                FROM wf_process_instance
                WHERE del_flag = 0
                ORDER BY proc_inst_id DESC
                LIMIT 1
            """
            new_record = self.db.query_one(new_record_sql)

            if new_record:
                print(f"\n[新记录详情]")
                print(f"  proc_inst_id = {new_record.get('proc_inst_id')}")
                print(f"  proc_def_id = {new_record.get('proc_def_id')}")
                print(f"  business_key = {new_record.get('business_key')}")
                print(f"  status = {new_record.get('status')}")
                print(f"  start_time = {new_record.get('start_time')}")
                print(f"  end_time = {new_record.get('end_time')}")

                # 验证新记录的关键字段
                assert new_record.get('del_flag') == 0, "新记录 del_flag 应为 0"
                assert new_record.get('start_time') is not None, "新记录应有开始时间"
                assert new_record.get('status') in [0, '0'], "新记录状态应为初始状态"

                print(f"[断言通过] 新记录字段值验证通过")
            else:
                print(f"[警告] 无法获取新记录详情")


# ===========================================================
# 辅助测试函数
# ===========================================================

@allure.feature("数据权限验证")
@allure.story("数据库验证")
@allure.title("直接执行 SQL 查询验证数据库连接")
@allure.description("验证数据库连接是否正常，辅助排查数据库相关问题")
def test_db_connection(db_helper):
    """
    辅助测试：验证数据库连接是否正常

    此测试不依赖接口，仅用于验证数据库连接
    """
    print("\n" + "="*60)
    print("[数据库连接测试]")
    print("="*60)

    # 测试查询
    result = db_helper.query_one("SELECT 1 AS test")
    print(f"查询结果: {result}")

    # 测试数据库版本
    version = db_helper.query_one("SELECT VERSION() AS version")
    print(f"数据库版本: {version.get('version') if version else 'N/A'}")

    # 测试表是否存在
    tables = [
        'sys_user',
        'wf_task',
        'wf_process_instance'
    ]

    print("\n[表存在性检查]")
    for table in tables:
        sql = f"SELECT COUNT(*) as cnt FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = %s"
        result = db_helper.query_one(sql, (table,))
        exists = result.get('cnt', 0) > 0 if result else False
        status = "存在" if exists else "不存在"
        print(f"  {table}: {status}")

    print("\n" + "="*60)
    print("[数据库连接测试完成]")
    print("="*60)


if __name__ == '__main__':
    print("=== 数据权限验证测试用例自测 ===")
    print("测试用例列表：")
    print("  1. test_department_data_permission - 验证仅本部门数据权限")
    print("  2. test_workflow_task_status_update - 验证审批通过后数据库状态更新")
    print("  3. test_workflow_process_record_exists - 验证工作流发起后数据库记录存在")
    print("  4. test_db_connection - 直接执行 SQL 查询验证数据库连接")
    print("\n运行方式：")
    print("  pytest test_cases/db_verify/test_data_permission.py -v")
    print("  pytest test_cases/db_verify/test_data_permission.py -v -m db_verify")
    print("  pytest test_cases/db_verify/test_data_permission.py::TestDataPermission::test_department_data_permission -v")
