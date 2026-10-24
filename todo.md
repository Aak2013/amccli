做 CLI 是对的选择：单用户、本地、离线、可脚本化，比 Web 少一半工作量。但 CLI 有一个硬约束要先接受：**终端里渲染复杂数学公式很痛苦**。MVP 策略是：**显示原始 LaTeX，提供 `--plain` 做简单可读化，不追求终端 KaTeX。**

下面给你一份 CLI 版 Todo List。

---

## 0. 先定 CLI 形态（防止做成四不像）

- [ ] 确定形态：**子命令式 CLI + 交互式做题**，不做 TUI 全屏应用
- [ ] 确定用户模型：**单用户本地**，不做登录，配置存 `~/.amc-cli/config.toml`
- [ ] 确定数据存储：**SQLite**，默认 `~/.amc-cli/amc.db`
- [ ] 确定公式策略：默认输出 LaTeX 原文；`--plain` 做简单替换；不内嵌渲染器
- [ ] 确定 MVP 命令集：`init`、`import`、`list`、`show`、`practice`、`review`、`stats`、`recommend`
- [ ] 明确暂不做：多用户、云同步、终端图形公式、复杂推荐模型
- [ ] 写下验收：`amc practice --count 10` 能完整跑完并写入记录；`amc recommend` 能给出理由

**验收：** 一页 `CLI_SPEC.md`：命令表、输入输出、不做什么。

---

## 1. 项目骨架与命令框架

- [ ] 建项目：`amc-cli/`
- [ ] 用 `pyproject.toml` 管理，entry point：`amc = amc_cli.main:app`
- [ ] 选型：**Typer + Rich + sqlite3**（MVP 不用 SQLAlchemy）
- [ ] 目录：
  ```text
  amc-cli/
    pyproject.toml
    src/amc_cli/
      main.py
      config.py
      db.py
      schema.sql
      importers.py
      render.py
      mastery.py
      commands/
        init.py
        import_.py
        list_.py
        show.py
        practice.py
        review.py
        stats.py
        recommend.py
    tests/
    data/
  ```
- [ ] `amc --help`、`amc --version` 可用
- [ ] 全局选项：`--db PATH`、`--plain`、`--no-color`

**验收：** `pip install -e .` 后 `amc --help` 列出所有子命令。

---

## 2. 数据库与导入

- [ ] 建表：`questions`、`tags`、`question_tags`、`attempts`、`mastery`、`meta`
- [ ] `questions` 字段：id、contest、year、paper、problem_no、stem、options_json、answer、solution、difficulty、source、has_solution
- [ ] `attempts` 字段：id、question_id、user_choice、is_correct、elapsed_sec、created_at、mode（practice/review/diagnostic）
- [ ] `mastery` 字段：tag_id、score、attempts、correct、updated_at
- [ ] 写 `amc init`：建库、建表、写入版本号
- [ ] 写 `amc import questions.jsonl`：支持 `--dry-run`、`--dedupe`、`--limit`
- [ ] 导入时解析年份/竞赛/题号/选项/答案，失败条目写入 `import_failed.jsonl`
- [ ] 导入后打印统计：总数、有答案数、有解答数、按竞赛分布

**验收：** `amc init && amc import data/questions_v1.jsonl` 后，`amc list` 能查到数据。

---

## 3. 查询与展示

- [ ] `amc list`：支持 `--contest`、`--year`、`--tag`、`--difficulty`、`--has-answer`、`--limit`
- [ ] `amc list` 输出 Rich 表格：id、竞赛、年份、题号、主标签、难度、是否有答案
- [ ] `amc show <id>`：题干、选项、答案（`--with-answer` 才显示）、解答（`--with-solution`）
- [ ] `amc show <id> --plain`：简单替换 `$...$` 为原文，提示“复杂公式请复制到外部渲染”
- [ ] `amc tags`：列出标签树和每题数量
- [ ] 所有列表输出支持 `--json`，方便脚本化

**验收：** 能按“2023 AMC 12A”“几何”“难度 3”组合筛选并正确显示。

---

## 4. 交互式做题（核心）

- [ ] `amc practice --count 10 [--tag X] [--contest AMC12] [--difficulty 1-5]`
- [ ] 选题规则：按条件随机，排除最近已做题（可 `--include-done`）
- [ ] 每题展示：进度 `3/10`、id、竞赛年份题号、题干、选项 A–E
- [ ] 输入容错：`a/A/1` 都算 A；`s` 跳过；`q` 退出并保存已做记录；`?` 显示提示（可选）
- [ ] 提交后：立即判分（有答案）或提示“无标准答案，自评”（无答案）
- [ ] 显示正确答案和解答，按 `Enter` 继续
- [ ] 记录 attempt：选择、对错、用时、mode=practice
- [ ] Ctrl+C 中断时保存当前进度，不丢记录
- [ ] 结束打印本轮汇总：正确率、用时、错题 id 列表

