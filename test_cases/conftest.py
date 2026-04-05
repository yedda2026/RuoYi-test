# ===========================================================
# RuoYi 平台接口自动化测试框架
# Pytest 全局配置和 Fixture
# ===========================================================
# 作者：ruoyi-test Team
# 版本：v1.0.0
# ===========================================================
# 模块说明：
#   - 定义全局的 pytest fixture
#   - 提供登录 token 的统一管理
#   - 提供数据库连接的统一管理
#   - 配置测试会话级别的资源
# ===========================================================

import pytest
import sys
import os

# 将项目根目录添加到 Python 路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from utils.request_util import RequestUtil
from utils.yaml_util import read_yaml
from utils.db_util import DBUtil, close_db


# ===========================================================
# 全局 Fixture 定义
# ===========================================================

@pytest.fixture(scope="session")
def login_token():
    """
    登录获取 RuoYi Bearer Token 的 Fixture

    scope=session: 整个测试会话只执行一次登录
    原因：登录接口通常有限流或性能影响，重复登录会拖慢测试速度

    :return: Bearer Token 字符串
    :raises AssertionError: 登录失败时抛出异常
    """
    print("\n" + "="*60)
    print("[Fixture] 初始化登录 Token（scope=session）")
    print("="*60)

    # 1. 从配置文件中读取登录信息
    config = read_yaml('config/config.yaml')
    env = config.get('env', 'test')
    env_config = config.get(env, {})

    username = env_config.get('username')
    password = env_config.get('password')

    print(f"[登录信息] 环境: {env}, 用户名: {username}")

    # 2. 创建请求工具实例
    request_util = RequestUtil()

    # 3. 调用 RuoYi 登录接口
    login_endpoint = '/login'
    login_data = {
        'username': username,
        'password': password
    }

    print(f"[登录请求] POST {login_endpoint}")
    print(f"[登录参数] username={username}, password={password}")

    try:
        response = request_util.post(
            endpoint=login_endpoint,
            data=login_data
        )

        # 4. 解析登录响应
        # RuoYi 登录响应结构：{"code": 200, "msg": "操作成功", "data": {"token": "xxx"}}
        resp_json = response.json()
        print(f"[登录响应] {resp_json}")

        # 提取 token
        token = resp_json.get('data', {}).get('token')

        if not token:
            raise ValueError("登录响应中未找到 token 字段")

        print(f"[Token 生成] {token[:20]}...（已截断）")
        print(f"[Token 长度] {len(token)} 字符")

        print("="*60)
        print("[Fixture] 登录 Token 获取成功，会话内复用")
        print("="*60 + "\n")

        return token

    except Exception as e:
        print(f"\n[X] 登录失败: {e}")
        raise


@pytest.fixture(scope="session")
def request_helper():
    """
    提供请求工具实例的 Fixture

    scope=session: 整个测试会话使用同一个 Session 实例

    :return: RequestUtil 实例
    """
    return RequestUtil()


@pytest.fixture(scope="session")
def db_helper():
    """
    提供数据库连接工具实例的 Fixture

    scope=session: 整个测试会话使用同一个数据库连接
    好处：复用连接，提升性能

    :return: DBUtil 实例
    """
    print("\n" + "="*60)
    print("[Fixture] 初始化数据库连接（scope=session）")
    print("="*60)

    db = DBUtil()
    db.connect()

    print("="*60)
    print("[Fixture] 数据库连接初始化成功")
    print("="*60 + "\n")

    yield db

    # 关闭数据库连接
    db.close()
    print("[Fixture] 数据库连接已关闭")


@pytest.fixture(scope="function")
def clean_test_data():
    """
    测试用例后置清理 Fixture

    scope=function: 每个测试函数执行后都会调用
    用于清理测试过程中产生的数据
    """
    yield
    print("\n[清理] 测试数据清理完成")


# ===========================================================
# Pytest 钩子函数（Hooks）
# ===========================================================

def pytest_configure(config):
    """
    Pytest 配置钩子 - 在测试运行前执行

    :param config: Pytest 配置对象
    """
    print("\n" + "="*60)
    print("RuoYi 平台接口自动化测试框架")
    print("Pytest 配置初始化中...")
    print("="*60)

    # 注册自定义 markers
    config.addinivalue_line("markers", "db_verify: 数据库验证测试")
    config.addinivalue_line("markers", "permission: 权限测试")
    config.addinivalue_line("markers", "workflow: 工作流测试")
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "regression: 回归测试")


def pytest_sessionstart(session):
    """
    测试会话开始钩子
    """
    print("\n[会话开始] 测试会话已启动")


def pytest_sessionfinish(session, exitstatus):
    """
    测试会话结束钩子
    """
    # 关闭全局数据库连接
    close_db()
    print("\n[会话结束] 测试会话已结束")
    print(f"[退出状态] {exitstatus}")


if __name__ == '__main__':
    print("=== Conftest 模块自测 ===")
    print("全局 Fixture 列表：")
    print("  - login_token (scope=session): 获取登录 Token")
    print("  - request_helper (scope=session): 获取请求工具实例")
    print("  - db_helper (scope=session): 获取数据库连接")
    print("  - clean_test_data (scope=function): 测试数据清理")
