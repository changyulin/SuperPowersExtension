---
name: experience-memory
description: Use when starting implementation, debugging, refactoring, or test
  work that may depend on prior project experience; when the user asks to
  remember, record, 沉淀, 检索, 晋升, promote, prune, or clean engineering
  experience; or when a repeated bug, project preference, architectural
  decision, or reusable lesson should be checked or stored.
---

# Experience Memory

## 概述

这个 skill 用来把一次会话里临时出现的经验，沉淀为后续可检索、
可复用、可晋升的工程记忆。

它采用双层存储：

- 项目内记忆：`<project-root>\docs\experience-memory\`
- 用户全局记忆：`%USERPROFILE%\.experience-memory\`

项目内只记录这个仓库自己的事实、偏好和决策。全局只保留跨项目仍然
成立的稳定经验，避免项目噪音污染其他仓库。

## 何时使用

在下面这些情况触发：

- 开始实现、排错、重构、补测试或调整工程约束前，可能需要先查旧经验
- 解决了一个之前踩过或以后大概率还会踩的错误
- 发现了一个稳定最佳实践，不再希望重复试错
- 用户明确表达了项目偏好、禁忌或约束
- 做出了架构、接口、目录、边界上的关键决策
- 开始新任务前，希望先检索这个项目以前的经验
- 完成任务后，希望把新经验追加到本地或晋升到全局
- 需要清理过期、重复、冲突的经验记录

## 快速判定

| 场景 | 动作 | 停止条件 |
|---|---|---|
| 新任务可能受历史经验影响 | 先 `search`，项目内优先，全局次之 | 命中后先核对当前文件和代码仍然一致 |
| 修复了明确且可复用的问题 | 用 `add` 写入项目内 `learnings.jsonl` | 没有根因或验证证据时不要写入 |
| 一条 learning 不足以解释背景 | 用 `new-doc` 生成 `solution` 或 `decision` 模板 | 只生成模板后必须补真实内容 |
| 经验看起来可跨项目复用 | 先检查是否依赖当前仓库私有细节，再考虑 `promote` | 证据不足或语义依赖本仓库时停在项目内 |
| 记忆库有噪音 | 先列候选并标记状态 | 删除或批量改状态前必须获得用户确认 |

不要记录下面这些内容：

- 一次性 typo 修复
- 与当前项目无关的临时聊天内容
- 没有验证过、只是猜测的“经验”
- 纯粹来自外部服务波动、不可复用的偶发问题

## 反例与红线

| 不要做 | 触发例子 | 替代动作 |
|---|---|---|
| 不要把所有代码任务都自动升级为记忆检索 | 用户要求“直接看代码定位”“只润色 README”“给函数加类型注解” | 按用户请求处理；只有出现历史经验、项目偏好、重复问题或明确记忆需求时再检索 |
| 不要把未验证判断写成 learning | 只是怀疑某配置有问题，还没有根因、修复和验证输出 | 继续排查；任务结束后满足写入条件再 `add` |
| 不要把项目私有经验直接晋升全局 | 规则依赖当前仓库目录、业务 SQL、内部接口或私有数据口径 | 先保留项目内；确认跨项目仍成立并获得用户确认后再 `promote` |
| 不要把旧记忆当成当前事实 | 命中记录引用的文件已经改名、删除或行为漂移 | 先核对当前文件、测试和代码；不一致时标记为清理候选 |
| 不要整库倾倒或泄露敏感信息 | 用户只问一个 bug，却输出大量无关记忆或包含密钥、客户数据 | 只展示前 3 到 5 条相关摘要；敏感内容先脱敏或不写入 |
| 不要默认删除、批量标记或合并记忆 | 发现重复、过期、冲突条目 | 先列候选、原因和影响范围；等用户明确确认后再执行 |

## 存储布局

### 项目内

项目根目录下的 `docs\experience-memory\` 是项目事实源：

- `learnings.jsonl`
  - 原子经验库
- `solutions\`
  - 高价值问题复盘
- `decisions\`
  - 架构与接口决策记录
- `profile.json`
  - 项目记忆元数据
- `state.json`
  - 最近检索、写入、晋升状态

### 全局

用户目录下的 `%USERPROFILE%\.experience-memory\` 是全局共享层：

- `registry\projects.json`
  - 已注册项目索引
- `shared\learnings.jsonl`
  - 已晋升的通用原子经验
- `shared\solutions\`
  - 已晋升的通用复盘
- `shared\decisions\`
  - 已晋升的通用决策
- `projects\<project-slug>\catalog.json`
  - 单项目的全局索引与统计

字段细节见 `references/schema.yaml`。

## 经验类型

原子经验统一写入 `learnings.jsonl`，首版只允许四类：

- `error_fix`
  - 错误与修复经验
- `best_practice`
  - 稳定最佳实践
- `project_preference`
  - 项目偏好与约束
- `decision`
  - 架构、接口、边界决策

高价值内容再升级成文档：

- `solutions\`
  - 适合“问题 -> 根因 -> 修复 -> 防复发”
- `decisions\`
  - 适合“背景 -> 决策 -> 备选方案 -> 影响”

## 工作流

### 1. 初始化

先为当前项目创建本地记忆目录，并确保全局目录存在：

```powershell
python ".\scripts\memory_cli.py" init --project-root "<project-root>"
```

如果不传 `--project-root`，脚本会尝试从当前目录向上查找项目根。

### 2. 开始工作前先检索

先搜项目内，再搜全局：

```powershell
python ".\scripts\memory_cli.py" search "pytest env app init" `
  --project-root "<project-root>" --scope both --limit 5
```

