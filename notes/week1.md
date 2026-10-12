# 第 1 周：项目结构笔记

## 一、本周目标

|         目标      |       说明     |
|------------------|----------------|
| 读懂真实项目结构    | 以 requests 为例 |
| 理解每个文件的作用  | README、pyproject.toml、包目录、测试 |
| 把知识用到自己的项目 | subtitle_tool |


## 二、requests 顶层结构

requests/
├── .github/ ← GitHub 配置（含 CI）
├── docs/ ← 文档
├── src/requests/ ← 源码包
├── tests/ ← 测试
├── .gitignore ← Git 忽略规则
├── AUTHORS.rst ← 作者列表
├── HISTORY.md ← 更新日志
├── LICENSE ← 许可证
├── Makefile ← 自动化命令
├── README.md ← 项目说明
├── pyproject.toml ← 项目配置
├── setup.py ← 安装脚本
└── tox.ini ← 测试配置

### 顶层文件作用

| 文件 | 作用 |
|------|------|
| README.md | 项目说明书，别人第一眼看的 |
| pyproject.toml | 项目配置：名字、版本、依赖、工具配置 |
| setup.py | 安装脚本（旧方式） |
| LICENSE | 许可证 |
| HISTORY.md | 更新日志 |
| AUTHORS.rst | 作者列表 |
| Makefile | 自动化命令 |
| tox.ini | 多环境测试配置 |
| .gitignore | Git 忽略的文件 |
| .github/ | GitHub 配置，含 CI |


## 三、四个必看模块
### 1. exceptions.py — 异常设计
核心思想：
所有异常继承一个根异常 RequestException
用户可以"粗捕"（except RequestException）或"精捕"（except ConnectTimeout）
有些异常多重继承 ValueError/TypeError，融入 Python 内置异常体系
异常可以带上下文（request、response 属性）
警告和异常分开（RequestsWarning 继承 Warning）

IOError
└── RequestException
    ├── HTTPError
    ├── ConnectionError
    │   ├── ProxyError
    │   ├── SSLError
    │   └── ConnectTimeout（也继承 Timeout）
    ├── Timeout
    │   ├── ConnectTimeout
    │   └── ReadTimeout
    ├── InvalidURL（也继承 ValueError）
    ├── MissingSchema（也继承 ValueError）
    └── ...

学到：
异常要分层
异常要能粗捕也能精捕
异常要融入 Python 体系
异常可以带上下文

### 2. api.py — 对外 API

作用：
提供 get/post/put/patch/delete/head/options/request 八个函数
所有函数最终调用 request()

参数对应关系：

函数	    特殊参数
request()	通用
get()	   params（放 URL）
post()	   data、json（放请求体）
put()	   data
patch()	   data
delete()	-
head()	   allow_redirects=False（默认不重定向）
options()	-
GET vs POST：
对比	    GET	           POST
用途	    查数据	        提交数据
数据位置	URL（params）	请求体（data/json）
幂等	   是	              否
安全	   低	              高
典型	   搜索、查看	     登录、注册

data vs json：
参数	发送格式	Content-Type
data	表单	application/x-www-form-urlencoded
json	JSON	application/json

七个方法语义：
方法	语义	 记忆
GET	    查	    拿到数据
POST	增	    投递数据
PUT	    全改	放新的覆盖旧的
PATCH	局部改	 打补丁
DELETE	删	    删除数据
HEAD   只看头	我只要头
OPTIONS	探测	问支持啥

### 3. models.py — 只看 Response 类

属性：
属性	          说明
status_code	     状态码，如 200、404
headers	         响应头，大小写不敏感
url	             最终 URL
encoding	     编码
reason	        状态码文字说明（"OK"）
cookies	        服务器返回的 Cookie
elapsed	         请求耗时（timedelta）
history	        重定向历史
request	       对应的 PreparedRequest

@property：
属性	             作用
ok	                状态码 < 400
content	            响应体（bytes，延迟加载）
text	            响应体（str，自动解码）
apparent_encoding	推测编码
is_redirect	        是否重定向

content vs text：
属性	 返回	是否解码	适合
content	bytes	否	      图片、文件、二进制
text	str	    是	      HTML、JSON、文本

记忆口诀：
content 是"原始内容"，带 b
text 是"文本内容"，不带 b

延迟加载：
_content 初始是 False，表示"还没读"
第一次访问 r.content 时才真正下载
读完缓存，第二次直接返回
好处：省带宽、省时间、省内存

特殊方法：
方法	     作用
repr	    print(r) 显示 <Response [200]>
bool	    if r: 状态码 < 400 时为 True
iter	    for chunk in r: 逐块迭代
enter/exit	支持 with 语句

方法：
方法	             作用
json()	            解析 JSON
raise_for_status()	4xx/5xx 抛异常
iter_content()	    逐块读取
iter_lines()	    逐行读取
close()	            关闭连接
raise_for_status()：

400~499 → 抛 HTTPError("Client Error")
500~599 → 抛 HTTPError("Server Error")
3xx 不抛（重定向是正常的）


