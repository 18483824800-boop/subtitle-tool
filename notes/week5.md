# 第 5 周：设计模式与架构笔记

## 一、本周目标

| 目标 | 说明 |
|------|------|
| 理解 httpx 架构 | 看 `_client.py` 和 `_transports/` |
| 学策略模式 | 同一件事多种做法 |
| 重构 subtitle_tool | 用策略模式 |
| CI 全绿 | 提交到 GitHub |


## 二、本周完成

| 天 | 内容 | 状态 |
|----|------|------|
| 第 1 天 | 克隆 httpx，看源码结构 | ✅ |
| 第 2 天 | 看 `_client.py` | ✅ |
| 第 3 天 | 看 `_transports/` | ✅ |
| 第 4 天 | 学策略模式 | ✅ |
| 第 5 天 | 重构 `subtitle_tool` | ✅ |
| 第 6 天 | 学工厂模式 | ⬜ |
| 第 7 天 | 写笔记 | ✅ |


## 三、httpx 的结构

### 顶层结构

    httpx/
    ├── .git/
    ├── .github/            ← CI
    ├── .gitignore
    ├── CHANGELOG.md        ← 更新日志
    ├── LICENSE.md          ← 许可证
    ├── README.md           ← 项目说明
    ├── docs/               ← 文档
    ├── httpx/              ← 源码包
    ├── mkdocs.yml          ← 文档配置
    ├── pyproject.toml      ← 项目配置
    ├── requirements.txt    ← 依赖
    ├── scripts/            ← 脚本
    └── tests/              ← 测试

### 源码包

    httpx/
    ├── __init__.py
    ├── __version__.py
    ├── _api.py             ← 公共 API
    ├── _auth.py            ← 认证
    ├── _client.py          ← 客户端
    ├── _config.py          ← 配置
    ├── _content.py         ← 内容处理
    ├── _decoders.py        ← 解码
    ├── _exceptions.py      ← 异常
    ├── _main.py            ← 命令行入口
    ├── _models.py          ← 数据模型
    ├── _multipart.py       ← 多部分表单
    ├── _status_codes.py    ← 状态码
    ├── _transports/        ← 传输层（核心）
    ├── _types.py           ← 类型定义
    ├── _urlparse.py        ← URL 解析
    ├── _urls.py            ← URL 处理
    ├── _utils.py           ← 工具函数
    └── py.typed            ← 类型标记

### `_` 前缀的含义

`_` 开头的模块是"内部模块"，用户不应该直接 import。

用户只用 `httpx.get()` 或 `httpx.Client()`。

### 对照 requests

| requests | httpx | 作用 |
|----------|-------|------|
| api.py | _api.py | 公共 API |
| auth.py | _auth.py | 认证 |
| sessions.py | _client.py | 客户端 |
| models.py | _models.py | 数据模型 |
| exceptions.py | _exceptions.py | 异常 |
| adapters.py | _transports/ | 传输层 |
| utils.py | _utils.py | 工具 |


## 四、`_client.py` 的类结构

    class UseClientDefault:        # 标记"用默认值"
    class ClientState(enum.Enum):  # 客户端状态
    class BoundSyncStream:         # 同步流绑定
    class BoundAsyncStream:        # 异步流绑定
    class BaseClient:              # 客户端基类（核心）
    class Client(BaseClient):      # 同步客户端
    class AsyncClient(BaseClient): # 异步客户端

### 关键观察

1. `Client` 和 `AsyncClient` 都继承 `BaseClient`。
2. 这是"模板方法模式"：基类定义通用逻辑，子类实现同步/异步。

### `BaseClient.__init__`

    def __init__(
        self,
        *,
        auth=None,
        params=None,
        headers=None,
        cookies=None,
        timeout=DEFAULT_TIMEOUT_CONFIG,
        follow_redirects=False,
        max_redirects=DEFAULT_MAX_REDIRECTS,
        event_hooks=None,
        base_url="",
        trust_env=True,
        default_encoding="utf-8",
    ):
        ...

### 关键点

| 特点 | 说明 |
|------|------|
| `*` 开头 | 强制关键字参数 |
| 包装类 | Headers、Cookies、Timeout |
| `@property` + `@setter` | 读写时做处理 |
| 状态管理 | ClientState 枚举 |
| 默认超时 | 避免卡死 |
| base_url | 简化 API 调用 |

### `@property` + `@setter` 的作用

    @property
    def headers(self) -> Headers:
        return self._headers

    @headers.setter
    def headers(self, headers: HeaderTypes) -> None:
        client_headers = Headers({
            b"Accept": b"*/*",
            b"Accept-Encoding": ACCEPT_ENCODING.encode("ascii"),
            b"Connection": b"keep-alive",
            b"User-Agent": USER_AGENT.encode("ascii"),
        })
        client_headers.update(headers)
        self._headers = client_headers

**关键**：每次设置 headers，都会加"默认头"。

