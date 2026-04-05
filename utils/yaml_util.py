# ===========================================================
# RuoYi 平台接口自动化测试框架
# 工具函数模块 - YAML 文件读取封装
# ===========================================================
# 作者：ruoyi-test Team
# 版本：v1.0.0
# ===========================================================
# 模块说明：
#   - 提供统一的 YAML 文件读取接口
#   - 支持读取单个 YAML 文件
#   - 支持读取测试用例数据
# ===========================================================

import yaml
import os
from typing import Any, Dict


def get_yaml_path(filename: str) -> str:
    """
    获取 YAML 文件的绝对路径

    :param filename: YAML 文件名（包含相对路径）
    :return: YAML 文件的绝对路径
    :raises FileNotFoundError: 当文件不存在时抛出异常
    """
    # 获取项目根目录（utils 的上一级目录的上一级目录）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # d:\...\ruoyi-test\utils -> d:\...\ruoyi-test
    root_dir = os.path.dirname(os.path.dirname(current_dir))
    yaml_path = os.path.join(root_dir, filename)

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"YAML 文件不存在: {yaml_path}")

    return yaml_path


def read_yaml(filename: str) -> Dict[str, Any]:
    """
    读取 YAML 文件并返回字典格式的数据

    :param filename: YAML 文件名（支持相对路径，如 data/xxx/data.yaml）
    :return: YAML 文件解析后的字典数据
    :raises FileNotFoundError: 当文件不存在时抛出异常
    :raises yaml.YAMLError: 当 YAML 格式错误时抛出异常

    使用示例：
        data = read_yaml('config/config.yaml')
        print(data['database']['host'])
    """
    yaml_path = get_yaml_path(filename)

    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    return data if data is not None else {}


def read_yaml_by_key(filename: str, key: str) -> Any:
    """
    读取 YAML 文件中指定 key 的值

    :param filename: YAML 文件名（支持相对路径）
    :param key: 要读取的顶层 key
    :return: 指定 key 对应的值
    :raises KeyError: 当 key 不存在时抛出异常

    使用示例：
        db_config = read_yaml_by_key('config/config.yaml', 'database')
    """
    data = read_yaml(filename)
    return data.get(key)


if __name__ == '__main__':
    # 简单的自测代码
    print("=== YAML 工具函数自测 ===")

    # 测试读取配置文件
    try:
        config_data = read_yaml('config/config.yaml')
        print(f"配置文件读取成功，当前环境: {config_data.get('env')}")
        db_config = config_data.get('database', {})
        print(f"数据库配置: host={db_config.get('host')}, port={db_config.get('port')}")
    except Exception as e:
        print(f"配置文件读取失败: {e}")

    # 测试获取项目根目录
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"项目根目录: {root}")
