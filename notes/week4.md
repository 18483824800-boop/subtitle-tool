# 第 4 周：巩固 CI 笔记

## 一、本周目标

|      目标.       |       说明.      |
|------------------|-----------------|
| 把项目推到 GitHub | 用 git 和 GitHub |
|    让 CI 全绿     |     修 CI 报错   |
| 理解本地和 CI 的差异| 本地通过 ≠ CI 通过|


## 二、本周完成

|        任务     | 状态 |
|----------------|------|
|     初始化 git  | ✅ |
|    配置 git 用户 | ✅ |
| 创建 .gitignore | ✅ |
| 创建 GitHub 仓库 | ✅ |
| 推送到 GitHub    | ✅ |
|   修 CI 错误     | ✅ |
|      CI 全绿.    | ✅ |


## 三、git 基础

### 三层结构

工作区（你改的文件）
    │
    │ git add .
    ▼
暂存区（准备提交的文件）
    │
    │ git commit -m "..."
    ▼
本地仓库（历史记录）
    │
    │ git push
    ▼
远程仓库（GitHub）


### 四条核心命令

|           命令          |      作用    |   类比.     |
|------------------------|--------------|------------|
|  git config user.name  |   设置用户名.  |  论文作者名  |
| git config user.email  |   设置邮箱.    | 论文联系方式 |
|      git add .         |  加文件到暂存区 |   放购物车   |
|    git commit -m "..." |  提交到本地仓库 |    结账.    |
|       git push         |  推送到 GitHub |    寄到仓库  |


### 第一次推送的完整流程

    cd ~/Desktop/fly/subtitle_tool
    git init
    git config user.name "melodysun"
    git config user.email "melodysun@localhost"
    git add .
    git commit -m "Initial commit"
    git remote add origin https://github.com/18483824800-boop/subtitle-tool.git
    git branch -M main
    git push -u origin main


### 后续提交的流程

    git add .
    git commit -m "Fix: ..."
    git push


## 四、.gitignore

### 作用

告诉 git"哪些文件不要提交"。

### 内容

    __pycache__/
    *.pyc
    *.pyo
    .pytest_cache/
    .mypy_cache/
    *.egg-info/
    dist/
    build/
    .venv/
    venv/
    *.log
    .DS_Store
    subtitle_tool_backup/

### 各行含义

|             行 |        作用     |
|----------------|----------------|
|   __pycache__/ | Python 编译缓存 |
|       *.pyc.   |   编译后的字节码 |
| .pytest_cache/ |    pytest 缓存 |
|   .mypy_cache/ |      mypy 缓存 |
|    .venv/      |        虚拟环境 |
|     *.log      |        日志文件 |
|    .DS_Store.  |  Mac 文件夹配置 |


## 五、GitHub Actions

### 什么是 CI

CI = Continuous Integration（持续集成）。

每次 push 或 PR，GitHub 自动跑你配置的任务。

结果在 GitHub 页面上显示：
- 🟡 黄色：正在跑
- ✅ 绿色：通过
- ❌ 红色：失败

### 配置文件

.github/workflows/tests.yml：

    name: Tests

    on: [push, pull_request]

    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v5
            with:
              python-version: "3.11"
          - run: pip install -r requirements.txt
          - run: pip install pytest black flake8 mypy Flake8-pyproject
          - run: black --check .
          - run: flake8 .
          - run: mypy subtitle_tool/
          - run: python -m pytest tests/

### 核心概念

| 概念     |           说明               |
|---------|------------------------------|
| on      | 触发条件（push、pull_request） |
| jobs    | 任务列表                      |
| runs-on | 运行环境                      |
| steps.  | 步骤列表                      |
| uses    | 用现成 action                 |
| run     | 执行 shell 命令               |


## 六、CI 失败与修复

### 第一次 CI 失败

日志：

    Run flake8 .
    ./main.py:47:80: E501 line too long (97 > 79 characters)
    ./subtitle_tool/parse.py:13:80: E501 line too long (80 > 79 characters)
    ...

**原因**：CI 里的 flake8 没读 pyproject.toml，行长还是默认的 79。

**为什么**：本地装了 Flake8-pyproject 插件，CI 没装。

### 修复

在 CI 配置里加 Flake8-pyproject：

    - run: pip install pytest black flake8 mypy Flake8-pyproject

### 修复后

CI 全绿 ✅


## 七、本地和 CI 的差异（重点）