检索规则见 `references/retrieval-workflow.md`。

如果没有命中，继续按真实代码和当前需求工作；不要为了填充记忆而制造经验。
如果命中条目提到的文件已经不存在，把该命中视为可疑，并把它加入后续清理候选。

### 3. 发生新经验时记录

把经验先写到项目内：

```powershell
python ".\scripts\memory_cli.py" add `
  --kind "error_fix" `
  --title "测试环境变量必须先于 app 初始化" `
  --summary "否则会加载错误配置并导致测试误连开发环境" `
  --rule "创建 app 前先设置测试环境变量" `
  --tag "pytest" --tag "config" --tag "app-init" `
  --file "src/app/main.py" --file "tests/conftest.py" `
  --project-root "<project-root>"
```

写入前确认三件事：

1. 已经知道根因、稳定规则或明确用户偏好。
2. 这不是一次性、偶发或未验证猜测。
3. `title` 和 `rule` 能让下次检索者直接理解怎么行动。

### 4. 高价值案例升级成文档

如果这次经验值得长文复盘，生成模板再补内容：

```powershell
python ".\scripts\memory_cli.py" new-doc `
  --doc-kind "solution" `
  --title "修复测试配置提前加载问题" `
  --project-root "<project-root>"
```

### 5. 跨项目有效时晋升到全局

只有在经验不依赖当前仓库细节时，才晋升到全局：

```powershell
python ".\scripts\memory_cli.py" promote `
  --id "<learning-id>" `
  --project-root "<project-root>"
```

CHECKPOINT / STOP：晋升会影响其他项目。执行前必须确认：

- 该经验已经在项目内记录并验证。
- 规则不依赖当前仓库的私有目录、接口、数据或业务口径。
- 用户没有要求只保留为项目内经验。

### 6. 定期清理

清理不是默认删除，而是先识别：

- 重复记录
- 互相冲突的规则
- 已失效的文件路径
- 已被更新决策替代的旧条目

清理规则见 `references/pruning-rules.md`。

CHECKPOINT / STOP：清理默认不删除。删除、批量标记或合并前，先列出候选、原因和影响范围，等用户明确确认。

## 失败分支

| 触发条件 | 一线处理 | 仍失败时 |
|---|---|---|
| `search` 没有命中 | 继续真实代码分析，不编造记忆 | 任务结束后若产生新经验，再考虑 `add` |
| 命中条目的文件路径不存在 | 把命中降级为可疑 | 加入清理候选，不直接采用 |
| 项目内和全局经验冲突 | 项目内优先，再看更新时间和置信度 | 仍无法判断时向用户说明冲突并暂停采用 |
| `memory_cli.py` 路径找不到 | 先定位 skill 根目录或使用绝对路径 | 不要改写记忆目录结构来适配错误路径 |
| 写入或初始化遇到权限错误 | 报告目标路径和失败命令 | 不要改到别的仓库或全局目录绕过权限 |
| `learnings.jsonl` 解析失败 | 停止写入，保留原文件 | 先备份并人工检查坏行，再恢复操作 |
| 用户要求删除记忆 | 先确认条目重复、无效或错误 | 未确认前只允许标记候选或建议合并 |

## 路径解析原则

始终遵守下面的路径优先级：

1. 命令显式传入的 `--project-root`
2. 当前工作目录向上查找的项目根
3. 当前工作目录

全局目录固定为：

- `%USERPROFILE%\.experience-memory\`

不要把全局经验库放到某个仓库内，也不要把项目内经验直接混入全局
共享层。

## 检索优先级

每次读取记忆时遵循这个顺序：

1. 项目内 `learnings.jsonl`
2. 项目内 `solutions\` / `decisions\`
3. 全局 `shared\learnings.jsonl`
4. 全局 `shared\solutions\` / `shared\decisions\`

如果项目内和全局存在冲突：

- 项目内优先
- 新于旧优先
- 高置信度优先

## 资源

- `references/schema.yaml`
  - 目录结构、字段和文档 schema
- `references/retrieval-workflow.md`
  - 检索、排序、命中后的使用策略
- `references/pruning-rules.md`
  - 去重、过期、冲突处理策略
- `assets/learning-template.json`
  - 原子经验示例
- `assets/solution-template.md`
  - 问题复盘模板
- `assets/decision-template.md`
  - 决策记录模板
- `scripts/memory_cli.py`
  - 初始化、记录、检索、晋升、生成文档的命令行工具
