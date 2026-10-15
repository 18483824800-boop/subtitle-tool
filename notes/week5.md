# 第 5 周：设计模式与架构笔记

## 一、本周目标

|       目标.         |       说明                       |
|------------------- |------|
| 理解 httpx 架构     | 看 `_client.py` 和 `_transports/` |
| 学策略模式          | 同一件事多种做法                    |
| 学工厂模式          | 根据条件创建对象                    |
| 重构 subtitle_tool | 用策略 + 工厂                      |
| CI 全绿            | 提交到 GitHub                      |


## 二、本周完成

| 天      |         内容.        | 状态 |
|---------|---------------------|------|
| 第 1 天 | 克隆 httpx，看源码结构 | ✅ |
| 第 2 天 | 看 `_client.py`      | ✅ |
| 第 3 天 | 看 `_transports/`    | ✅ |
| 第 4 天 | 学策略模式             | ✅ |
| 第 5 天 | 重构 `subtitle_tool`（策略模式） | ✅ |
| 第 6 天 | 学工厂模式             | ✅ |
| 第 7 天 | 写笔记                | ✅ |


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

| requests.     | httpx          | 作用 |
|---------------|----------------|------|
| api.py        | _api.py        | 公共 API |
| auth.py       | _auth.py       | 认证 |
| sessions.py   | _client.py     | 客户端 |
| models.py     | _models.py     | 数据模型 |
| exceptions.py | _exceptions.py | 异常 |
| adapters.py   | _transports/   | 传输层 |
| utils.py      | _utils.py      | 工具 |


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

|             特点         |           说明           |
|-------------------------|--------------------------|
| `*` 开头                 | 强制关键字参数             |
| 包装类                   | Headers、Cookies、Timeout |
| `@property` + `@setter` | 读写时做处理               |
| 状态管理                 | ClientState 枚举          |
| 默认超时                 |  避免卡死                  |
| base_url                | 简化 API 调用              |

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

|   角色   |    作用    |              例子                     |
|---------|------------|--------------------------------------|
| 策略接口 | 定义"做什么" | `Translator`                         |
| 具体策略 | 实现"怎么做" | `OllamaTranslator`、`DeepLTranslator` |
| 上下文   | 使用策略    | `translate_srt`                       |

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

|     优点     |        说明       |
|-------------|-------------------|
| 符合开闭原则  | 加新策略不用改旧代码 |
| 易测试       | 每个策略独立测.     |
| 易维护       | 每个策略短小        |
| 灵活         | 运行时切换策略      |
| 消除 if/else | 代码更清晰         |

### 缺点

| 缺点           | 说明               |
|---------------|--------------------|
| 类变多         | 每个策略一个类 -------|
| 简单场景过度设计 | 只有 1 个策略时没必要 |


## 六点五、工厂模式

### 是什么

把"创建对象"的逻辑抽出来，放到一个"工厂"里。
用户只告诉工厂"要什么"，工厂返回对象。

### 三个角色

|   角色.  | 作用          |                例子                    |
|---------|---------------|---------------------------------------|
| 产品接口 | 定义"产品是什么" | `Translator`                          |
| 具体产品 | 实现产品        | `OllamaTranslator`、`DeepLTranslator` |
| 工厂.   | 创建产品        | `create_translator`                   |

### 代码结构

    # 1. 产品接口（已有）
    class Translator:
        def translate(self, text): ...

    # 2. 具体产品（已有）
    class OllamaTranslator(Translator): ...
    class DeepLTranslator(Translator): ...

    # 3. 工厂
    def create_translator(name: str, config: dict) -> Translator:
        if name == "ollama":
            ollama = config["ollama"]
            return OllamaTranslator(
                model=ollama["model"],
                url=ollama["url"],
                timeout=ollama["timeout"],
                max_retries=ollama["max_retries"],
                retry_delay=ollama["retry_delay"],
            )
        elif name == "deepl":
            deepl = config.get("deepl", {})
            return DeepLTranslator(
                api_key=deepl.get("api_key", ""),
                url=deepl.get("url", "https://api-free.deepl.com/v2/translate"),
            )
        else:
            raise ValueError(f"未知翻译器: {name}")

### 用法

    translator = create_translator("ollama", config)
    result = translator.translate("Hello")

    # 换成 DeepL
    translator = create_translator("deepl", config)
    result = translator.translate("Hello")

### 工厂模式 vs if/else

