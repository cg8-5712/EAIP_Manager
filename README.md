# EAIP Manager - 航图数据包管理工具

**服务器端/开发人员工具**

用于创建、验证和管理加密的 AIPKG 航图数据包。

---

## 📦 功能

- ✅ **打包工具**：将航图目录打包成加密的 .aipkg 文件
- ✅ **验证工具**：验证 .aipkg 文件完整性
- ✅ **提取工具**：提取和查看包内容（需要密码）

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd EAIP_Manager
pip install -r requirements.txt
```

### 2. 打包航图数据

```bash
python scripts/build_aipkg.py <源目录> <输出文件>
```

**示例：**

```bash
python scripts/build_aipkg.py \
    "F:\航图数据\EAIP2025-07.V1.4\Terminal" \
    "../packages/eaip-2507.aipkg"
```

运行后会提示输入加密密码。

**重要：请妥善保管此密码，这是 Distribution Password！**

---

## 📝 详细使用

### 打包工具

#### 基本用法

```bash
python scripts/build_aipkg.py <源目录> <输出文件> [选项]
```

#### 参数说明

| 参数 | 说明 | 必需 |
|------|------|------|
| `源目录` | Terminal 目录路径 | ✅ |
| `输出文件` | 输出的 .aipkg 文件路径 | ✅ |
| `-v, --version` | EAIP 版本 | ❌ |
| `-p, --password` | 加密密码 | ❌ |
| `-c, --compression` | 压缩算法 (gzip/none) | ❌ |
| `-l, --level` | 压缩级别 (1-9) | ❌ |

#### 完整示例

```bash
# 最高压缩率
python scripts/build_aipkg.py \
    ./Terminal \
    ./packages/eaip-2507.aipkg \
    --version EAIP2025-07.V1.4 \
    --compression gzip \
    --level 9

# 禁用压缩（最快）
python scripts/build_aipkg.py \
    ./Terminal \
    ./packages/eaip-2507.aipkg \
    --compression none

# 调试模式
python scripts/build_aipkg.py \
    ./Terminal \
    ./packages/eaip-2507.aipkg \
    --log-level DEBUG
```

---

## 🔐 密码管理

### Distribution Password

这是打包时设置的密码，用于：
- 加密整个 .aipkg 文件
- 客户端解密时使用

**安全要求：**
- 最小长度：12 个字符
- 包含大小写字母
- 包含数字
- 包含特殊字符

**示例强密码：**
```
Aviation2025!@ComplexServerPassword#2507
```

### 密码存储

❌ **不要做：**
- 不要写在代码注释中
- 不要提交到 Git
- 不要发送明文邮件

✅ **应该做：**
- 使用密码管理器（1Password, LastPass）
- 团队内部加密文档
- 环境变量（生产环境）

---

## 📊 输出信息

打包成功后会显示：

```
============================================================
打包完成！
============================================================
输出文件: packages/eaip-2507.aipkg
EAIP 版本: EAIP2025-07.V1.4
文件总数: 3421
机场数量: 156
原始大小: 1024.00 MB
压缩后: 512.00 MB
最终大小: 520.00 MB
压缩率: 50.0%
总压缩率: 50.8%
============================================================
```

---

## 🗂️ 目录结构要求

源目录必须是 **Terminal** 目录，结构如下：

```
Terminal/                          ← 这个目录作为输入
├─ ZBAA/                          ← 机场 ICAO 代码（4个字符）
│  ├─ ADC/                        ← 航图分类
│  │  └─ ZBAA-1A-ADC.pdf
│  ├─ SID/
│  │  ├─ ZBAA-7A01-SID....pdf
│  │  └─ ...
│  ├─ STAR/
│  └─ ...
├─ ZBAD/
└─ ...
```

**支持的航图分类：**
- ADC（机场图）
- SID（标准仪表离场）
- STAR（标准终端进场）
- IAC（仪表进近图）
- GMC（地面移动图）
- AOC（航空器运行图）
- APDC（机场停机位图）
- PATC（精密进近地形图）
- FDA（最后下降区图）
- DATABASE CODING TABLE
- WAYPOINT LIST

---

## ⚙️ 高级配置

### 环境变量

创建 `.env` 文件：

```env
# 日志级别
LOG_LEVEL=INFO

# 默认压缩配置
DEFAULT_COMPRESSION=gzip
DEFAULT_COMPRESSION_LEVEL=6

# PBKDF2 迭代次数
DEFAULT_ENCRYPTION_ITERATIONS=100000
```

---

## 🔧 故障排查

### 问题 1：提示"密码过于简单"

**解决：** 使用��强的密码，满足所有安全要求。

### 问题 2：找不到源目录

**解决：** 检查路径是否正确，确保是 Terminal 目录。

```bash
# Windows
dir "F:\path\to\Terminal"

# Linux/macOS
ls "/path/to/Terminal"
```

应该看到一堆 4 个字母的文件夹（机场代码）。

### 问题 3：打包过程很慢

**解决：**
- 降低压缩级别（`--level 1`）
- 或禁用压缩（`--compression none`）

### 问题 4：打包后文件很大

**解决：**
- 提高压缩级别（`--level 9`）
- 检查是否有非 PDF 文件混入

---

## 📚 相关文档

- [航图加密方案详细设计](../EAIP_Viewer/docs/07-航图加密方案.md)
- [打包工具详细说明](./docs/README_AIPKG.md)

---

## 🤝 与查看器集成

打包完成后，将 `.aipkg` 文件分发给用户：

1. **服务器端（你）**：
   - 使用本工具打包
   - 记住 Distribution Password
   - 分发 .aipkg 文件

2. **客户端（用户）**：
   - 使用 EAIP_Viewer 打开
   - 无需知道 Distribution Password（硬编码在客户端）
   - 使用用户账号密码登录

---

## 🔒 安全注意事项

1. **Distribution Password 保密**
   - 只有开发人员知道
   - 硬编码在 EAIP_Viewer 中（混淆保护）

2. **源文件保护**
   - 打包后可以删除原始 Terminal 目录
   - 建议保留备份

3. **版本管理**
   - 不同版本使用不同的 .aipkg 文件
   - 文件名包含版本号（如 eaip-2507.aipkg）

---

## 📞 支持

如有问题：
1. 查看文档
2. 检查日志文件：`logs/manager.log`
3. 提交 Issue

---

**版本**: 1.0
**最后更新**: 2025-10-01
**作者**: EAIP Viewer Team