### 差异 1：flake8 读不读 pyproject.toml

| 环境  |     装了什么           |    flake8 读什么   |
|------|-----------------------|-------------------|
| 本地  | 装了 Flake8-pyproject | 读 pyproject.toml  |
| CI   |     只装了 flake8      |   读默认配置（79）   |

**解决**：CI 里也装 Flake8-pyproject。

### 差异 2：pytest 能不能找到包

|             环境         | sys.path 含项目根目录吗|
|-------------------------|----------------------|
| 本地（python -m pytest） |         是            |
| CI（python -m pytest）  |          是           |

**你的项目结构**（非 src/ 布局），pytest 能找到包。

**不需要 pip install -e .**。

### 结论

**本地通过 ≠ CI 通过。**

**CI 是"干净环境"，要显式声明所有依赖。**

**这是 CI 的价值：帮你发现本地忽略的问题。**


## 八、常见的"本地通过，CI 失败"原因

| 原因      |         例子.            |       怎么修           |
|-----------|-------------------------|-----------------------|
| 依赖没声明 | 本地装了某个包，CI 没装.    | 加到 requirements.txt |
| 插件没声明 | Flake8-pyproject 只在本地 | CI 里显式装            |
| 环境差异   | Python 版本不同           | CI 里指定版本          |
| 路径问题   | 本地能 import，CI 不能     | pip install -e .     |
| 缓存问题   | 本地有缓存，CI 没有         | 清缓存重跑             |


## 九、git 提交信息规范

### 常见前缀

| 前缀      | 含义 |              例子               |
|----------|------|--------------------------------|
| Fix:     | 修 bug| Fix: install Flake8-pyproject |
| Add:     | 加功能 | Add: 支持 DeepL 翻译           |
| Docs:    | 改文档 | Docs: 更新 README              |
| Refactor:| 重构   | Refactor: 拆分 parse 模块      |
| Test:    | 改测试 | Test: 加 parse 边界测试         |
| Chore:   | 杂事   | Chore: 更新依赖                |

### 为什么写前缀

- 一眼看出 commit 类型。
- 方便生成 changelog。
- 团队协作更清晰。


## 十、遇到的错误

|                         错误         |    原因       | 怎么修 |
|-------------------------------------|--------------|--------|
|        fatal: not a git repository  | 没初始化 git  | git init |
| fatal: unable to access ... Empty   |   网络问题.   |   重试   |
| CI 失败：E501 line too long (97 > 79)| CI 里 flake8 没读 pyproject.toml | 装 Flake8-pyproject |


## 十一、跑过的命令

    # git 初始化
    git init
    git config user.name "melodysun"
    git config user.email "melodysun@localhost"

    # 第一次提交
    git add .
    git commit -m "Initial commit"

    # 关联远程
    git remote add origin https://github.com/18483824800-boop/subtitle-tool.git
    git branch -M main
    git push -u origin main

    # 后续提交
    git add .
    git commit -m "Fix: install Flake8-pyproject in CI"
    git push


## 十二、第 4 周学到的核心概念

|     概念        |     说明    |
|----------------|------------|
| git init       | 初始化仓库   |
| git add        | 加到暂存区   |
| git commit     | 提交到本地   |
| git push       | 推到 GitHub |
| git remote add | 关联远程     |
| .gitignore     | 忽略文件     |
| GitHub Actions | CI 服务     |
| CI 全绿         | 所有检查通过 |
| 本地 ≠ CI.      | CI 是干净环境|
| 依赖显式声明     | CI 里装所有依赖|


## 十三、对照 requests 和 flask

| 维度       | requests.     | flask.     |        你的                           |
|------------|--------------|------------|---------------------------------------|
| CI 文件     | run-test.yml | tests.yaml | tests.yml                             |
| 触发条件     | 所有 push/PR | 特定分支     | 所有 push/PR                           |
| 环境        | 多系统矩阵    | 多系统矩阵.   | 只 Ubuntu                             |
| Python 版本 | 8 个         | 11 个        | 1 个                                 |
| 工具        | make.        | uv + tox    | pip + black + flake8 + mypy + pytest |


## 十四、一句话总结第 4 周

第 4 周 = 把项目推到 GitHub，让 CI 全绿。
核心：git 三件套（add/commit/push）+ GitHub Actions。
重点：本地通过 ≠ CI 通过，CI 是干净环境，要显式声明依赖。