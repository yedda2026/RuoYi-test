# ===========================================================
# RuoYi 平台接口自动化测试框架
# 工具函数模块 - MySQL 数据库操作封装
# ===========================================================
# 作者：ruoyi-test Team
# 版本：v1.0.0
# ===========================================================
# 模块说明：
#   - 提供 MySQL 数据库连接和操作封装
#   - 支持查询、增删改等数据库操作
#   - 从 config/config.yaml 读取数据库连接配置
#   - 包含完整的异常处理机制
# ===========================================================

import pymysql
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager

from .yaml_util import read_yaml


class DBUtil:
    """
    MySQL 数据库操作工具类

    提供数据库连接、查询、关闭等功能
    """

    def __init__(self):
        """
        初始化数据库连接工具
        从配置文件中读取数据库连接参数
        """
        self.config = self._load_db_config()
        self.connection: Optional[pymysql.Connection] = None
        self.cursor: Optional[pymysql.cursors.Cursor] = None

    def _load_db_config(self) -> Dict[str, Any]:
        """
        从配置文件中加载数据库连接配置

        :return: 数据库配置字典
        :raises KeyError: 配置文件格式错误时抛出异常
        """
        config = read_yaml('config/config.yaml')
        db_config = config.get('database', {})

        if not db_config:
            raise KeyError("配置文件中未找到 database 配置")

        return {
            'host': db_config.get('host', 'localhost'),
            'port': db_config.get('port', 3306),
            'user': db_config.get('user', 'root'),
            'password': db_config.get('password', ''),
            'database': db_config.get('database', ''),
            'charset': 'utf8mb4'
        }

    def connect(self) -> None:
        """
        建立数据库连接

        :raises pymysql.MySQLError: 连接失败时抛出异常
        """
        try:
            print(f"\n[数据库连接] 正在连接 {self.config['host']}:{self.config['port']}")
            print(f"[数据库连接] 数据库: {self.config['database']}")

            self.connection = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                charset=self.config['charset'],
                cursorclass=pymysql.cursors.DictCursor
            )

            self.cursor = self.connection.cursor()
            print(f"[数据库连接] 连接成功！")

        except pymysql.MySQLError as e:
            print(f"[X 数据库连接失败] {type(e).__name__}: {e}")
            raise

    def _ensure_connection(self) -> None:
        """
        确保数据库连接处于活跃状态
        如果连接已断开或不存在，自动重连

        :raises pymysql.MySQLError: 重连失败时抛出异常
        """
        if self.connection is None or not self.connection.open:
            print("[数据库] 连接已断开，正在重新连接...")
            self.connect()
        else:
            try:
                self.connection.ping(reconnect=True)
            except Exception:
                print("[数据库] Ping 失败，正在重新连接...")
                self.connect()

    def query(self, sql: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        执行 SELECT 查询语句，返回所有结果

        :param sql: SQL 查询语句（使用 %s 占位符）
        :param params: 查询参数元组（可选）
        :return: 查询结果列表，每条记录为一个字典
        :raises pymysql.MySQLError: 查询失败时抛出异常

        使用示例：
            results = db.query("SELECT * FROM sys_user WHERE status = %s", (0,))
            for row in results:
                print(row['user_name'])
        """
        self._ensure_connection()

        try:
            print(f"\n[SQL 查询] {sql}")
            if params:
                print(f"[SQL 参数] {params}")

            self.cursor.execute(sql, params)
            results = self.cursor.fetchall()

            print(f"[SQL 结果] 共返回 {len(results)} 条记录")
            if results and len(results) <= 5:
                for i, row in enumerate(results):
                    print(f"  [{i+1}] {row}")
            elif results:
                print(f"  [前5条] {results[:5]}")

            return results

        except pymysql.MySQLError as e:
            print(f"\n[X SQL 查询异常] {type(e).__name__}: {e}")
            print(f"[X SQL 语句] {sql}")
            if params:
                print(f"[X SQL 参数] {params}")
            raise

    def query_one(self, sql: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        """
        执行 SELECT 查询语句，返回单条结果

        :param sql: SQL 查询语句（使用 %s 占位符）
        :param params: 查询参数元组（可选）
        :return: 单条记录字典，如果没有结果则返回 None
        :raises pymysql.MySQLError: 查询失败时抛出异常

        使用示例：
            user = db.query_one("SELECT * FROM sys_user WHERE user_id = %s", (1,))
            if user:
                print(user['user_name'])
        """
        self._ensure_connection()

        try:
            print(f"\n[SQL 查询单条] {sql}")
            if params:
                print(f"[SQL 参数] {params}")

            self.cursor.execute(sql, params)
            result = self.cursor.fetchone()

            if result:
                print(f"[SQL 结果] {result}")
            else:
                print(f"[SQL 结果] 无记录")

            return result

        except pymysql.MySQLError as e:
            print(f"\n[X SQL 查询异常] {type(e).__name__}: {e}")
            print(f"[X SQL 语句] {sql}")
            if params:
                print(f"[X SQL 参数] {params}")
            raise

    def execute(self, sql: str, params: Optional[Tuple] = None) -> int:
        """
        执行增删改语句（INSERT/UPDATE/DELETE）

        :param sql: SQL 语句（使用 %s 占位符）
        :param params: 参数元组（可选）
        :return: 受影响的行数
        :raises pymysql.MySQLError: 执行失败时抛出异常

        使用示例：
            affected = db.execute("UPDATE sys_user SET status = %s WHERE user_id = %s", (1, 1))
            db.commit()
            print(f"受影响行数: {affected}")
        """
        self._ensure_connection()

        try:
            print(f"\n[SQL 执行] {sql}")
            if params:
                print(f"[SQL 参数] {params}")

            affected_rows = self.cursor.execute(sql, params)

            print(f"[SQL 结果] 受影响行数: {affected_rows}")

            return affected_rows

        except pymysql.MySQLError as e:
            print(f"\n[X SQL 执行异常] {type(e).__name__}: {e}")
            print(f"[X SQL 语句] {sql}")
            if params:
                print(f"[X SQL 参数] {params}")
            raise

    def commit(self) -> None:
        """
        提交当前事务
        """
        if self.connection:
            try:
                self.connection.commit()
                print("[数据库] 事务已提交")
            except pymysql.MySQLError as e:
                print(f"[X 提交失败] {type(e).__name__}: {e}")
                raise

    def rollback(self) -> None:
        """
        回滚当前事务
        """
        if self.connection:
            try:
                self.connection.rollback()
                print("[数据库] 事务已回滚")
            except pymysql.MySQLError as e:
                print(f"[X 回滚失败] {type(e).__name__}: {e}")
                raise

    def close(self) -> None:
        """
        关闭数据库连接和游标
        """
        try:
            if self.cursor:
                self.cursor.close()
                print("[数据库] 游标已关闭")
                self.cursor = None

            if self.connection:
                self.connection.close()
                print("[数据库] 连接已关闭")
                self.connection = None

        except Exception as e:
            print(f"[X 关闭连接时出错] {type(e).__name__}: {e}")

    def __enter__(self):
        """
        支持 with 语句自动连接

        使用示例：
            with DBUtil() as db:
                results = db.query("SELECT * FROM sys_user")
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出 with 语句时自动关闭连接
        如果发生异常则回滚事务
        """
        if exc_type is not None:
            print(f"[数据库] 检测到异常，正在回滚...")
            self.rollback()
        self.close()
        return False

    def get_scalar(self, sql: str, params: Optional[Tuple] = None) -> Any:
        """
        执行查询并返回单个标量值（用于 COUNT、SUM、MAX 等聚合查询）

        :param sql: SQL 查询语句
        :param params: 参数元组（可选）
        :return: 查询到的标量值，如果没有则返回 None

        使用示例：
            count = db.get_scalar("SELECT COUNT(*) FROM sys_user WHERE status = %s", (0,))
        """
        result = self.query_one(sql, params)
        if result:
            return list(result.values())[0]
        return None


# ===========================================================
# 全局数据库实例（延迟初始化）
# ===========================================================

_db_instance: Optional[DBUtil] = None


def get_db() -> DBUtil:
    """
    获取全局数据库实例（单例模式）

    :return: DBUtil 实例
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DBUtil()
        _db_instance.connect()
    return _db_instance


def close_db() -> None:
    """
    关闭全局数据库实例
    """
    global _db_instance
    if _db_instance is not None:
        _db_instance.close()
        _db_instance = None


if __name__ == '__main__':
    # 简单的自测代码
    print("=== DBUtil 数据库工具类自测 ===")

    try:
        # 使用 with 语句自动管理连接
        with DBUtil() as db:
            # 测试查询
            print("\n--- 测试查询单条 ---")
            result = db.query_one("SELECT 1 AS test")
            print(f"查询结果: {result}")

            # 测试列表查询
            print("\n--- 测试列表查询 ---")
            results = db.query("SELECT 'A' AS col UNION SELECT 'B' AS col")
            print(f"查询结果: {results}")

    except Exception as e:
        print(f"\n自测失败: {e}")
