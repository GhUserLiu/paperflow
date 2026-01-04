# 虚拟环境设置指南

本文档介绍如何为 arxiv-zotero-auto 项目设置 Python 虚拟环境。

## 🎯 为什么要使用虚拟环境?

虚拟环境为每个项目创建独立的 Python 环境,避免不同项目之间的依赖冲突。

**优点**:
- ✅ 依赖隔离,不同项目使用不同版本的包
- ✅ 保持全局 Python 环境干净
- ✅ 易于复现和分享
- ✅ 不需要管理员权限

## 🚀 快速开始

### Windows 用户

```bash
# 1. 进入项目目录
cd C:\Users\liuzh\Desktop\Projects\arxiv-zotero-auto

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
venv\Scripts\activate

# 4. 升级 pip (可选但推荐)
python -m pip install --upgrade pip

# 5. 安装项目依赖
pip install -r requirements.txt

# 6. 以可编辑模式安装项目
pip install -e .

# 7. 配置环境变量
# 复制示例文件
copy .env.example .env
# 然后编辑 .env 文件,填入你的凭证
```

### Linux / macOS 用户

```bash
# 1. 进入项目目录
cd ~/Projects/arxiv-zotero-auto

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 升级 pip (可选但推荐)
python -m pip install --upgrade pip

# 5. 安装项目依赖
pip install -r requirements.txt

# 6. 以可编辑模式安装项目
pip install -e .

# 7. 配置环境变量
# 复制示例文件
cp .env.example .env
# 然后编辑 .env 文件,填入你的凭证
nano .env  # 或使用你喜欢的编辑器
```

## 📝 虚拟环境使用

### 激活虚拟环境

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

激活后,命令行提示符会显示虚拟环境名称:
```bash
(venv) C:\Users\liuzh\Desktop\Projects\arxiv-zotero-auto>
```

### 验证虚拟环境

```bash
# 检查 Python 路径
(venv) where python   # Windows
(venv) which python   # Linux/macOS

# 应该显示虚拟环境中的 Python,例如:
# C:\Users\liuzh\Desktop\Projects\arxiv-zotero-auto\venv\Scripts\python.exe

# 检查已安装的包
(venv) pip list

# 应该只显示虚拟环境中安装的包
```

### 运行项目

```bash
# 运行主采集脚本
(venv) python scripts/auto_collect.py

# 或使用模块方式
(venv) python -m arxiv_zotero.cli --help

# 运行测试
(venv) python -m pytest tests/
```

### 退出虚拟环境

```bash
(venv) deactivate
```

## 🗑️ 删除虚拟环境

如果需要重新创建或删除虚拟环境:

```bash
# 1. 先退出虚拟环境
deactivate

# 2. 删除虚拟环境目录
# Windows:
rmdir /s /q venv

# Linux/macOS:
rm -rf venv

# 3. 重新创建(按照上面的步骤)
python -m venv venv
```

## 📦 requirements.txt 说明

`requirements.txt` 包含项目所需的所有 Python 包:

```txt
arxiv>=2.0.0              # arXiv API 客户端
pyzotero>=1.5.0          # Zotero API 客户端
requests>=2.31.0         # HTTP 请求库
pytz>=2023.3             # 时区处理
python-dotenv>=1.0.0     # 环境变量管理
aiohttp>=3.9.0           # 异步 HTTP
pyyaml>=6.0              # YAML 配置文件
PyPDF2>=3.0.0            # PDF 处理
google-generativeai>=0.3.0  # AI 摘要(可选)
```

### 安装特定版本

如果需要安装特定版本的包:

```bash
# 安装特定版本
pip install arxiv==2.0.0

# 升级包
pip install --upgrade arxiv

# 查看包信息
pip show arxiv
```

## 🔧 常见问题

### 问题 1: 找不到 python 命令

**解决方案**:
```bash
# 使用 python3
python3 -m venv venv

# 或使用完整路径
C:\Python311\python.exe -m venv venv
```

### 问题 2: 激活脚本被杀毒软件拦截

**解决方案**:
- 将项目目录添加到杀毒软件白名单
- 或使用 `PowerShell`:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  venv\Scripts\Activate.ps1
  ```

### 问题 3: pip 安装失败

**解决方案**:
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 4: 权限错误

**解决方案**:
```bash
# 确保使用虚拟环境,不需要管理员权限
# 不要使用 sudo 或管理员权限
# 如果仍然出错,检查虚拟环境是否正确激活
which python  # 应该指向 venv 目录
```

## 💡 最佳实践

1. **每个项目使用独立的虚拟环境**
   ```bash
   # ✅ 好的做法
   project1/venv/
   project2/venv/

   # ❌ 不好的做法
   shared_venv/
   ```

2. **将虚拟环境目录加入 .gitignore**
   ```gitignore
   venv/
   .venv/
   ```

3. **保持 requirements.txt 更新**
   ```bash
   # 添加新包后更新
   pip freeze > requirements.txt

   # 或使用 pip-tools (高级)
   pip install pip-tools
   pip-compile requirements.in
   ```

4. **使用 .env.example 模板**
   ```bash
   # ✅ 好的做法
   .env.example    # 提交到 Git
   .env            # 不提交,包含真实凭证

   # ❌ 不好的做法
   .env            # 包含 API Key,被提交到 Git
   ```

5. **文档化你的环境**
   ```bash
   # 在 README.md 中说明
   # Python 版本要求
   Python 3.7+

   # 依赖说明
   pip install -r requirements.txt
   ```

## 🎓 进阶:使用 conda (可选)

如果你更喜欢使用 conda:

```bash
# 创建 conda 环境
conda create -n arxiv-zotero python=3.11

# 激活环境
conda activate arxiv-zotero

# 安装依赖
pip install -r requirements.txt

# 退出环境
conda deactivate
```

**注意**: 本项目不需要 conda,pip 虚拟环境已足够。

## 📚 更多资源

- [Python 虚拟环境官方文档](https://docs.python.org/3/library/venv.html)
- [pip 用户指南](https://pip.pypa.io/en/stable/user_guide/)
- [Python 打包指南](https://packaging.python.org/)

---

**最后更新**: 2026-01-04
