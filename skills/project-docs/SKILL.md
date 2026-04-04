---
name: project-docs
description: Use when creating or updating lightweight project documentation in a repository, especially README, project overviews, architecture docs, business rules, coding guidelines, ADRs, module READMEs, how-to guides, or docs added after code changes in an existing codebase.
---

# 项目文档维护

## 核心原则

- 文档要短、准、可维护，优先帮助人和 AI 快速做事。
- 先复用现有文档，再新增；先更新最相关文档，再扩展到新文档。
- 只写会稳定影响后续开发、验收和协作的内容。
- 如果仓库里已有 `PRD.md` 或同类需求文件，先以它判断文档范围和优先级。

## 标准结构

```text
项目根目录/
├── README.md
└── docs/
    └── project-docs/
        ├── project-overview.md
        ├── architecture.md
        ├── business-rules.md
        ├── coding-guidelines.md
        ├── adr/
        ├── modules/<module>/README.md
        ├── how-to/
        └── assets/
```

- `README.md`: 项目入口、最短上手路径、指向其他文档的导航。
- `docs/project-docs/project-overview.md`: 项目背景、目标、技术栈、启动方式、目录说明。
- `docs/project-docs/architecture.md`: 系统分层、模块划分、依赖关系、边界与约束。
- `docs/project-docs/business-rules.md`: 核心业务对象、流程、状态机、规则、例外。
- `docs/project-docs/coding-guidelines.md`: 命名、分层、错误处理、日志、禁止事项。
- `docs/project-docs/adr/`: 设计决策记录，只写“为什么这么定”。
- `docs/project-docs/modules/<module>/README.md`: 核心模块说明，按模块复杂度按需创建。
- `docs/project-docs/how-to/`: 常见任务、操作指南、重复性流程。
- `docs/project-docs/assets/`: 图表、截图、流程图等附件。

## 选文档

- 先判断任务类型，再选最小文档集。
- 项目总览类内容写到 `README.md` 和 `docs/project-docs/project-overview.md`。
- 架构边界、模块关系、依赖约束写到 `docs/project-docs/architecture.md`。
- 业务对象、流程、状态、规则、例外写到 `docs/project-docs/business-rules.md`。
- 命名、分层、错误处理、日志、禁止事项写到 `docs/project-docs/coding-guidelines.md`。
- 关键决策及其原因写到 `docs/project-docs/adr/`。
- 单个模块的职责、对外能力、依赖、坑位写到模块级 `README.md`。
- 可重复执行的操作写到 `docs/project-docs/how-to/`。
- 图表和截图单独放到 `docs/project-docs/assets/`，正文只保留必要链接。

## 写什么

- 写目的、边界、职责、规则、例外、例子、相关链接。
- 写“为什么”以及“哪些地方不能改”，不要只写当前代码长什么样。
- 写能帮助后续改代码、做验收、排查问题的内容。
- 新增文档时，优先保持结构统一，方便 AI 快速检索和复用。

## 不写什么

- 不写大而空的口号、营销话术、纯概念堆砌。
- 不写重复代码里已经很清楚的实现细节。
- 不写过期内容、历史脉络流水账、无人维护的长文档。
- 不写只有背景、没有边界和例外的说明。
- 不为了补齐目录而补齐目录，只有确实有用时才创建新文档。

## 已有项目补文档

1. 先扫描现有文档，找出已经存在的角色和缺口。
2. 把现有文档映射到标准结构，不要先重命名、先复制、再重构。
3. 优先补最小必需集：入口、总览、架构、业务规则、规范。
4. 只有当前没有合适承载位置时，才新增文档。
5. 如果已有文档可以更新，就直接更新它，不要再造一份同类文档。

## 验收后同步文档

- 代码验收完成后，检查这次变更是否影响行为、接口、边界、依赖、决策、模块职责。
- 只要有影响，就在同一轮里更新或新增对应文档。
- 如果新增文档，顺手补 README 或导航链接，避免文档孤岛。
- 如果变更只影响局部，优先更新最近、最相关的文档。
- 如果文档和代码出现分歧，以代码验收结果为准，立刻修正文档。

## 默认模板

- `README.md`: 项目是什么、怎么启动、去哪里找文档。
- `docs/project-docs/project-overview.md`: 背景、目标、技术栈、目录、入口。
- `docs/project-docs/architecture.md`: 分层、边界、依赖、约束。
- `docs/project-docs/business-rules.md`: 对象、流程、状态、规则、例外。
- `docs/project-docs/coding-guidelines.md`: 团队约定、禁止事项、统一写法。
- `docs/project-docs/adr/`: 问题、备选方案、决策、后果。
- `docs/project-docs/modules/<module>/README.md`: 职责、依赖、边界、坑位。
- `docs/project-docs/how-to/`: 目标、前置条件、步骤、验证方法。

## 保持轻量

- 一页能讲清楚的，不要写成十页。
- 文档粒度按“主题 / 模块”切，不按“时间 / 人名”切。
- 只维护关键文档，其他内容宁可链接到代码或更小的文档。
