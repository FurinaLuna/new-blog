---
alwaysApply: true
scene: git_message
---

精炼,简洁的提交信息格式 ,让人能够快速理解提交的内容,大厂程序员的提交信息格式如下:
```
<type>(<scope>): <subject>
```
- `<type>`: 提交类型, 可选值为 `feat`、`fix`、`docs`、`refactor`、`test`、`chore` 等
- `<scope>`: 受选范围, 可选值为 `components`、`utils`、`styles` 等
- `<subject>`: 提交的简短描述, 可选值为 `添加新功能`、`修复错误` 等

例如:
```
feat: 新增登录功能
```