**默认头**：Accept、Accept-Encoding、Connection、User-Agent。

**用户传的头会覆盖默认头。**


## 五、`_transports/` 目录

    _transports/
    ├── __init__.py    ← 暴露 7 个类
    ├── base.py        ← 抽象基类
    ├── default.py     ← 默认实现（HTTPTransport）
    ├── mock.py        ← 测试用（MockTransport）
    ├── asgi.py        ← ASGI 应用（ASGITransport）
    └── wsgi.py        ← WSGI 应用（WSGITransport）

### `base.py`

    class BaseTransport:
        def __enter__(self): ...
        def __exit__(self, ...): self.close()
        def handle_request(self, request): 
            raise NotImplementedError(...)
        def close(self): pass

    class AsyncBaseTransport:
        async def __aenter__(self): ...
        async def __aexit__(self, ...): await self.aclose()
        async def handle_async_request(self, request):
            raise NotImplementedError(...)
        async def aclose(self): pass

### `default.py` 的 `HTTPTransport`

    class HTTPTransport(BaseTransport):
        def __init__(self, verify=True, cert=None, ...):
            import httpcore
            self._pool = httpcore.ConnectionPool(...)
        
        def handle_request(self, request):
            req = httpcore.Request(...)
            resp = self._pool.handle_request(req)
            return Response(...)
        
        def close(self):
            self._pool.close()

### 异常映射

    @contextlib.contextmanager
    def map_httpcore_exceptions():
        try:
            yield
        except Exception as exc:
            for from_exc, to_exc in HTTPCORE_EXC_MAP.items():
                if isinstance(exc, from_exc):
                    raise to_exc(str(exc)) from exc

**作用**：把 `httpcore` 的异常映射成 httpx 的异常。


## 六、策略模式

### 是什么

把"算法"抽出来，让它们可以互相替换。

### 三个角色

| 角色 | 作用 | 例子 |
|------|------|------|
| 策略接口 | 定义"做什么" | `Translator` |
| 具体策略 | 实现"怎么做" | `OllamaTranslator`、`DeepLTranslator` |
| 上下文 | 使用策略 | `translate_srt` |

### 代码结构

    # 1. 策略接口
    class Translator:
        def translate(self, text: str) -> str:
            raise NotImplementedError

    # 2. 具体策略
    class OllamaTranslator(Translator):
        def translate(self, text: str) -> str:
            ...

    class DeepLTranslator(Translator):
        def translate(self, text: str) -> str:
            ...

    # 3. 上下文
    def translate_srt(blocks, translator: Translator):
        for block in blocks:
            block["text"] = translator.translate(block["text"])

### 用法

    translator = OllamaTranslator(model="qwen2.5:7b", url="...")
    translate_srt(blocks, translator)

    # 换成 DeepL
    translator = DeepLTranslator(api_key="...")
    translate_srt(blocks, translator)

### 优点

| 优点 | 说明 |
|------|------|
| 符合开闭原则 | 加新策略不用改旧代码 |
| 易测试 | 每个策略独立测 |
| 易维护 | 每个策略短小 |
| 灵活 | 运行时切换策略 |
| 消除 if/else | 代码更清晰 |

### 缺点

| 缺点 | 说明 |
|------|------|
| 类变多 | 每个策略一个类 |
| 简单场景过度设计 | 只有 1 个策略时没必要 |


## 七、重构后的 subtitle_tool

### 目录结构

    subtitle_tool/
    ├── subtitle_tool/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── merge.py
    │   ├── parse.py
    │   └── translators/        ← 新增
    │       ├── __init__.py
    │       ├── base.py         ← Translator
    │       ├── ollama.py       ← OllamaTranslator
    │       └── deepl.py        ← DeepLTranslator
    ├── tests/
    ├── main.py
    └── ...

### `base.py`

    """翻译器抽象基类"""

    class Translator:
        """翻译器抽象基类"""

        def translate(self, text: str) -> str:
            """翻译单段文本"""
            raise NotImplementedError(
                "The 'translate' method must be implemented."
            )

### `ollama.py`

    """Ollama 翻译器"""
    import time
    from typing import Any
    import requests
    from .base import Translator

    class OllamaTranslator(Translator):
        """用 Ollama 本地模型翻译"""

        def __init__(self, model, url, timeout=120, max_retries=3, retry_delay=2):
            self.model = model
            self.url = url
            self.timeout = timeout
            self.max_retries = max_retries
            self.retry_delay = retry_delay

        def translate(self, text: str) -> str:
            prompt = (...)
            payload: dict[str, Any] = {...}
            for attempt in range(1, self.max_retries + 1):
                try:
                    resp = requests.post(
                        self.url,
                        json=payload,
                        timeout=self.timeout,
                        proxies={"http": None, "https": None},
                    )
                    resp.raise_for_status()
                    result = resp.json().get("response", "").strip()
                    if result:
                        return result
                except Exception:
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay)
                    else:
                        return text
            return text

