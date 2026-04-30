# Experience Memory

Experience Memory 是一个面向 AI 编码代理和工程团队的双层记忆方案，用来把一次会话里的临时经验沉淀为可检索、可复用、可晋升的工程记忆。

它同时提供两部分能力：

- `SKILL.md`：约束代理在实现、排错、重构、补测试前，先检索记忆，再决定如何写入或晋升。
- `"scripts\\memory_cli.py"`：用于初始化、检索、记录、晋升和生成文档模板的命令行工具。

这个仓库适合解决两个常见问题：

- 同一类坑在同一个项目里反复踩。
- 某些工程经验明明可以跨项目复用，却总是散落在聊天记录或个人脑海里。

## 功能概览

当前版本支持以下核心功能：

- 初始化项目级和全局级记忆目录。
- 在项目记忆、全局记忆或两者之间检索经验。
- 记录结构化 learning 条目到 `JSONL`。
- 将项目内已验证的经验晋升到全局记忆。
- 为高价值问题生成 `solution` 复盘文档模板。
- 为关键架构/接口决策生成 `decision` 文档模板。
- 自动维护项目注册表、项目 catalog 和最近操作状态。

支持的 learning 类型只有 4 类：

- `error_fix`
- `best_practice`
- `project_preference`
- `decision`

支持的文档类型只有 2 类：

- `solution`
- `decision`

## 工作原理

### 1. 双层记忆模型

Experience Memory 把记忆分成两层：

- 项目内记忆：`"<project-root>\\docs\\experience-memory\\"`
- 用户全局记忆：`"%USERPROFILE%\\.experience-memory\\"`

设计原则很简单：

- 项目内只存当前仓库自己的事实、偏好和决策。
- 全局层只保留跨项目依然成立的稳定经验。
- 如果项目内和全局层冲突，项目内优先。

### 2. 路径解析

CLI 会按下面的顺序决定 `project_root`：

1. 显式传入的 `--project-root`
2. 从当前目录向上查找到的最近 `.git` 根目录
3. 当前工作目录

这意味着脚本既可以在仓库根目录使用，也可以在子目录使用。

### 3. 存储结构

初始化后会创建下面这套结构：

```text
<project-root>\
  docs\experience-memory\
    learnings.jsonl
    profile.json
    state.json
    solutions\
    decisions\

%USERPROFILE%\
  .experience-memory\
    registry\
      projects.json
    shared\
      learnings.jsonl
      solutions\
      decisions\
    projects\
      <project-slug>\
        catalog.json
```

其中：

- `learnings.jsonl` 存放原子经验，一行一个 JSON 对象。
- `solutions\\` 存放高价值问题复盘。
- `decisions\\` 存放关键决策记录。
- `profile.json` 记录项目与记忆目录元信息。
- `state.json` 记录最近检索、写入、晋升时间。
- `projects.json` 记录全局已注册项目。
- `catalog.json` 记录单个项目在全局层的索引和计数。

### 4. 检索机制

建议的检索顺序是：

1. 项目内 `learnings.jsonl`
2. 项目内 `solutions\\` / `decisions\\`
3. 全局 `shared\\learnings.jsonl`
4. 全局 `shared\\solutions\\` / `shared\\decisions\\`

当前 CLI 的 `search` 子命令主要负责在 `JSONL learning` 中做排序和召回，排序分数来自这些字段命中：

- 标题：权重最高
- 规则：较高权重
- 摘要
- 标签
- 文件路径
- 类型
- `confidence`
- 项目级条目额外加权

换句话说，越像“当前项目里、最近验证过、标题/规则命中更强”的经验，越容易排到前面。

### 5. 写入与晋升机制

写入新经验时，CLI 会：

- 自动初始化缺失目录。
- 根据标题生成形如 `YYYY-MM-DD-<slug>` 的 `id`。
- 将条目写入项目级或全局级 `learnings.jsonl`。
- 自动刷新项目 catalog 和最近写入时间。

晋升时，CLI 会：

