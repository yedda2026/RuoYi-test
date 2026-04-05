# ===========================================================
# RuoYi 平台接口自动化测试框架
# 工具函数模块 - 常用断言方法封装
# ===========================================================
# 作者：ruoyi-test Team
# 版本：v1.0.0
# ===========================================================
# 模块说明：
#   - 封装常用的断言方法，统一断言风格
#   - 提供清晰的断言失败信息
#   - 支持多种断言场景
# ===========================================================

from typing import Any, Optional
from requests import Response


class AssertUtil:
    """
    断言工具类
    提供统一的断言方法，简化测试用例中的断言编写
    """

    def __init__(self, response: Response):
        """
        初始化断言工具实例

        :param response: requests 库的 Response 对象
        """
        self.response = response
        self.res_json = response.json() if self._is_json() else None

    def _is_json(self) -> bool:
        """
        判断响应内容是否为 JSON 格式

        :return: 是 JSON 返回 True，否则返回 False
        """
        try:
            self.response.json()
            return True
        except Exception:
            return False

    def assert_status_code(self, expected_code: int, message: Optional[str] = None) -> None:
        """
        断言 HTTP 状态码

        :param expected_code: 期望的 HTTP 状态码
        :param message: 自定义失败信息（可选）
        :raises AssertionError: 状态码不匹配时抛出异常

        使用示例：
            AssertUtil(response).assert_status_code(200)
        """
        actual_code = self.response.status_code
        error_msg = message or f"状态码断言失败，期望: {expected_code}, 实际: {actual_code}"
        assert actual_code == expected_code, error_msg

    def assert_code(self, expected_code: int, code_key: str = 'code') -> None:
        """
        断言响应体中的 code 字段值

        :param expected_code: 期望的 code 值
        :param code_key: code 字段的键名，默认为 'code'
        :raises AssertionError: code 不匹配或响应非 JSON 时抛出异常

        使用示例：
            AssertUtil(response).assert_code(200)
        """
        assert self.res_json is not None, "响应体不是 JSON 格式，无法断言 code 字段"
        actual_code = self.res_json[code_key]
        assert actual_code == expected_code, \
            f"响应 code 断言失败，期望: {expected_code}, 实际: {actual_code}"

    def assert_code_message(self, expected_code: int, expected_message: str,
                           code_key: str = 'code', message_key: str = 'msg') -> None:
        """
        断言响应体中的 code 和 message 字段值

        :param expected_code: 期望的 code 值
        :param expected_message: 期望的 message 值
        :param code_key: code 字段的键名，默认为 'code'
        :param message_key: message 字段的键名，默认为 'msg'
        :raises AssertionError: code 或 message 不匹配时抛出异常
        """
        assert self.res_json is not None, "响应体不是 JSON 格式"
        actual_code = self.res_json.get(code_key)
        actual_message = self.res_json.get(message_key)
        assert actual_code == expected_code and actual_message == expected_message, \
            f"断言失败 - 期望 code: {expected_code}, msg: {expected_message}, " \
            f"实际 code: {actual_code}, msg: {actual_message}"

    def assert_msg_contains(self, expected_text: str, msg_key: str = 'msg') -> None:
        """
        断言响应 msg 字段包含指定文本

        :param expected_text: 期望包含的文本
        :param msg_key: message 字段键名，默认为 'msg'
        :raises AssertionError: 不包含时抛出异常
        """
        assert self.res_json is not None, "响应体不是 JSON 格式"
        actual_msg = str(self.res_json.get(msg_key, ''))
        assert expected_text in actual_msg, \
            f"msg 不包含期望文本，期望包含: {expected_text}, 实际: {actual_msg}"

    def assert_field_not_null(self, field_name: str, field_key: Optional[str] = None) -> Any:
        """
        断言字段值不为空，并返回字段值

        :param field_name: 要检查的字段名
        :param field_key: 如果要检查嵌套字段，传入嵌套的键路径（可选）
        :return: 字段的实际值
        :raises AssertionError: 字段为空或不存在时抛出异常
        """
        assert self.res_json is not None, "响应体不是 JSON 格式，无法断言字段"

        if field_key:
            if field_key in self.res_json and isinstance(self.res_json[field_key], dict):
                data = self.res_json[field_key]
                assert field_name in data, f"字段 {field_name} 在 {field_key} 中不存在"
                value = data[field_name]
            else:
                raise KeyError(f"指定的父字段 {field_key} 不存在或不是字典类型")
        else:
            assert field_name in self.res_json, f"字段 {field_name} 不存在于响应中"
            value = self.res_json[field_name]

        assert value is not None and value != '', \
            f"字段 {field_name} 值为空，不符合预期"
        return value

    def assert_field_equals(self, field_name: str, expected_value: Any,
                           field_key: Optional[str] = None) -> None:
        """
        断言字段值等于指定值

        :param field_name: 要检查的字段名
        :param expected_value: 期望的值
        :param field_key: 如果要检查嵌套字段，传入嵌套的键路径（可选）
        :raises AssertionError: 字段值不匹配时抛出异常
        """
        actual_value = self.field_value(field_name, field_key)
        assert actual_value == expected_value, \
            f"字段 {field_name} 断言失败，期望: {expected_value}, 实际: {actual_value}"

    def field_value(self, field_name: str, field_key: Optional[str] = None) -> Any:
        """
        获取字段的实际值（不进行断言）

        :param field_name: 字段名
        :param field_key: 嵌套路径（可选）
        :return: 字段的实际值
        """
        assert self.res_json is not None, "响应体不是 JSON 格式"

        if field_key:
            if field_key in self.res_json and isinstance(self.res_json[field_key], dict):
                data = self.res_json[field_key]
                return data.get(field_name)
            return None
        return self.res_json.get(field_name)


# ===========================================================
# 辅助断言函数（非类方法，可直接调用）
# ===========================================================

def assert_true(condition: bool, message: str = "条件断言失败") -> None:
    """
    断言条件为 True

    :param condition: 条件表达式
    :param message: 失败时的提示信息
    :raises AssertionError: 条件为 False 时抛出异常
    """
    assert condition, message


def assert_equal(actual: Any, expected: Any, message: Optional[str] = None) -> None:
    """
    断言两个值相等

    :param actual: 实际值
    :param expected: 期望值
    :param message: 失败时的提示信息
    :raises AssertionError: 值不相等时抛出异常
    """
    error_msg = message or f"值不相等，期望: {expected}, 实际: {actual}"
    assert actual == expected, error_msg


def assert_in(actual: Any, expected: Any, message: Optional[str] = None) -> None:
    """
    断言 actual in expected

    :param actual: 要检查的值
    :param expected: 容器或字符串
    :param message: 失败时的提示信息
    :raises AssertionError: 不包含时抛出异常
    """
    error_msg = message or f"期望值不在实际结果中，期望: {expected}, 实际: {actual}"
    assert actual in expected, error_msg


if __name__ == '__main__':
    print("=== 断言工具类自测 ===")
    print("AssertUtil 类提供以下断言方法：")
    print("  - assert_status_code: 断言 HTTP 状态码")
    print("  - assert_code: 断言响应 code 字段")
    print("  - assert_code_message: 断言 code 和 msg")
    print("  - assert_msg_contains: 断言 msg 包含文本")
    print("  - assert_field_not_null: 断言字段不为空")
    print("  - assert_field_equals: 断言字段等于某值")