**验收：** 连续做 10 题不崩溃；中断后 `amc stats` 能看到已做题；错题进入错题本。

---

## 5. 错题本与复习

- [ ] `amc review`：列出待复习错题，按最近错误时间排序
- [ ] `amc review --due`：只显示间隔复习到期的题（MVP 用简单规则：错后 1/3/7 天）
- [ ] `amc review --count 10`：进入交互式重做，mode=review
- [ ] 重做正确后更新 `mastery`，并标记该错题“已订正”
- [ ] `amc wrong list` / `amc wrong remove <id>`：查看和手动移除错题

**验收：** 做错 3 题后 `amc review` 能看到；重做正确后掌握度上升。

---

## 6. 掌握度与推荐（MVP 规则）

- [ ] `mastery` 更新公式：按 tag 加权正确率，难度权重 + 最近性衰减
- [ ] 简单版：`score = 0.7*score + 0.3*(correct?1:0)`，按 tag 更新
- [ ] `amc stats`：各 tag 的掌握度、做题数、正确率、待复习数
- [ ] `amc stats --tag geometry`：单标签详情
- [ ] `amc recommend --count 5`：规则推荐
  - 找 mastery 最低的 2–3 个 tag
  - 选难度匹配（当前 mastery 低→难度 1–3；中→2–4；高→3–5）
  - 排除最近做过的题
  - 输出推荐理由：“你在‘数论-同余’正确率 40%，推荐 3 道基础题”
- [ ] `amc recommend --json` 供脚本使用

**验收：** 新用户做 20 题后，`amc recommend` 给出 5 道有理由的题；理由能对上 stats。

---

## 7. 配置与体验

- [ ] `amc config set target AMC12`、`amc config show`
- [ ] 配置项：目标竞赛、默认题数、是否默认显示答案、plain 模式
- [ ] 颜色和表格用 Rich；`--no-color` 可关
- [ ] 错误信息友好：库不存在提示 `amc init`；id 不存在提示 `amc list`
- [ ] 日志：`~/.amc-cli/logs/`，记录导入失败和异常

**验收：** 首次使用不看文档也能按提示走完 init→import→practice。

---

## 8. 测试与打包

- [ ] pytest：导入解析、判分、mastery 更新、推荐规则
- [ ] 用临时 SQLite 做集成测试：init→import→practice→stats
- [ ] `amc --help` 快照测试
- [ ] `pip install -e .` 和 `python -m amc_cli` 两种入口都可用
- [ ] README：安装、命令示例、数据来源、许可证说明

**验收：** `pytest` 全绿；新机器按 README 能跑通。

---

## 9. 后期小模型补全的接口（先留坑）

- [ ] `amc import --need-solution` 导出待补题到 `need_solution.jsonl`
- [ ] `amc enrich --input result.jsonl` 导入模型补全结果，标记 `solution_source=model`
- [ ] `amc show` 区分显示“原始解答”和“模型生成解答”
- [ ] MVP 不实现自动调用模型，只留导入接口

**验收：** 能导入一批模型生成的解答，并在 `show` 中带标记显示。

---

## 推荐执行顺序（垂直切片）

1. **骨架 + init + import + list/show**
2. **practice 交互做题 + attempts 记录**
3. **review 错题本 + stats 掌握度**
4. **recommend 规则推荐**
5. **测试、README、找 1 个同学试用**
6. 再扩题量、再优化标签、再接小模型补全

---

## 命令速查（目标形态）

```bash
amc init
amc import data/questions_v1.jsonl --dedupe
amc list --contest AMC12 --year 2023 --tag geometry
amc show 123 --with-solution --plain
amc practice --count 10 --tag algebra
amc review --due --count 5
amc stats
amc recommend --count 5
amc config set target AMC12
```

---

## 不要做的事

- [ ] 不要在终端里死磕复杂公式渲染
- [ ] 不要先做多用户和云同步
- [ ] 不要没有答案就硬做自动判分
- [ ] 不要先上复杂推荐模型
- [ ] 不要把模型补全的解答和原始解答混在一起不标记

核心就一句：**CLI 先做“导入→查题→做题→错题→统计→规则推荐”的闭环，公式显示 LaTeX 原文，单用户本地 SQLite，两周内能自己用起来。**