- 从项目级 `learnings.jsonl` 找到指定 `id`。
- 复制条目到全局 `shared\\learnings.jsonl`。
- 自动补充 `promoted_at`、`promoted_from` 等字段。
- 保证全局 `id` 唯一。

### 6. 文档模板机制

对于“原子经验不足以表达上下文”的情况，CLI 允许生成文档模板：

- `solution`：适合问题复盘，关注问题、症状、根因、处理过程、最终修复和验证。
- `decision`：适合记录架构/接口/边界决策，关注背景、决策、备选方案和影响。

模板来自 `"assets\\solution-template.md"` 和 `"assets\\decision-template.md"`。

## 触发时机

### 什么时候先检索

在下面这些动作开始前，应先查项目记忆，再查全局记忆：

- 开始实现新功能
- 排查 bug
- 重构
- 补测试
- 调整目录、接口、边界或工程约束

### 什么时候新增 learning

满足下面任一条件，就应该考虑新增一条 learning：

- 刚修复了一个明确错误，并且已经知道根因和修复规则。
- 某个做法在项目里已经重复出现，不希望继续试错。
- 用户明确给出了项目偏好、禁忌或约束。
- 刚做出了以后会影响他人协作方式的关键决策。

### 什么时候生成长文档

满足下面任一条件，应该用 `new-doc` 补一份文档：

- 一条 learning 不足以解释背景。
- 修复步骤已经明显超过两步。
- 存在多个被否决的备选方案。
- 这是一个之后很可能被重新讨论的决策。

### 什么时候晋升到全局

只有在经验满足这两个条件时，才应该晋升到全局：

- 已经在当前项目内被验证。
- 不依赖当前仓库的私有实现细节，跨项目仍然成立。

### 什么时候不要写入

下面这些内容不应写入 experience memory：

- 一次性的 typo 修复
- 没有验证过的猜测
- 纯偶发、不可复用的问题
- 与当前项目无关的聊天内容

## 安装

### 前置条件

- Python 3.10 或更高版本
- 一个本地仓库目录

当前脚本只依赖 Python 标准库，不需要额外安装第三方包。

### 安装方式一：作为本地 CLI 使用

1. 将仓库放到本地任意目录。
2. 进入仓库根目录。
3. 初始化记忆目录。

示例：

```powershell
Set-Location "E:\MyGitProject\AICode\experience-memory"
python ".\scripts\memory_cli.py" init --project-root "."
```

### 安装方式二：作为代理技能使用

如果你的代理系统支持“技能”或“工具说明”目录，可以直接复用本仓库：

- `SKILL.md` 提供代理行为规则。
- `"scripts\\memory_cli.py"` 提供实际操作命令。
- `"references\\"` 提供检索、裁剪和 schema 说明。
- `"assets\\"` 提供可落地模板。
- `"agents\\openai.yaml"` 提供适用于代理注册的元信息。

其中 `"agents\\openai.yaml"` 已声明：

- 名称：`Experience Memory`
- 描述：`Capture and reuse project and global engineering memory`
- `allow_implicit_invocation: true`

也就是说，在支持该元信息的代理系统里，可以把它作为一个可隐式触发的技能来接入。

## 使用方法

### 查看路径

```powershell
python ".\scripts\memory_cli.py" paths --project-root "."
```

用途：

- 确认当前项目根目录
- 确认项目 slug
- 确认项目级与全局级记忆路径

### 初始化记忆目录

```powershell
python ".\scripts\memory_cli.py" init --project-root "."
```

执行后会同时准备：

- 当前项目的 `"docs\experience-memory"`
- 当前用户的全局 `".experience-memory"`

### 检索记忆

```powershell
python ".\scripts\memory_cli.py" search "pytest env app init" --project-root "." --scope both --limit 5
```

常用参数：

- `--scope "project"`：只搜项目内
- `--scope "global"`：只搜全局
- `--scope "both"`：两层一起搜，默认值
- `--kind "<kind>"`：按 `error_fix` / `best_practice` / `project_preference` / `decision` 过滤
- `--limit "5"`：限制输出条数

