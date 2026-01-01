# webui 自动化框架

## 目录结构

webautotest/ # 项目根目录
│
├── configs/ # 配置文件目录
│ ├── **init**.py
│ ├── config.py # 基础配置
│ ├── config.yaml # 环境配置
│
├── drivers/ # 浏览器驱动目录
│ ├── chromedriver.exe # Chrome 驱动 (Windows)
│ ├── chromedriver # Chrome 驱动 (Linux/Mac)
│ └── geckodriver # Firefox 驱动
│
├── logs/ # 日志目录
│ └── .gitkeep # 保持空目录
│
├── reports/ # 测试报告目录
│ ├── allure/ # Allure 原始数据
│ ├── html/ # HTML 报告
│ └── screenshots/ # 截图目录
│
├── src/ # 源代码目录
│ │
│ ├── core/ # 核心模块
│ │ ├── **init**.py
│ │ ├── base_page.py # 基础页面类
│ │ ├── webdriver_manager.py # 浏览器管理
│ │ ├── element_locator.py # 元素定位器封装
│ │ ├── wait_conditions.py # 等待条件封装
│ │ └── logger.py # 日志模块
│ │
│ ├── pages/ # 页面对象层 (POM 核心)
│ │ ├── **init**.py
│ │ ├── base_page.py # 页面基类
│ │ ├── login_page.py # 登录页面
│ │ ├── home_page.py # 主页
│ │ ├── cart_page.py # 购物车页面
│ │ └── checkout_page.py # 结算页面
│ │
│ ├── components/ # 公共组件
│ │ ├── **init**.py
│ │ ├── header.py # 头部组件
│ │ ├── footer.py # 底部组件
│ │ ├── navigation.py # 导航组件
│ │ └── modal_dialog.py # 模态框组件
│ │
│ ├── utils/ # 工具类
│ │ ├── **init**.py
│ │ ├── file_utils.py # 文件操作
│ │ ├── data_utils.py # 数据处理
│ │ ├── date_utils.py # 日期处理
│ │ └── allure_utils.py # Allure 工具
│ │
│ └── api/ # API 相关（可选）
│ ├── **init**.py
│ └── auth_api.py # 认证 API
│
├── tests/ # 测试用例目录
│ │
│ ├── conftest.py # Pytest 共享 fixture
│ │
│ ├── test_suites/ # 测试套件
│ │ ├── **init**.py
│ │ ├── smoke/ # 冒烟测试
│ │ │ ├── **init**.py
│ │ │ └── test_smoke_login.py
│ │ │
│ │ ├── regression/ # 回归测试
│ │ │ └── **init**.py
│ │ │
│ │ └── e2e/ # 端到端测试
│ │ └── **init**.py
│ │
│ ├── test_cases/ # 按功能模块划分
│ │ ├── **init**.py
│ │ ├── test_login.py # 登录测试
│ │ ├── test_product.py # 商品测试
│ │ ├── test_cart.py # 购物车测试
│ │ └── test_checkout.py # 结算测试
│ │
│ └── data/ # 测试数据
│ ├── **init**.py
│ ├── test_data.json # JSON 测试数据
│ ├── test_data.yaml # YAML 测试数据
│ ├── login_data.csv # CSV 测试数据
│ └── sql_scripts/ # SQL 脚本
│ └── setup_data.sql
│
├── .env.example # 环境变量示例
├── .gitignore # Git 忽略文件
├── .pylintrc # Pylint 配置
├── pytest.ini # Pytest 配置
├── requirements.txt # 依赖包列表
├── README.md # 项目说明
├── run_tests.py # 测试运行脚本
└── setup.cfg # 项目配置

## 遇到的问题

1. allure 报告中，网页 mp4 视频无法播放，需要更换编码器
2. selenium4 启动浏览器驱动，不需要再指定路径，会自己下载
3. 分布式网络问题，vnc 密码 secret
