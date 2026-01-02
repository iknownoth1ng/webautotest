#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  run_tests.py
@Time    :  2025/12/31 23:10:18
@Author  :  owl
@Desp    : 简化版测试运行器，使用logger
"""

import argparse
import subprocess
import sys

from configs.path import REPORTS_DIR


def main():
    from src.core.logger import logger  # 延迟导入以避免不必要的依赖

    parser = argparse.ArgumentParser(description="Web自动化测试执行脚本")

    parser.add_argument(
        "--env",
        default="test",
        choices=["dev", "test", "prod"],
        help="测试环境: dev, test, prod",
    )

    parser.add_argument(
        "--browser",
        default="chrome",
        choices=["chrome", "firefox", "edge"],
        help="浏览器类型: chrome, firefox, edge",
    )

    parser.add_argument("--headless", action="store_true", help="是否使用无头模式运行")

    # pytest-timeout插件
    parser.add_argument("--timeout", type=int, default=30, help="超时时间（秒）")

    # pytest-xdist插件
    parser.add_argument("--concurrency", type=int, default=1, help="并发执行数")

    # pytest-rerunfailures插件
    parser.add_argument("--reruns", type=int, default=0, help="失败重跑次数")

    parser.add_argument(
        "--record-video",
        action="store_true",
        help="是否录制视频（只运行标记为video的用例）",
        default=True,
    )

    # parser.add_argument(
    #     "--load_env",
    #     action="store_true",
    #     help="是否从 .env 文件加载环境变量（生产环境建议通过其他方式设置）",
    # )

    parser.add_argument(
        "test_path", nargs="?", default="tests/", help="测试路径（默认: tests/）"
    )

    args = parser.parse_args()

    logger.info("开始执行测试")
    logger.info(f"测试路径: {args.test_path}")

    # # 根据参数决定是否加载 .env 文件
    # if args.load_env:
    #     # 检查并加载 .env 文件
    #     env_file = Path(".env")
    #     if env_file.exists():
    #         from dotenv import load_dotenv

    #         load_dotenv()
    #         logger.info(f"已从 {env_file.absolute()} 加载环境变量")
    #     else:
    #         logger.warning(f".env 文件不存在于 {env_file.absolute()}")

    # 构建pytest命令
    cmd = [sys.executable, "-m", "pytest", args.test_path]

    # 添加参数
    cmd.extend(["--env", args.env])
    cmd.extend(["--browser", args.browser])

    if args.headless:
        cmd.append("--headless")

    if args.concurrency > 1:
        cmd.extend(["-n", str(args.concurrency)])

    if args.reruns > 0:
        cmd.extend(["--reruns", str(args.reruns), "--reruns-delay", "2"])

    if args.record_video:
        cmd.append("--record-video")

    if args.timeout:
        # 设置pytest-timeout插件的超时时间
        cmd.extend(["--timeout", str(args.timeout)])

    # 添加详细输出
    cmd.extend(["-v", "-s"])

    # 执行测试
    logger.info(f"执行命令: {' '.join(cmd)}")
    logger.info(f"当前环境: {args.env}")
    logger.info(f"当前浏览器: {args.browser}")

    try:
        result = subprocess.run(cmd)
        logger.info(f"测试执行完成，返回码: {result.returncode}")

        # 如果测试成功，启动 Allure 报告
        if result.returncode != 0:
            import shutil
            import time

            logger.info("启动 Allure 报告服务")
            allure_path = shutil.which("allure")
            if allure_path:
                try:
                    # 启动 allure serve
                    subprocess.Popen(
                        [
                            allure_path,
                            "serve",
                            str(REPORTS_DIR / "allure-results"),
                        ]
                    )
                    time.sleep(3)  # 等待服务启动
                except Exception as e:
                    logger.error(f"启动 Allure 失败: {e}")
            else:
                logger.warning(
                    "Allure CLI 未找到，请确保已安装并添加到 PATH，或手动运行: allure serve ./reports/allure-results"
                )

        # sys.exit(result.returncode)
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(130)
    except Exception as e:
        logger.error(f"执行测试时发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