### 记录一条 learning

```powershell
python ".\scripts\memory_cli.py" add `
  --project-root "." `
  --kind "error_fix" `
  --title "测试环境变量必须先于 app 初始化" `
  --summary "否则会加载错误配置并导致测试误连开发环境" `
  --rule "创建 app 前先设置测试环境变量" `
  --tag "pytest" `
  --tag "config" `
  --tag "app-init" `
  --file "src/app/main.py" `
  --file "tests/conftest.py"
```

默认行为：

- `--scope` 默认为 `project`
- `--confidence` 默认为 `0.8`
- `--source` 默认为 `observed`
- `--status` 默认为 `active`

### 生成复盘或决策文档

生成问题复盘模板：

```powershell
python ".\scripts\memory_cli.py" new-doc --project-root "." --doc-kind "solution" --title "修复测试配置提前加载问题"
```

生成决策记录模板：

```powershell
python ".\scripts\memory_cli.py" new-doc --project-root "." --doc-kind "decision" --title "统一采用项目内优先的记忆读取策略"
```

### 晋升到全局记忆

```powershell
python ".\scripts\memory_cli.py" promote --project-root "." --id "2026-04-01-test-env-before-app-init"
```

这一步应该谨慎使用，因为它会把项目经验提升为跨项目共享经验。

## 推荐工作流

建议把 Experience Memory 当成一个固定流程，而不是一次性工具：

1. 新任务开始前先 `search`
2. 确认存在可复用经验后按经验执行
3. 出现新经验时用 `add` 沉淀
4. 需要上下文时用 `new-doc`
5. 经验跨项目成立后再 `promote`
6. 定期清理重复、过期、冲突条目

## 数据约束

为了保证记忆质量，建议始终遵守下面这些约束：

- 项目内优先，全局次之
- 未验证内容不要写入
- 一次性问题不要写入
- 删除不是默认动作，优先标记 `active` / `stale` / `superseded`
- 只有跨项目仍然成立的经验才能晋升全局

## 仓库结构

```text
.
├─ "agents/"
│  └─ "openai.yaml"
├─ "assets/"
│  ├─ "decision-template.md"
│  ├─ "learning-template.json"
│  └─ "solution-template.md"
├─ "references/"
│  ├─ "pruning-rules.md"
│  ├─ "retrieval-workflow.md"
│  └─ "schema.yaml"
├─ "scripts/"
│  └─ "memory_cli.py"
└─ "SKILL.md"
```

## 适用场景

这个仓库尤其适合下面几类团队或项目：

- 让 AI 代理先“读项目经验”再动手写代码
- 将工程经验从聊天记录迁移到结构化存储
- 避免多仓库之间重复踩坑
- 为高价值问题和关键决策留下长期可追溯记录

如果你想要的不是“知识库”，而是“带项目上下文优先级、可逐步晋升到全局的工程记忆层”，这个仓库就是为这个目标设计的。

## 编码兼容

- CLI 启动时会主动将 `stdout` 和 `stderr` 重设为 `UTF-8`，减少 Windows PowerShell 下中文输出乱码。
- `learnings.jsonl` 读取采用逐行解码，按 `utf-8-sig`、`utf-8`、`gb18030` 顺序兼容历史混合编码记录。
- 如果从旧环境导入过记忆文件，建议在确认内容无误后将整份 `JSONL` 标准化回 `UTF-8`，避免其他只支持单一编码的工具再次失败。

## AGENTS.md
请在AGENTS.md中加入以下内容：
```
## Experience Memory
- 开始实现、排错、重构、补测试前，先检索 experience memory：先项目内，后全局
- 项目记忆目录为 `"<project-root>\\docs\\experience-memory\\"`，全局记忆目录为 `"%USERPROFILE%\\.experience-memory\\"`
- 未验证、一次性、纯偶发、与当前项目无关的内容不得写入
- 仅将跨项目仍成立的经验晋升到全局；冲突时项目内优先
```
