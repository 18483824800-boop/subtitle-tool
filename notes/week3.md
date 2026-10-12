# 第 3 周：工程规范与 CI 笔记

## 一、本周目标

|          目标.          |     说明            |
|------------------------|---------------------|
|     学会代码规范工具      | black、flake8、mypy |
| 学会配置 pyproject.toml | 工具配置写这里        |
|         学会 CI        | GitHub Actions      |
|        理解真实项目     | 读 flask 的 CI 和配置 |


## 二、本周完成

| 天 | 内容 | 状态 |
|----|------|------|
| 第 1 天 | 克隆 flask，看 CI | ✅ |
| 第 2 天 | 看 flask 的 tests.yaml | ✅ |
| 第 3 天 | 看 flask 的 pyproject.toml | ✅ |
| 第 4 天 | 安装工具 | ✅ |
| 第 5 天 | 配置 pyproject.toml | ✅ |
| 第 6 天 | 配置 GitHub Actions | ✅ |
| 第 7 天 | 写笔记 | ✅ |


## 三、三个工具

### black — 自动格式化

**作用**：统一代码格式（空格、缩进、行长度）。

**命令**：

    black --check .    # 只检查，不改
    black .            # 检查并修改

**它能修什么**：
- E225：运算符两边空格
- E231：逗号/冒号后空格
- E302：函数间空行（2 行）
- W291/W293：行尾/空行空格
- W292：文件末尾换行
- W391：文件末尾多空行

### flake8 — 代码检查

**作用**：检查代码质量和风格。

**命令**：

    flake8 .

**常见报错**：

| 报错 | 含义 |
|------|------|
| F401 | 未使用导入 |
| E225 | 运算符两边缺空格 |
| E231 | 逗号/冒号后缺空格 |
| E302 | 函数间空行不够 |
| E501 | 行太长 |
| W291/W293 | 行尾/空行有空格 |
| W292 | 文件末尾没换行 |
| W391 | 文件末尾多空行 |
| E402 | 导入不在文件顶部 |
| E251 | 关键字参数空格 |
| E304 | 装饰器后空行 |
| E265 | 注释格式 |

**flake8 默认不读 pyproject.toml**，要装 `Flake8-pyproject` 插件。

### mypy — 类型检查

**作用**：检查类型注解。

**命令**：

    mypy subtitle_tool/

**常见报错**：

|           报错           |      含义  |
|-------------------------|------------|
|       import-untyped.   | 库缺类型存根 |
| missing type annotation | 缺类型注解   |

**解决 `import-untyped`**：
- 装类型存根（如 `types-PyYAML`）。
- 或配置 `ignore_missing_imports = true`。


## 四、pyproject.toml

[project]
name = "subtitle-tool"
version = "0.1.0"
description = "用 Ollama 翻译和合并 SRT 字幕"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "requests>=2.31.0",
    "pyyaml>=6.0",
]

[project.scripts]
subtitle-tool = "subtitle_tool.main:main"

[tool.black]
line-length = 100

[tool.flake8]
max-line-length = 100

[tool.mypy]
python_version = "3.10"

[[tool.mypy.overrides]]
module = "yaml.*"
ignore_missing_imports = true

### 各段作用

段	                      作用
[project]	              项目信息 + 依赖
[project.scripts]	      命令行入口
[tool.black]	          black 配置
[tool.flake8]	         flake8 配置
[tool.mypy]	             mypy 配置
[[tool.mypy.overrides]]	对某些模块放宽

关键点
black 和 flake8 的行长要一致（都设 100），否则冲突。
mypy 的 python_version 要 ≥ 3.10（新版 mypy 不支持 3.8）。

## GitHub Actions
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
      - run: pip install pytest black flake8 mypy
      - run: black --check .
      - run: flake8 .
      - run: mypy subtitle_tool/
      - run: python -m pytest tests/

### 核心概念
概念	   说明
on	    触发条件（push、pull_request）
jobs	任务列表
runs-on	运行环境
steps	步骤列表
uses	用现成 action
run	    执行 shell 命令

### 对照 requests 和 flask
维度	      requests	       flask	          你的
触发条件	   所有 push/PR	   特定分支	          所有 push/PR
环境	      多系统矩阵	    多系统矩阵	       只 Ubuntu
Python 版本	  8 个	          11 个	              1 个
工具	     make	          uv + tox	       pip + black + flake8 + mypy + pytest

## 第 3 周学到的核心概念
概念	               说明
代码规范	           统一风格，方便协作
自动化检查	            让工具帮你查错
black	              自动格式化
flake8	             代码质量检查
mypy	             类型检查
pyproject.toml	    工具配置集中地
CI	                每次提交自动跑检查
GitHub Actions	    GitHub 的 CI 服务
Flake8-pyproject	让 flake8 读 pyproject.toml
类型存根	         types-PyYAML

## 遇到的问题
问题	                         怎么解决的
black 和 flake8 行长冲突	       都设 100
flake8 不读 pyproject.toml	      装 Flake8-pyproject 插件
mypy 报 yaml 缺存根	              装 types-PyYAML
mypy 警告 python_version 3.8	 改成 3.10
YAML 缩进错	                     每层 2 空格
YAML 拼写错	                     Tets → Tests，requirements.tx → requirements.txt

## 跑过的命令
bash
# 安装工具
pip3 install black flake8 mypy
pip3 install Flake8-pyproject
pip3 install types-PyYAML

# 检查
black --check .
flake8 .
mypy subtitle_tool/
python3 -m pytest tests/ -v

# 修格式
black .

# 验证 YAML
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/tests.yml')); print('YAML OK')"

## 一句话总结第 3 周
第 3 周 = 给项目加"代码规范"和"CI"。
核心工具：black、flake8、mypy、GitHub Actions。
核心文件：pyproject.toml、.github/workflows/tests.yml。


## 第 3 周完成
天	          内容	                        状态
第 1 天	      克隆 flask，看 CI	             ✅
第 2 天	      看 flask 的 tests.yaml	    ✅
第 3 天	      看 flask 的 pyproject.toml	✅
第 4 天	      安装工具	                     ✅
第 5 天	      配置 pyproject.toml	        ✅
第 6 天	      配置 GitHub Actions	        ✅
第 7 天	     写笔记	                        ✅

## 第 3 周成果
subtitle_tool/
├── .github/
│   └── workflows/
│       └── tests.yml        ← 新增：CI 配置
├── subtitle_tool/
│   ├── __init__.py          ← black 格式化
│   ├── parse.py
│   ├── translate.py
│   ├── merge.py
│   └── config.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_parse.py
│   ├── test_merge.py
│   └── test_translate.py
├── notes/
│   ├── week1.md
│   ├── week2.md
│   └── week3.md             ← 新增
├── config.yaml
├── pyproject.toml           ← 新增：工具配置
├── requirements.txt
├── README.md
└── main.py
核心产出：
pyproject.toml（配置 black、flake8、mypy）。
.github/workflows/tests.yml（CI 配置）。
所有代码已格式化和检查通过。

一句话总结第 3 周
第 3 周 = 给项目加"代码规范"和"CI"。
核心工具：black、flake8、mypy、GitHub Actions。
核心文件：pyproject.toml、.github/workflows/tests.yml。
你的代码现在：格式统一、风格规范、类型正确、CI 自动跑。