| 维度      | if/else     | 工厂模式.    |
|-----------|-------------|------------|
| 创建逻辑   | 分散         | 集中        |
| 加新翻译器 | 改多处        | 改工厂.     |
| 测试      | 要 mock 多个  | 工厂独立测   |
| 可读性     | `main.py` 长 | `main.py` 短|

### 优点

| 优点        | 说明                     |
|------------|--------------------------|
| 集中创建逻辑 | 不在 `main.py` 里 if/else |
| 符合开闭原则 | 加新翻译器只改工厂          |
| 易测试      | 工厂独立测                 |
| 用户简单.    | 只传名字                   |

### 缺点

| 缺点         |       说明           |
|-------------|----------------------|
| 多一层抽象    | 简单的场景不必要        |
| 工厂可能变复杂 | 翻译器多时 if/else 长 |

### 对照 httpx

httpx 的 `Client.__init__`：

    class Client(BaseClient):
        def __init__(self, transport=None):
            if transport is None:
                transport = HTTPTransport()   # 默认工厂
            self._transport = transport

你的 `create_translator`：

    def create_translator(name, config):
        if name == "ollama":
            return OllamaTranslator(...)
        elif name == "deepl":
            return DeepLTranslator(...)
        else:
            raise ValueError(...)

一样的思路：根据条件创建对象。


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
    │       ├── deepl.py        ← DeepLTranslator
    │       └── factory.py      ← create_translator
    ├── tests/
    │   ├── __init__.py
    │   ├── conftest.py
    │   ├── test_parse.py
    │   ├── test_merge.py
    │   ├── test_translate.py
    │   └── test_factory.py     ← 新增
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

### `factory.py`

    """翻译器工厂"""
    from .base import Translator
    from .deepl import DeepLTranslator
    from .ollama import OllamaTranslator


    def create_translator(name: str, config: dict) -> Translator:
        """根据名字创建翻译器

        Args:
            name: 翻译器名字（"ollama" 或 "deepl"）
            config: 配置字典

        Returns:
            Translator 实例

        Raises:
            ValueError: 未知翻译器名字
        """
        if name == "ollama":
            ollama = config["ollama"]
            return OllamaTranslator(
                model=ollama["model"],
                url=ollama["url"],
                timeout=ollama["timeout"],
                max_retries=ollama["max_retries"],
                retry_delay=ollama["retry_delay"],
            )
        elif name == "deepl":
            deepl = config.get("deepl", {})
            return DeepLTranslator(
                api_key=deepl.get("api_key", ""),
                url=deepl.get("url", "https://api-free.deepl.com/v2/translate"),
            )
        else:
            raise ValueError(f"未知翻译器: {name}")

### `translators/__init__.py`

    """翻译器模块"""
    from .base import Translator
    from .deepl import DeepLTranslator
    from .factory import create_translator
    from .ollama import OllamaTranslator

    __all__ = [
        "Translator",
        "OllamaTranslator",
        "DeepLTranslator",
        "create_translator",
    ]

### `config.yaml`

    ollama:
      url: "http://localhost:11434/api/generate"
      model: "qwen2.5:7b"
      timeout: 120
      max_retries: 3
      retry_delay: 2

    deepl:
      api_key: ""
      url: "https://api-free.deepl.com/v2/translate"

    translation:
      target_language: "Chinese"
      temperature: 0.3

    output:
      suffix: ".zh"

**注意**：代码用了 `config["ollama"]` 和 `config["deepl"]`，配置里要有这两段。

### `main.py` 的关键改动

    from subtitle_tool.translators import create_translator

    def translate_srt(input_file, output_file, config):
        ...
        translator = create_translator("ollama", config)
        ...

### `test_factory.py`

    """测试翻译器工厂"""
    import pytest

    from subtitle_tool.translators import (
        DeepLTranslator,
        OllamaTranslator,
        create_translator,
    )


    def test_create_ollama():
        """测试创建的 ollama 翻译器"""
        config = {
            "ollama": {
                "model": "qwen2.5:7b",
                "url": "http://localhost:11434/api/generate",
                "timeout": 120,
                "max_retries": 3,
                "retry_delay": 2,
            }
        }
        translator = create_translator("ollama", config)
        assert isinstance(translator, OllamaTranslator)
        assert translator.model == "qwen2.5:7b"


    def test_create_deepl():
        """测试创建的 deepl 翻译器"""
        config = {
            "deepl": {
                "api_key": "test-key",
                "url": "https://api-free.deepl.com/v2/translate",
            }
        }
        translator = create_translator("deepl", config)
        assert isinstance(translator, DeepLTranslator)
        assert translator.api_key == "test-key"


    def test_create_unknown():
        """测试未知翻译器"""
        config = {}
        with pytest.raises(ValueError, match="未知翻译器"):
            create_translator("unknown", config)


    def test_create_deepl_without_config():
        """测试没配 deepl 时用默认值"""
        config = {}
        translator = create_translator("deepl", config)
        assert isinstance(translator, DeepLTranslator)
        assert translator.api_key == ""


