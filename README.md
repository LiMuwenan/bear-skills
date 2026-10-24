# Bear Skills

个人 Skill 管理库。所有 skill 以「一个根目录文件夹 = 一个 skill」的方式管理，通过 Git 与 GitHub 仓库同步。

本地启用方式：把需要的 skill 文件夹复制或链接到 Trae 的全局 skills 目录 `C:\Users\<用户名>\.trae-cn\skills\`，Agent 即可自动发现并调用。

---

## 目录结构

```
bear-skills/
├── README.md                 # 本文件
├── .gitignore                # 忽略临时文件
└── <skill-name>/             # 每个 skill 一个文件夹
    ├── SKILL.md              # 必需：入口文件
    ├── scripts/              # 可选：可执行脚本
    ├── references/           # 可选：详细文档、参考资料
    └── assets/               # 可选：模板、图片等资源
```

约定：
- 根目录只允许出现 **skill 文件夹**、`README.md`、`.gitignore` 及少量元文件，不堆放临时文件。
- 文件夹名必须与 `SKILL.md` 中的 `name` 完全一致。
- 文件夹名使用 kebab-case：全小写、数字或连字符，不用空格、下划线、大写字母，长度不超过 64 个字符。

---

## Skill 的组织方式

一个 skill 由两部分组成：

1. **YAML frontmatter**：`name` 与 `description` 决定 Agent 是否加载它。描述写清了触发场景，skill 才会在合适的时机被选中。
2. **Markdown 正文**：写「怎么做」。Agent 命中后才读取正文，正文中引用的 `references/` 文件只在需要时才展开。

因此，正文只写可复用的方法与流程，不要写某一次具体任务的内容。skill 是「操作说明书」，不是「执行记录」。

---

## 新建一个 Skill

### 第 1 步：定名字

- 用 2–3 个词概括它能做什么，例如 `pdf-extractor`、`weekly-report`、`api-review`。
- 名字要能一眼看出用途，避免 `tools`、`misc`、`helper` 这类过于宽泛的词。
- 确认根目录下没有同名文件夹。

### 第 2 步：创建文件夹

```powershell
New-Item -ItemType Directory -Path .\<skill-name>
New-Item -ItemType File -Path .\<skill-name>\SKILL.md
```

按需创建 `scripts\`、`references\`、`assets\`，不需要就不要建空目录。

### 第 3 步：编写 frontmatter

```yaml
---
name: <skill-name>
description: <一句话说明它能做什么，并写清什么时候该用它，包含用户可能提到的关键词>
---
```

`description` 是最关键的一行，写不好的话 skill 永远不会被触发。推荐句式：

> 「<能力描述>。当用户<触发场景 / 关键词>时使用。」

### 第 4 步：编写正文

按下面的模板展开，只保留对完成任务真正有用的部分：

```markdown
# <Skill 标题>

## 适用场景
- 什么时候该用
- 什么时候不该用

## 前置条件
- 依赖的工具、环境变量、输入文件

## 步骤
1. 第一步，具体到可执行的操作
2. 第二步
3. 第三步

## 示例
输入示例 + 期望输出示例

## 常见错误
- 错误做法 → 正确做法

## 参考文件
- `references/xxx.md`：需要时再读的详细资料
- `scripts/xxx.py`：可直接运行的脚本
```

写作要点：
- 用祈使句（「先读取配置文件」），不要写成散文。
- 一个 skill 只解决一类问题；内容膨胀时拆成多个 skill。
- `SKILL.md` 控制在 500 行以内，长资料、大表格、完整代码示例放到 `references/`。
- 给出正例与反例，比只讲规则更容易被正确执行。

### 第 5 步：自检并提交

```powershell
git add .\<skill-name>
git commit -m "feat(<skill-name>): 新增 <skill-name> skill"
```

提交前过一遍文末的 Checklist。

---

## Frontmatter 字段说明

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `name` | 是 | skill 标识，必须与文件夹名相同，小写连字符格式 |
| `description` | 是 | 能力描述 + 触发场景，控制在 1024 字符以内，避免换行 |
| `license` | 否 | 许可证，或指向 `LICENSE.txt` |
| `allowed-tools` | 否 | 限定该 skill 可使用的工具，非必要不加，避免误限制 |

未知字段可能被忽略，不要在 frontmatter 里堆砌自定义配置；需要配置说明时写进正文。

---

## 可选目录的用途

| 目录 | 放什么 | 何时读取 |
| --- | --- | --- |
| `scripts/` | 可直接执行的脚本（Python、PowerShell 等） | 步骤中需要时执行，避免模型重复造轮子 |
| `references/` | 详细文档、规范、长示例 | 正文明确指引时才读取 |
| `assets/` | 模板、图片、字体等静态资源 | 输出文件需要时引用 |

---

## 关联 GitHub 仓库

### 首次初始化并推送

```powershell
git init
git add .
git commit -m "chore: init skill library"
git branch -M main
git remote add origin git@github.com:<你的用户名>/bear-skills.git
git push -u origin main
```

在 GitHub 上提前创建空仓库（不要勾选初始化 README），否则首次 push 需要先处理远程已有提交。

### 在新机器上克隆

```powershell
git clone git@github.com:<你的用户名>/bear-skills.git
```

### 启用某个 skill

复制（改动需重新复制）：

```powershell
Copy-Item -Recurse .\<skill-name> "$env:USERPROFILE\.trae-cn\skills\<skill-name>"
```

或建立目录联接，源仓库改动即时生效：

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.trae-cn\skills\<skill-name>" -Target "e:\bear-skills\<skill-name>"
```

---

## 日常流程

| 场景 | 操作 |
| --- | --- |
| 新增 skill | 建文件夹 → 写 `SKILL.md` → 本地试跑 → 提交 |
| 修改 skill | 改文件 → 验证效果 → `git commit` |
| 同步到其他机器 | `git pull` |
| 废弃 skill | 删除文件夹 → 提交；若仍需追溯历史，先打 tag 再删 |

建议提交信息带上 skill 名：`feat(<skill-name>): ...` / `fix(<skill-name>): ...`，方便定位变更来源。

---

## 发布前 Checklist

- [ ] 文件夹名与 frontmatter 的 `name` 一致，且为 kebab-case
- [ ] `description` 写清了「做什么」和「什么时候用」，包含触发关键词
- [ ] 正文是可直接执行的步骤，而不是背景介绍
- [ ] 正文中引用的 `references/`、`scripts/` 文件真实存在
- [ ] 没有写入个人隐私、令牌、密钥（检查脚本与示例）
- [ ] 已在本机 skills 目录实测，能被正确触发
- [ ] 已提交并推送到 GitHub
