# WebAutoTest 框架的 AI 编码助手指令

## 架构概述

这是一个基于 Selenium 的 JPress CMS Web 自动化测试框架，使用 Python 的页面对象模型 (POM)。关键组件：

-   **核心**：带有日志记录的 BasePage、用于线程安全浏览器实例的 WebDriverManager、用于定位器策略的 ElementLocator
-   **页面**：继承 BasePage 的页面对象（例如 AdminLoginPage），带有元素交互
-   **组件**：可重用的 UI 组件（头部、底部、导航）
-   **工具**：Allure 报告、视频录制 (OpenCV)、验证码识别 (ddddocr)、数据处理
-   **测试**：带有环境设置、驱动管理、视频录制固件的 Pytest

## 关键工作流程

-   **设置环境**：运行 `docker-compose -f docker-compose-jpress.yml up -d` 以启动 JPress 应用和 MySQL
-   **运行测试**：使用 `python run_tests.py --env dev --browser chrome`（支持 --headless、--concurrency、--reruns、--record-video）；内部使用 `sys.executable -m pytest` 确保虚拟环境中的 pytest
-   **分布式测试**：运行 `docker-compose -f docker-compose-grid.yml up -d` 以启动 Selenium Grid，然后使用 `--env test` 运行
-   **报告**：Allure 结果在 `reports/allure-results/` 中，使用 `allure serve reports/allure-results` 生成 HTML；测试成功后自动启动 Allure 服务（需要安装 Allure CLI 并添加到 PATH）
-   **调试**：视频自动录制到 `reports/videos/`，失败时截图；Grid 模式下标记的用例视频自动附加到 Allure 报告

## 项目特定约定

-   **定位器**：使用 `element_locator.py` 中的 `name()`、`xpath()`、`id()` 而不是原始元组（例如 `username_input = name("user")`）
-   **日志记录**：所有操作通过 BasePage 方法中的 `self.logger.log_action("action", details)` 记录
-   **配置**：通过 `config`（来自 YAML 的 AttrDict）访问，环境特定（dev/test/prod 通过 `ENV` 变量设置）
-   **固件**：`driver`（类作用域）、`admin_login`（预登录管理员页面）、`video_recorder`（自动附加到 Allure）
-   **数据加载**：YAML/JSON/CSV 在 `tests/data/` 中，使用 `data_utils.py` 加载
-   **验证码处理**：在登录流程中使用带有 OCR 的 CaptchaRecognizer 处理文本验证码
-   **视频录制**：通过 `config.webdriver.record_video` 配置，结合 `@pytest.mark.video` 标记控制（标记的用例录制，未标记的不录制）；Grid 模式下视频自动附加到 Allure 报告

## 示例

-   **页面方法**：`def input_username(self, username): self.input_text(self.username_input, username)`
-   **测试结构**：使用 `@allure.feature`、`@allure.title`、`with allure.step("step"):` 进行报告
-   **定位器使用**：`submit_btn = xpath("//button[@type='submit']")`
-   **配置访问**：`config.base_url`、`config.users.admin.username`

## 集成点

-   **Docker**：应用在容器中，持久化卷（`docker_volumes/`）
-   **Selenium Grid**：用于测试环境中的并行/分布式执行
-   **Allure**：自动报告生成，附加视频/截图
-   **视频录制**：BrowserVideoRecorder 捕获测试会话以进行调试；Grid 模式下标记用例的视频自动附加到 Allure 报告</content>
    <parameter name="filePath">d:\workspace\vsworkspace\webautotest\.github\copilot-instructions.md