## 八、对照 httpx

|             httpx                 | subtitle_tool                    |
|-----------------------------------|----------------------------------|
| `_transports/`                    | `translators/`                   |
| `base.py` 的 `BaseTransport`      | `base.py` 的 `Translator`         |
| `default.py` 的 `HTTPTransport`   | `ollama.py` 的 `OllamaTranslator` |
| `mock.py` 的 `MockTransport`      | `deepl.py` 的 `DeepLTranslator`   |
| `__init__.py`                     | `__init__.py`                    |
| `Client.__init__` 的默认 transport | `create_translator`              |


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

|                       问题                           | 怎么解决的 |
|-----------------------------------------------------|-----------|
| 方法名写成 `translate_text`                           | 改成 `translate` |
| `@patch` 路径多了一个点                                | 改成 `translators.ollama` |
| `ImportError: cannot import name 'OllamaTranslator'` | 写 `translators/__init__.py` |
| mypy 报 `json=payload` 类型错                         | 加 `payload: dict[str, Any]` |
| mypy 报 `proxies` 类型错                              | 加 `# type: ignore[dict-item]` |
| CI 失败：`ollama.py` 没格式化                          | 本地跑 `black .` 再 push |
| `config.yaml` 没加 deepl 段                           | 加 deepl 段，工厂用 .get() |
| 工厂报 KeyError                                       | 用 config.get("deepl", {}) |


## 十一、跑过的命令

    # 创建目录和文件
    mkdir -p subtitle_tool/translators
    touch subtitle_tool/translators/__init__.py
    touch subtitle_tool/translators/base.py
    touch subtitle_tool/translators/ollama.py
    touch subtitle_tool/translators/deepl.py
    touch subtitle_tool/translators/factory.py

    # 删旧文件
    rm subtitle_tool/translate.py

    # 验证导入
    python3 -c "from subtitle_tool.translators import Translator, OllamaTranslator, DeepLTranslator, create_translator; print('OK')"

    # 验证工厂
    python3 -c "from subtitle_tool.translators import create_translator; from subtitle_tool.config import load_config; config = load_config(); t = create_translator('ollama', config); print(type(t).__name__)"

    # 跑检查
    black .
    flake8 .
    mypy subtitle_tool/
    python3 -m pytest tests/ -v

    # 提交
    git add .
    git commit -m "Refactor: 用策略模式重构翻译模块"
    git push

    git add .
    git commit -m "Add: 工厂模式翻译器"
    git push


## 十二、第 5 周学到的核心概念

| 概念 | 说明 |
|------|------|
| 策略模式 | 同一件事多种做法 |
| 工厂模式 | 根据条件创建对象 |
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
| 集中创建逻辑 | 不在 main.py 里 if/else |
| `.get()` 避免 KeyError | 配置可能缺失 |
| 配置和代码要一致 | 代码用 config["deepl"]，配置里要有 |


## 十三、一句话总结第 5 周

第 5 周 = 学设计模式（策略模式 + 工厂模式），重构 subtitle_tool。
核心：抽象基类 + 多实现 + 工厂创建，让代码更灵活。
对照：httpx 的 `_transports/` 就是策略模式。


## 十四、明天早上复习重点

1. **策略模式的三个角色**：接口、具体策略、上下文。
2. **工厂模式的三个角色**：产品接口、具体产品、工厂。
3. **策略模式 vs if/else**：每个策略一个类。
4. **工厂模式 vs if/else**：集中 vs 分散。
5. **为什么用 `self.xxx`**：持久化，每个实例独立。
6. **`@patch` 路径怎么写**：被测模块里看到的路径。
7. **mypy 类型注解**：`dict[str, Any]`、`# type: ignore`。
8. **对照 httpx**：`_transports/` vs `translators/`。
9. **配置和代码一致**：代码用 `config["deepl"]`，配置里要有。
10. **CI 通过的条件**：black、flake8、mypy、pytest 全通过。