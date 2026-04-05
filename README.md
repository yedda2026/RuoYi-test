# ruoyi-test

> 基于 [RuoYi-Vue-Pro](https://github.com/YunaiV/ruoyi-vue-pro) 的接口自动化测试框架（含数据库验证）

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Pytest-8.3-green.svg)](https://pytest.org/)
[![PyMySQL](https://img.shields.io/badge/PyMySQL-1.1-red.svg)](https://pymysql.org/)
[![Allure](https://img.shields.io/badge/Allure-Report-orange.svg)](https://allurtest.info/)

## 项目简介

`ruoyi-test` 是针对 [RuoYi-Vue-Pro](https://github.com/YunaiV/ruoyi-vue-pro) 后台管理系统设计的接口自动化测试框架，基于 **Python + Pytest + PyMySQL + Allure** 构建，支持接口测试与数据库联合验证，覆盖数据权限、工作流审批等场景。

### 被测系统

| 项目 | 说明 | 地址 |
|------|------|------|
| RuoYi-Vue-Pro | SpringBoot + MyBatis Plus + Vue 后台管理系统，支持 RBAC、数据权限、Flowable 工作流等 | [GitHub](https://github.com/YunaiV/ruoyi-vue-pro) |

---

## 测试用例概览

### 模块分布

```
ruoyi-test
├── test_cases/
│   ├── conftest.py                  # 全局 Fixture（login_token + db_helper）
│   └── db_verify/
│       └── test_data_permission.py  # 数据库验证（3 条用例）
└── utils/
    ├── __init__.py
    ├── yaml_util.py                  # YAML 读取工具
    ├── request_util.py              # HTTP 请求封装（Bearer Token）
    ├── assert_util.py               # 断言工具类（支持 RuoYi 的 code/msg 结构）
    └── db_util.py                  # MySQL 数据库操作封装
```

### 功能测试思维导图

```
RuoYi 平台测试
│
├── [D] 数据库验证（3 条用例）
│   │
│   ├── D1_验证仅本部门数据权限
│   │   ├─ 接口调用：GET /system/user/list
│   │   ├─ SQL 提取：从 sys_user 提取返回的 deptId 列表
│   │   ├─ 越权查询：SELECT dept_id FROM sys_user WHERE dept_id NOT IN (本部门ID)
│   │   └─ 验证点：接口返回数据中不包含越权用户
│   │
│   ├── D2_验证审批通过后数据库状态更新
│   │   ├─ 接口调用：POST /workflow/task/complete
│   │   ├─ 前置查询：SELECT status FROM wf_task WHERE task_id = ?
│   │   ├─ 审批后查询：再次查询 wf_task 表 status 字段
│   │   └─ 验证点：status 已更新为完成状态（如 2）
│   │
│   └── D3_验证工作流发起后数据库记录存在
│       ├─ 计数查询：SELECT COUNT(*) FROM wf_process_instance
│       ├─ 接口调用：POST /workflow/process/start
│       ├─ 再次计数：确认 count + 1
│       └─ 验证点：新记录存在，proc_status = 初始状态
│
└── [W] 辅助验证：数据库连接可用性
    └─ 直接执行 SQL 查询，验证表存在性（sys_user / wf_task / wf_process_instance）
```

---

## 用例详情

### 数据库验证（3 条）

| ID | 用例名称 | 接口 / SQL | 验证点 | 失败时打印 |
|----|---------|-----------|--------|-----------|
| D1 | 验证仅本部门数据权限 | GET /system/user/list + sys_user 查询 | 接口返回数据不包含其他部门用户 | 越权用户列表（user_id/dept_id/dept_name） |
| D2 | 验证审批通过后数据库状态更新 | POST /workflow/task/complete + wf_task 查询 | wf_task.status = 2（完成） | 审批前/后状态值 + 完整记录 |
| D3 | 验证工作流发起后数据库记录存在 | POST /workflow/process/start + wf_process_instance 查询 | count + 1，新记录字段正确 | 发起前/后数量 + 新记录详情 |

---

## 快速开始

### 1. 安装依赖

```bash
cd ruoyi-test
pip install -r requirements.txt
```

### 2. 配置环境

编辑 `config/config.yaml`：

```yaml
env: test

test:
  base_url: http://localhost:8080      # RuoYi 服务地址
  username: admin
  password: admin123

database:
  host: localhost
  port: 3306
  user: root
  password: root123
  database: ry_cloud                   # RuoYi 数据库名
```

### 3. 运行测试

```bash
# 运行全部用例
pytest test_cases/ -v

# 只运行数据库验证用例
pytest test_cases/ -v -m db_verify

# 运行单个用例
pytest "test_cases/db_verify/test_data_permission.py::TestDataPermission::test_department_data_permission" -v

# 生成 Allure 报告
pytest test_cases/ -v --alluredir=reports/allure-results
allure serve reports/allure-results
```

---

## 项目结构

```
ruoyi-test/
├── config/
│   └── config.yaml              # 环境配置（含 database 连接配置）
├── utils/
│   ├── __init__.py
│   ├── yaml_util.py            # YAML 读取工具
│   ├── request_util.py         # HTTP 请求封装（自动添加 Bearer Token）
│   ├── assert_util.py          # 断言工具类（RuoYi code/msg 结构）
│   └── db_util.py              # MySQL 数据库操作封装
├── test_cases/
│   ├── conftest.py             # 全局 Fixture（login_token + db_helper）
│   └── db_verify/
│       └── test_data_permission.py  # 数据库验证用例（3 条）
├── pytest.ini                   # Pytest 配置（含 db_verify/workflow 等标记）
├── requirements.txt             # Python 依赖（含 PyMySQL）
└── README.md
```

---

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 编程语言 |
| Pytest | 8.3 | 测试框架 |
| Requests | 2.32 | HTTP 客户端 |
| PyMySQL | 1.1 | MySQL 数据库连接 |
| PyYAML | 6.0 | 配置解析 |
| Allure-Pytest | 2.13 | 测试报告生成 |

---

## License

MIT License - 仅供学习与测试使用
