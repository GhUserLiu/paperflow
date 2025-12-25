#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化管理脚本 | Automation Management Script

管理内容：
1. 环境创建和配置
2. 依赖安装和更新
3. 数据下载和处理
4. 测试和验证
5. 文档生成
6. 部署和发布

Usage:
    python automation.py --help
    python automation.py setup
    python automation.py test
    python automation.py install
"""

import argparse
import subprocess
import sys
from pathlib import Path
import shutil
import json
from datetime import datetime
import io

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class Colors:
    """终端颜色代码"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(text):
    """打印成功消息"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """打印错误消息"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text):
    """打印警告消息"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text):
    """打印信息"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def run_command(command, description=None, check=True):
    """运行命令并显示输出"""
    if description:
        print_info(description)

    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )

        if result.stdout:
            print(result.stdout)

        return result.returncode == 0

    except subprocess.CalledProcessError as e:
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print_error(e.stderr)
        return False


class ProjectManager:
    """项目管理器"""

    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent
        self.venv_path = self.project_root / 'venv'
        self.requirements_file = self.project_root / 'requirements.txt'

    def setup_environment(self, python_version='python3'):
        """1. 环境创建和配置"""
        print_header("环境设置 | Environment Setup")

        # 检查是否已存在虚拟环境
        if self.venv_path.exists():
            print_warning("虚拟环境已存在 | Virtual environment already exists")
            response = input("是否重新创建？| Recreate? (y/N): ")
            if response.lower() != 'y':
                print_info("跳过环境创建 | Skipping environment creation")
                return True

            print_info("删除旧的虚拟环境 | Removing old virtual environment...")
            shutil.rmtree(self.venv_path)

        # 创建虚拟环境
        print_info("创建虚拟环境 | Creating virtual environment...")
        if not run_command(f"{python_version} -m venv venv", "创建虚拟环境"):
            print_error("虚拟环境创建失败 | Failed to create virtual environment")
            return False

        print_success("虚拟环境创建成功 | Virtual environment created")

        # 创建必要的目录
        directories = ['logs', 'output', 'config']
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
            print_success(f"创建目录 | Created directory: {directory}/")

        # 检查 .env 文件
        env_file = self.project_root / '.env'
        env_example = self.project_root / 'config' / '.env.example'

        if not env_file.exists() and env_example.exists():
            print_info("复制 .env.example 到 .env | Copying .env.example to .env")
            shutil.copy(env_example, env_file)
            print_warning("请编辑 .env 文件添加你的凭证 | Please edit .env file with your credentials")

        print_success("环境设置完成 | Environment setup completed")
        return True

    def install_dependencies(self, upgrade=False):
        """2. 依赖安装和更新"""
        print_header("依赖管理 | Dependency Management")

        if not self.venv_path.exists():
            print_error("虚拟环境不存在 | Virtual environment not found")
            print_info("请先运行: python automation.py setup")
            return False

        # 确定pip命令
        if sys.platform == 'win32':
            pip_cmd = self.venv_path / 'Scripts' / 'pip'
        else:
            pip_cmd = self.venv_path / 'bin' / 'pip'

        # 升级 pip
        print_info("升级 pip | Upgrading pip...")
        run_command(f"{pip_cmd} install --upgrade pip")

        # 安装依赖
        if upgrade:
            print_info("更新所有依赖 | Updating all dependencies...")
            command = f"{pip_cmd} install --upgrade -r {self.requirements_file}"
        else:
            print_info("安装依赖 | Installing dependencies...")
            command = f"{pip_cmd} install -r {self.requirements_file}"

        if run_command(command):
            print_success("依赖安装完成 | Dependencies installed")
            return True
        else:
            print_error("依赖安装失败 | Failed to install dependencies")
            return False

    def download_data(self):
        """3. 数据下载和处理"""
        print_header("数据管理 | Data Management")

        print_info("此功能用于下载测试数据 | This feature downloads test data")
        print_info("当前项目无需额外数据下载 | No additional data download needed")

        # 显示日志文件信息
        log_file = self.project_root / 'logs' / 'arxiv_zotero.log'
        if log_file.exists():
            size = log_file.stat().st_size / 1024  # KB
            print_info(f"日志文件大小 | Log file size: {size:.2f} KB")
        else:
            print_warning("日志文件不存在 | Log file not found")

        return True

    def run_tests(self, verbose=False):
        """4. 测试和验证"""
        print_header("测试运行 | Running Tests")

        if not self.venv_path.exists():
            print_error("虚拟环境不存在 | Virtual environment not found")
            return False

        # 确定pytest命令
        if sys.platform == 'win32':
            pytest_cmd = self.venv_path / 'Scripts' / 'pytest'
        else:
            pytest_cmd = self.venv_path / 'bin' / 'pytest'

        verbose_flag = '-v' if verbose else ''

        # 运行测试
        print_info("运行单元测试 | Running unit tests...")
        success = run_command(
            f"{pytest_cmd} tests/ {verbose_flag}",
            check=False
        )

        if success:
            print_success("所有测试通过 | All tests passed")
        else:
            print_warning("某些测试失败 | Some tests failed")

        return success

    def generate_docs(self):
        """5. 文档生成"""
        print_header("文档生成 | Documentation Generation")

        print_info("检查文档文件 | Checking documentation files...")

        docs = {
            'README.md': '主文档 | Main documentation',
            'docs/PROJECT_STRUCTURE.md': '项目结构 | Project structure',
            'docs/api-docs.md': 'API 文档 | API documentation',
        }

        for doc_file, description in docs.items():
            doc_path = self.project_root / doc_file
            if doc_path.exists():
                print_success(f"✓ {description}: {doc_file}")
            else:
                print_warning(f"✗ 缺失 | Missing: {doc_file}")

        print_info("\n文档统计 | Documentation statistics:")
        md_files = list(self.project_root.rglob('*.md'))
        print(f"  总计 Markdown 文件 | Total Markdown files: {len(md_files)}")

        return True

    def deploy_release(self, dry_run=False):
        """6. 部署和发布"""
        print_header("部署准备 | Deployment Preparation")

        if dry_run:
            print_info("模拟运行 | Dry run mode")

        # 检查 Git 状态
        print_info("检查 Git 状态 | Checking Git status...")
        run_command("git status --short", "Git 状态:", check=False)

        # 检查最新提交
        print_info("\n最新提交 | Latest commit:")
        run_command("git log -1 --oneline", check=False)

        # 运行测试
        print_info("\n运行测试套件 | Running test suite...")
        if not self.run_tests(verbose=False):
            print_error("测试失败，取消部署 | Tests failed, cancelling deployment")
            return False

        if dry_run:
            print_warning("模拟模式：不执行实际部署 | Dry run: not actually deploying")
            return True

        # 构建包
        print_info("构建发布包 | Building release package...")
        if run_command("python setup.py sdist bdist_wheel", check=False):
            print_success("构建完成 | Build completed")

            # 显示生成的文件
            dist_dir = self.project_root / 'dist'
            if dist_dir.exists():
                print_info("生成的文件 | Generated files:")
                for file in dist_dir.iterdir():
                    print(f"  - {file.name}")
            return True
        else:
            print_error("构建失败 | Build failed")
            return False

    def clean(self, all=False):
        """清理项目"""
        print_header("项目清理 | Project Cleanup")

        # 清理 Python 缓存
        patterns = ['__pycache__', '*.pyc', '*.pyo']
        for pattern in patterns:
            if '*' in pattern:
                for file in self.project_root.rglob(pattern.split('*')[1]):
                    if file.is_file():
                        file.unlink()
                        print_success(f"删除 | Deleted: {file}")
            else:
                for dir_path in self.project_root.rglob(pattern):
                    if dir_path.is_dir():
                        shutil.rmtree(dir_path)
                        print_success(f"删除 | Deleted: {dir_path}")

        # 清理构建目录
        build_dirs = ['build', 'dist', '*.egg-info']
        for dir_name in build_dirs:
            if '*' in dir_name:
                for path in self.project_root.glob(dir_name):
                    if path.is_dir():
                        shutil.rmtree(path)
                        print_success(f"删除 | Deleted: {path}")
            else:
                path = self.project_root / dir_name
                if path.exists():
                    shutil.rmtree(path)
                    print_success(f"删除 | Deleted: {dir_name}/")

        if all:
            # 清理虚拟环境
            if self.venv_path.exists():
                print_warning("删除虚拟环境 | Removing virtual environment...")
                shutil.rmtree(self.venv_path)
                print_success(f"删除 | Deleted: venv/")

            # 清理日志
            log_dir = self.project_root / 'logs'
            if log_dir.exists():
                for log_file in log_dir.glob('*.log'):
                    log_file.unlink()
                    print_success(f"删除 | Deleted: {log_file}")

        print_success("清理完成 | Cleanup completed")
        return True

    def info(self):
        """显示项目信息"""
        print_header("项目信息 | Project Information")

        print(f"项目根目录 | Project root: {self.project_root}")
        print(f"Python 版本 | Python version: {sys.version.split()[0]}")
        print(f"操作系统 | OS: {sys.platform}")

        # 虚拟环境状态
        if self.venv_path.exists():
            print_success("虚拟环境 | Virtual environment: 已安装 | Installed")
        else:
            print_warning("虚拟环境 | Virtual environment: 未安装 | Not installed")

        # Git 信息
        if (self.project_root / '.git').exists():
            run_command("git branch --show-current", "Git 分支 | Git branch:", check=False)
            run_command("git log -1 --format='%h - %s (%ar)'", "最新提交 | Latest commit:", check=False)
        else:
            print_warning("未初始化 Git 仓库 | Git repository not initialized")

        # 项目结构
        print_info("\n项目统计 | Project statistics:")
        print(f"  Python 文件 | Python files: {len(list(self.project_root.rglob('*.py')))}")
        print(f"  文档文件 | Markdown files: {len(list(self.project_root.rglob('*.md')))}")
        print(f"  测试文件 | Test files: {len(list((self.project_root / 'tests').rglob('test_*.py')))}")

        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='自动化管理脚本 | Automation Management Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例 | Examples:
  python automation.py setup              设置环境 | Setup environment
  python automation.py install            安装依赖 | Install dependencies
  python automation.py install --upgrade  更新依赖 | Update dependencies
  python automation.py test               运行测试 | Run tests
  python automation.py test -v            详细测试 | Verbose tests
  python automation.py docs               生成文档 | Generate documentation
  python automation.py deploy --dry-run   模拟部署 | Dry run deployment
  python automation.py clean              清理项目 | Clean project
  python automation.py info               显示信息 | Show information
        """
    )

    parser.add_argument('command', nargs='?',
                       choices=['setup', 'install', 'download', 'test', 'docs', 'deploy', 'clean', 'info'],
                       help='命令 | Command to execute',
                       default='info')

    parser.add_argument('--upgrade', action='store_true',
                       help='更新依赖 | Upgrade dependencies')

    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出 | Verbose output')

    parser.add_argument('--dry-run', action='store_true',
                       help='模拟运行 | Dry run mode')

    parser.add_argument('--all', action='store_true',
                       help='清理所有 | Clean everything (including venv)')

    parser.add_argument('--python-version', default='python3',
                       help='Python 版本 | Python version (default: python3)')

    args = parser.parse_args()

    # 创建项目管理器
    manager = ProjectManager()

    # 执行命令
    success = True

    if args.command == 'setup':
        success = manager.setup_environment(args.python_version)

    elif args.command == 'install':
        success = manager.install_dependencies(upgrade=args.upgrade)

    elif args.command == 'download':
        success = manager.download_data()

    elif args.command == 'test':
        success = manager.run_tests(verbose=args.verbose)

    elif args.command == 'docs':
        success = manager.generate_docs()

    elif args.command == 'deploy':
        success = manager.deploy_release(dry_run=args.dry_run)

    elif args.command == 'clean':
        success = manager.clean(all=args.all)

    elif args.command == 'info':
        success = manager.info()

    return 0 if success else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_warning("\n\n操作已取消 | Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print_error(f"错误 | Error: {e}")
        sys.exit(1)