### 4. __init__.py — 包的入口
作用：
- 把子模块的东西"提升"到包顶层
- 定义 __version__ 等包级变量
- 用 __all__ 声明 from 包 import * 时导出什么

效果：

# 没有 __init__.py，要写完整路径
from requests.api import get

# 有 __init__.py，可以简写
from requests import get

核心代码：
__version__ = "2.32.3"
from .api import get, post, put, patch, delete, head, options, request
from .models import Request, Response
from .exceptions import RequestException
from .sessions import Session
__all__ = ["get", "post", ..., "Request", "Response", ...]

## 四：看任何模块的三个问题

这个模块负责什么？（一句话）
它对外提供什么？（函数/类/常量）
它依赖谁？（导入了什么）
能回答这三个问题，就算"看完了"。
细节看不懂的，记下来，继续往下走

## 五、测试和 CI

### 测试
测试文件命名：test_*.py
测试函数命名：test_*
测试结构：准备 → 执行 → 断言
用 assert 断言
用 pytest.raises 测异常
用 @pytest.mark.parametrize 参数化
用 fixture 注入依赖

### conftest.py
pytest 的共享配置文件
里面定义 fixture
同目录及子目录的测试都能用

fixture 两种写法：
# 简单 fixture
@pytest.fixture
def data():
    return {"key": "value"}

# 带清理的 fixture
@pytest.fixture
def server():
    准备
    yield 值
    清理

### CI
on: 触发条件（push、pull_request）
jobs: 任务
matrix: 多环境测试
steps: 步骤
uses: 用 action
run: 执行命令

## 六、subtitle_tool 结构

subtitle_tool/
├── subtitle_tool/
│   ├── __init__.py
│   ├── parse.py
│   ├── translate.py
│   ├── merge.py
│   └── config.py
├── tests/
│   ├── __init__.py
│   └── test_parse.py
├── config.yaml
├── requirements.txt
├── README.md
└── main.py

### 各文件作用
文件	                      作用
subtitle_tool/	             源码包
subtitle_tool/init.py	     包入口，提升 API
subtitle_tool/parse.py	     SRT 解析和拼装
subtitle_tool/translate.py	调用 Ollama 翻译
subtitle_tool/merge.py	    合并双语字幕
subtitle_tool/config.py	    加载配置
tests/	                    测试
config.yaml	                配置文件
requirements.txt	        依赖列表
README.md	                项目说明
main.py	                    命令行入口

## 七、subtitle_tool 代码

### parse.py

"""SRT 解析模块"""
import re
from pathlib import Path

def parse_srt(path):
    """解析 SRT 文件，返回字幕块列表"""
    ...

def build_srt(blocks):
    """把字幕块列表重新拼成 SRT 字符串"""
    ...

parse_srt：SRT 字符串 → 列表
build_srt：列表 → SRT 字符串
两者互逆

### translate.py

"""翻译模块"""
import time
import requests

def translate_text(text, model, ollama_url, timeout=120, max_retries=3, retry_delay=2):
    """调用 Ollama 翻译单段文本"""
    ...
发 POST 请求给 Ollama
用 json=payload（不是 data=）
有重试机制
全失败时返回原文

### merge.py
"""字幕合并模块"""
from .parse import parse_srt, build_srt

def merge_srt(en_file, zh_file, output_file):
    """合并英文和中文字幕"""
    ...
用 build_srt 拼装（不重复造轮子）

### config.py
python
"""配置加载模块"""
import yaml
from pathlib import Path

def load_config(path="config.yaml"):
    """加载配置文件"""
    ...
用 yaml.safe_load（不是 load，安全）
文件不存在时抛 FileNotFoundError

### init.py
python
"""字幕工具包"""
__version__ = "0.1.0"

from .parse import parse_srt, build_srt
from .translate import translate_text
from .merge import merge_srt

__all__ = ["parse_srt", "build_srt", "translate_text", "merge_srt"]

### main.py
python
#!/usr/bin/env python3
"""字幕工具命令行入口"""
import sys
from pathlib import Path

from subtitle_tool.config import load_config
from subtitle_tool.parse import parse_srt, build_srt
from subtitle_tool.translate import translate_text
from subtitle_tool.merge import merge_srt

def translate_srt(input_file, output_file, config):
    ...

def main():
    ...

if __name__ == "__main__":
    main()
命令行入口
支持 translate 和 merge 两个命令
用 sys.argv 读参数

## 八、第 1 周学到的核心概念
概念	               说明
一个文件一个职责	     parse.py 只管解析
同包导入用 .	        from .parse import ...
init.py 提升 API	   from .parse import parse_srt
依赖和配置分开	        requirements.txt + config.yaml
延迟加载	           Response.content
异常分层	           RequestException 为根
测试结构	           准备 → 执行 → 断言
CI	                  GitHub Actions自动跑测试
未使用导入是问题	    flake8 会报 F401
DRY 原则	           Don't Repeat Yourself


