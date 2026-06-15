# Code Review Quality

面向代码审查与质量保障的 skill，用于审查代码变更、PR、diff、重构和生成代码，重点关注正确性、契约兼容、安全性、数据状态、并发时序、可维护性、性能、测试覆盖和可观测性。

## 当前内容

- `skills/code-review-quality/SKILL.md`
  - 主工作流与输出要求
- `skills/code-review-quality/references/review-checklist.md`
  - 风险导向审查清单
- `skills/code-review-quality/references/output-format.md`
  - 推荐反馈模板与排序方式
- `skills/code-review-quality/evals/evals.json`
  - 输出质量评测提示词与 expectations，用于验证审查结果是否高信号、可定位、可执行
- `skills/code-review-quality/evals/trigger-evals.json`
  - 触发评测集合，用于区分应该进入代码审查模式和不应该进入代码审查模式的相邻场景

## 使用方式

- 需要做代码审查时，先看 `skills/code-review-quality/SKILL.md`
- 变更较复杂或涉及接口、权限、数据、并发时，再看 `references/review-checklist.md`
- 需要统一审查输出风格时，按 `references/output-format.md` 组织结果
- 需要迭代优化输出质量时，基于 `evals/evals.json` 跑 with-skill 和 baseline 对比
- 需要优化触发准确性时，基于 `evals/trigger-evals.json` 做 should-trigger / should-not-trigger 检查
