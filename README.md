# RuoYi-Vue-Pro 企业管理平台测试 · ruoyi-test

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Pytest-8.3-green.svg)](https://pytest.org/)
[![PyMySQL](https://img.shields.io/badge/PyMySQL-1.1-red.svg)](https://pymysql.org/)
[![Allure](https://img.shields.io/badge/Allure-Report-orange.svg)](https://allurtest.info/)

| 角色 | 覆盖范围 | 被测开源项目 |
|------|----------|--------------|
| 测试工程师 | PC 端后台、**工作流审批专项**、**权限安全专项** | [YunaiV/ruoyi-vue-pro](https://github.com/YunaiV/ruoyi-vue-pro)（⭐ 30k+） |

**本测试仓库：** [yedda2026/RuoYi-test](https://github.com/yedda2026/RuoYi-test)（GitHub 可能将 URL 规范为同名大小写形式）

---

## 业务背景

[RuoYi-Vue-Pro](https://github.com/YunaiV/ruoyi-vue-pro) 基于 **Spring Boot + MyBatis Plus + Vue & Element**，具备 **RBAC 动态权限**、**Flowable 工作流**、SaaS 多租户、用户/角色/部门/岗位、系统监控与审计日志等能力。本项目测试聚焦 **PC 后台**：RBAC 与**数据权限隔离**、**多租户边界**、工作流多分支与审批完整性；引入 **MySQL 库表校验**，核对接口结果与 SQL、数据权限 WHERE 是否生效。小程序、CRM/ERP、AI/IoT、支付/短信等未纳入本轮专项。

---

## 岗位职责

- **工作流模块**：XMind 梳理请假、报销、合同、入职/离职、采购等 **6 类**审批；覆盖串行/并行、会签、驳回/退回、发起人撤回、超时自动审批等节点；复杂分支用**判定表**设计用例；Excel 管理用例，禅道跟踪缺陷。
- **RBAC 与安全**：菜单/按钮/API 权限正确性；**水平越权**（跨用户/跨租户资源）、**垂直越权**（低权角色调高权接口）；数据权限（仅本部门 / 全部 / 自定义）过滤是否生效。
- **数据库验证**：MySQL 直连比对接口返回与 SQL 结果；检查数据权限 SQL 是否拼接正确 WHERE；工作流状态变更后字段是否落库一致。
- **接口测试（Postman）**：无 Token / Token 过期 / Token 篡改 → **401**；低权调高权接口 → **403**；跨租户访问应被拦截；工作流发起/通过/驳回等正向链路。
- **接口自动化（Pytest + Requests）**：核心工作流与权限类接口脚本化；参数化与数据驱动；多角色登录 Fixture（如管理员、普通员工、跨部门用户）支撑越权场景；Allure 分模块报告。
- **性能测试（JMeter）**：高频接口如登录、待办列表、报表加载；峰值阶梯加压（如 20/50/80 并发）；聚合报告分析 TPS 与响应时间，定位瓶颈。

---

## 工作成果（项目指标）

| 维度 | 说明 |
|------|------|
| **功能测试** | **320+** 条功能用例（Excel）；覆盖工作流审批、RBAC、用户/角色/部门、系统监控、日志审计等 **6** 大模块；有效缺陷 **26** 个，其中 **8** 个 P0/P1。 |
| **工作流专项** | 发现并行审批节点双用户同时操作导致前后端不一致、重新提交后历史附件缺失、超时自动审批逻辑异常等问题。 |
| **权限安全专项** | **5** 处未授权访问类问题（水平 3：Token 有效但资源归属未校验；垂直 2：接口缺权限注解）；**2** 处过期 Token 误返回 **500** 而非 **401**。 |
| **数据库验证** | 发现「仅本部门」数据权限下接口仍返回跨部门数据（SQL 未拼数据权限 WHERE）；**1** 处跨租户隔离类问题。 |
| **接口自动化** | 工作流与鉴权相关核心接口自动化覆盖 **55+**（与 Postman/手工形成互补）。 |
| **性能** | 报表类接口在约 **80** 并发下 P95≈**5s**，根因为 **N+1 查询**（约 100 个部门节点触发 101 次 SQL）；协助改为 JOIN 后 P95≈**750ms**（约 **85%** 提升）。 |

---

## 技术栈与工具

Postman · Pytest · Requests · JMeter · MySQL · Allure · XMind · 禅道

---

## 本仓库代码说明

- 简历中的 **320+ 功能用例、55+ 自动化接口、JMeter 场景、多角色 Postman 集合** 等为**全项目测试实践**，部分资产在 Excel / Postman / 独立脚本或内网环境。
- **本仓库**开源 **Pytest + Requests + PyMySQL + Allure** 框架，并落地 **数据库验证类用例**（数据权限、审批后状态、流程发起记录等）及连接性检查，作为与简历中「库表校验、权限专项」对齐的**可运行示例**，可按 **55+ 接口**目标继续扩展 `test_cases/` 与配置。

### 当前自动化用例一览

| 类型 | 用例数 | 说明 |
|------|--------|------|
| 数据权限 / 工作流库表 | 3 + 辅助 | 部门数据权限、审批后 `wf_task` 状态、发起后 `wf_process_instance` 记录等（见 `test_data_permission.py`） |

表名、接口路径需与本地部署的 RuoYi/Flowable 版本一致，可在 YAML 或代码中调整。

---

## 被测系统

| 项目 | 说明 | 开源地址 |
|------|------|----------|
| RuoYi-Vue-Pro | Spring Boot 多模块、数据权限、Flowable 工作流等 | https://github.com/YunaiV/ruoyi-vue-pro |

---

## 测试用例概览（本仓库）

```
ruoyi-test
├── test_cases/
│   ├── conftest.py              # login_token、db_helper（session）
│   └── db_verify/
│       └── test_data_permission.py
├── utils/
│   ├── db_util.py
│   ├── request_util.py
│   └── ...
└── config/config.yaml           # API + database
```

### 数据库验证用例摘要

| ID | 名称 | 要点 |
|----|------|------|
| D1 | 仅本部门数据权限 | 用户列表 API + `sys_user` 交叉校验 |
| D2 | 审批通过状态更新 | 审批 API + `wf_task.status` |
| D3 | 流程发起记录 | 发起 API + `wf_process_instance` 计数与字段 |

---

## 快速开始

```bash
cd ruoyi-test
pip install -r requirements.txt
```

编辑 `config/config.yaml`：`base_url`、登录账号、**database** 四项。

```bash
pytest test_cases/ -v
pytest test_cases/ -v -m db_verify
pytest test_cases/ -v --alluredir=reports/allure-results
allure serve reports/allure-results
```

---


