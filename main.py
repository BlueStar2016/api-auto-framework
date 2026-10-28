import sys
import pytest

if __name__ == "__main__":
    # 可以通过命令行参数传递环境
    # python run_tests.py --env=test
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    # 默认参数
    default_args = [
        "-v",  # 详细输出
        "--html=reports/report.html",  # HTML 报告
        "--self-contained-html",  # 独立 HTML
        "--maxfail=5",  # 失败 5 次后停止
        "-n", "2",  # 并行执行（需安装 pytest-xdist）
        "tests/"  # 测试目录
    ]

    final_args = default_args + args

    # 运行 pytest
    exit_code = pytest.main(final_args)
    sys.exit(exit_code)