### `deepl.py`

    """DeepL 翻译器（演示策略模式）"""
    import requests
    from .base import Translator

    class DeepLTranslator(Translator):
        def __init__(self, api_key, url="https://api-free.deepl.com/v2/translate"):
            self.api_key = api_key
            self.url = url

        def translate(self, text: str) -> str:
            resp = requests.post(
                self.url,
                headers={"Authorization": f"DeepL-Auth-Key {self.api_key}"},
                data={"text": text, "target_lang": "ZH"},
            )
            resp.raise_for_status()
            return resp.json()["translations"][0]["text"]

### `translators/__init__.py`

    """翻译器模块"""
    from .base import Translator
    from .deepl import DeepLTranslator
    from .ollama import OllamaTranslator

    __all__ = ["Translator", "OllamaTranslator", "DeepLTranslator"]


## 八、对照 httpx

| httpx | subtitle_tool |
|-------|---------------|
| `_transports/` | `translators/` |
| `base.py` 的 `BaseTransport` | `base.py` 的 `Translator` |
| `default.py` 的 `HTTPTransport` | `ollama.py` 的 `OllamaTranslator` |
| `mock.py` 的 `MockTransport` | `deepl.py` 的 `DeepLTranslator` |
| `__init__.py` | `__init__.py` |


## 九、为什么 `__init__` 里要 `self.model = model`

### 不写会怎样

    class OllamaTranslator:
        def __init__(self, model, url, ...):
            pass

        def translate(self, text):
            payload = {"model": model}  # ❌ NameError

`model` 只是 `__init__` 的参数，不是"对象的属性"。`__init__` 结束后消失。

### 写了的含义

    def __init__(self, model, url, ...):
        self.model = model   # 把参数存到"对象的属性"

**`self.xxx` 是"持久化"，参数是"临时"。**

### 为什么不用全局变量

多实例冲突：

    t1 = OllamaTranslator(model="qwen2.5:7b")
    t2 = OllamaTranslator(model="llama3")
    # 全局 model 被 t2 覆盖

`self.xxx` 是"每个实例独立"的。


## 十、遇到的问题

| 问题 | 怎么解决的 |
|------|-----------|
| 方法名写成 `translate_text` | 改成 `translate` |
| `@patch` 路径多了一个点 | 改成 `translators.ollama` |
| `ImportError: cannot import name 'OllamaTranslator'` | 写 `translators/__init__.py` |
| mypy 报 `json=payload` 类型错 | 加 `payload: dict[str, Any]` |
| mypy 报 `proxies` 类型错 | 加 `# type: ignore[dict-item]` |
| CI 失败：`ollama.py` 没格式化 | 本地跑 `black .` 再 push |


## 十一、跑过的命令

    # 创建目录和文件
    mkdir -p subtitle_tool/translators
    touch subtitle_tool/translators/__init__.py
    touch subtitle_tool/translators/base.py
    touch subtitle_tool/translators/ollama.py
    touch subtitle_tool/translators/deepl.py

    # 删旧文件
    rm subtitle_tool/translate.py

    # 验证导入
    python3 -c "from subtitle_tool.translators import Translator, OllamaTranslator, DeepLTranslator; print('OK')"

    # 跑检查
    black .
    flake8 .
    mypy subtitle_tool/
    python3 -m pytest tests/ -v

    # 提交
    git add .
    git commit -m "Refactor: 用策略模式重构翻译模块"
    git push


## 十二、第 5 周学到的核心概念

| 概念 | 说明 |
|------|------|
| 策略模式 | 同一件事多种做法 |
| 抽象基类 | 定义接口 |
| 继承 | 子类实现 |
| `self.xxx` | 持久化配置 |
| `__init__.py` | 提升类到顶层 |
| `@patch` 路径 | 要精确 |
| mypy 类型注解 | `dict[str, Any]` |
| `# type: ignore` | 忽略特定错误 |
| httpx 的 `_` 前缀 | 内部模块 |
| httpx 的分层架构 | API → 客户端 → 传输 |
| CI 是干净环境 | 本地通过 ≠ CI 通过 |


## 十三、一句话总结第 5 周

第 5 周 = 学设计模式（策略模式），重构 subtitle_tool。
核心：抽象基类 + 多实现，让代码更灵活。
对照：httpx 的 `_transports/` 就是策略模式。


## 十四、明天早上复习重点

1. **策略模式的三个角色**：接口、具体策略、上下文。
2. **为什么用 `self.xxx`**：持久化，每个实例独立。
3. **`@patch` 路径怎么写**：被测模块里看到的路径。
4. **mypy 类型注解**：`dict[str, Any]`、`# type: ignore`。
5. **对照 httpx**：`_transports/` vs `translators/`。
6. **CI 通过的条件**：black、flake8、mypy、pytest 全通过。