## 九、遇到的问题
问题	                        怎么解决的
exceptions.py 的 reduce         看不懂	跳过，以后再看
merge.py 的未使用导入	          用 build_srt 替代手动拼装
main.py漏了 load_config 的括号	  加 ()
config["ollama"] 报 TypeError	检查 load_config() 有没有括号


## 十、对照：requests vs subtitle_tool
requests	    subtitle_tool
src/requests/	subtitle_tool/
init.py	        init.py
api.py	        main.py
models.py	    parse.py
exceptions.py	（待写）
sessions.py	    merge.py
utils.py	    config.py
tests/	        tests/
pyproject.toml	requirements.txt + config.yaml
README.md	    README.md

### 我说API 和 main.py"对应"，是指功能定位相似：
维度	    api.py	               你的 main.py
定位	    对外入口	             对外入口
用户怎么用	requests.get(url)	    python3 main.py translate audio.srt
底层调用	request() → Session	    translate_srt() → parse_srt + translate_text + build_srt
两者都是"用户接触的第一层"

### 但它们的"形式"不同
api.py 是"库的入口"
python
# 用户这样用
1. import requests
r = requests.get('https://api.github.com')
用户是程序员。
调用方式：写 Python 代码。
入口：requests.get() 这个函数。

2. main.py 是"命令行工具的入口"
bash
# 用户这样用
python3 main.py translate audio.srt
用户是命令行使用者。
调用方式：在终端敲命令。
入口：main() 这个函数。
都是"入口"，但面向的用户不同。

### models.py 和 parse.py 为什么对应

1. 两个文件的功能
models.py 定义了什么：
Request：请求对象。
PreparedRequest：准备好的请求。
Response：响应对象。
核心职责：定义"数据长什么样"。

parse.py 定义了什么：
parse_srt()：SRT 字符串 → 列表。
build_srt()：列表 → SRT 字符串。
核心职责：处理"数据"。

2. 为什么说它们"对应"

因为两者都处理"核心数据结构"。
维度	    requests 的 models.py	      你的 parse.py
核心职责	  定义数据模型	                  处理数据
处理什么	  Request、Response	            SRT 字幕块
在项目里的位置	核心模块	                  核心模块
被谁用	      api.py、sessions.py	       merge.py、main.py

3. 但它们的"处理方式"不同

3.1 models.py 用"类"
python
class Response:
    def __init__(self):
        self.status_code = None
        self.headers = {}
        self.url = None
        ...

    @property
    def content(self):
        ...
特点：
用类表示数据。
数据是"对象"，有属性和方法。
r.status_code、r.json()。

3.2 parse.py 用"函数 + 字典"
python
def parse_srt(path):
    ...
    blocks.append({
        "idx": "1",
        "timecode": "00:00:00,000 --> 00:00:04,200",
        "text": "Hello",
    })
    return blocks
特点：
用字典表示数据。
数据是"字典"，用 block["text"] 访问。
没有方法，只有数据。

4. 对应关系
requests                          subtitle_tool
────────                          ─────────────
                                  
models.py                         parse.py
  │                                 │
  ├── class Request                 ├── def parse_srt(path)
  │   ├── method                    │   └── 返回 list[dict]
  │   ├── url                       │
  │   └── headers                   ├── def build_srt(blocks)
  │                                 │   └── 返回 str
  ├── class PreparedRequest         
  │                                 
  └── class Response                
      ├── status_code               
      ├── headers                   
      ├── content                   
      ├── text                      
      ├── json()                    
      └── raise_for_status()        

5. 更准确的对应

其实你的 parse.py 同时对应 requests 的两个东西：
requests	                    subtitle_tool	            说明
models.py	                    parse.py	              都处理核心数据
compat.py 的 json	            parse.py 的 parse_srt	  都是"解析"
models.py 的 Response.content	parse.py 的 build_srt	  都是"拼装"
因为 requests 把"解析"和"数据模型"分开，而你把它们合在 parse.py 里。
为什么？
requests 复杂，需要分开。
你的项目简单，合在一起就够。

### 为什么说sessions.py 对应 merge.py

因为两者都是"组合器"：把多个底层组件组合起来，完成一个完整任务。

维度	      requests 的 sessions.py	                   你的 merge.py
核心职责	   组合组件，完成完整请求	                      组合函数，完成合并
组合了什么	   Request + Response + 适配器 + Cookie	        parse_srt + build_srt
在项目里的位置	逻辑层	                                      逻辑层
被谁用	       api.py	                                    main.py
sessions.py：把"造请求 → 发请求 → 处理响应"串起来。
merge.py：把"解析英文 → 解析中文 → 合并 → 拼装"串起来。

### 更重要的：你要理解"分层"

一个项目通常分几层：
层	    职责	          requests	     你的项目
入口层	用户接触的第一层	api.py	         main.py
数据层	定义/处理数据	   models.py	   parse.py
逻辑层	业务逻辑	      sessions.py	  merge.py、translate.py
工具层	辅助工具	      utils.py	      config.py
异常层	错误定义	      exceptions.py	（待写）











