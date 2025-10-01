#!/usr/bin/env python3
"""
EAIP Manager 快速开始脚本
交互式引导打包流程
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.builder.aipkg_builder import AIPKGBuilder
from src.utils.logger import setup_logger, logger
import getpass


def main():
    print("\n" + "=" * 60)
    print("EAIP Manager - 航图打包工具")
    print("=" * 60)

    setup_logger(level="INFO")

    # 1. 输入源目录
    print("\n步骤 1：指定源目录")
    print("请输入 Terminal 目录的完整路径")
    print("示例：F:\\航图数据\\EAIP2025-07.V1.4\\Terminal")

    source_dir = input("\n源目录: ").strip().strip('"')

    if not Path(source_dir).exists():
        print(f"❌ 错误：目录不存在: {source_dir}")
        return 1

    # 2. 输入输出文件
    print("\n步骤 2：指定输出文件")
    print("请输入输出的 .aipkg 文件路径")
    print("示例：../packages/eaip-2507.aipkg")

    output_file = input("\n输出文件: ").strip().strip('"')

    # 确保输出目录存在
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 3. 输入版本（可选）
    print("\n步骤 3：EAIP 版本（可选）")
    print("留空则自动检测")

    eaip_version = input("\nEAIP 版本: ").strip()
    if not eaip_version:
        eaip_version = None

    # 4. 输入密码
    print("\n步骤 4：设置加密密码")
    print("⚠️  重要：请妥善保管此密码（Distribution Password）")
    print("要求：")
    print("  - 至少 12 个字符")
    print("  - 包含大小写字母、数字和特殊字符")
    print("  - 示例：Aviation2025!@ComplexPassword")

    while True:
        password = getpass.getpass("\n密码: ")
        password_confirm = getpass.getpass("确认密码: ")

        if password != password_confirm:
            print("❌ 两次输入的密码不一致，请重试")
            continue

        if len(password) < 12:
            print("❌ 密码长度至少 12 个字符，请重试")
            continue

        break

    # 5. 选择压缩配置
    print("\n步骤 5：压缩配置")
    print("  1. 标准压缩（级别 6，推荐）")
    print("  2. 最高压缩（级别 9，慢）")
    print("  3. 最快速度（级别 1）")
    print("  4. 禁用压缩")

    choice = input("\n请选择 [1-4，默认1]: ").strip() or "1"

    compression_map = {
        "1": ("gzip", 6),
        "2": ("gzip", 9),
        "3": ("gzip", 1),
        "4": ("none", 0)
    }

    compression, level = compression_map.get(choice, ("gzip", 6))

    # 6. 确认信息
    print("\n" + "=" * 60)
    print("打包信息确认")
    print("=" * 60)
    print(f"源目录: {source_dir}")
    print(f"输出文件: {output_file}")
    print(f"EAIP 版本: {eaip_version or '自动检测'}")
    print(f"压缩: {compression}")
    if compression != "none":
        print(f"压缩级别: {level}")
    print("=" * 60)

    confirm = input("\n确认开始打包? [Y/n]: ").strip().lower()
    if confirm and confirm != 'y':
        print("操作已取消")
        return 0

    # 7. 开始打包
    print("\n开始打包...\n")

    def progress_callback(current, total, message):
        if total > 0:
            percentage = int(current / total * 100)
            bar_length = 40
            filled = int(bar_length * current / total)
            bar = '=' * filled + '-' * (bar_length - filled)
            print(f'\r[{bar}] {percentage}% - {message}', end='', flush=True)
        else:
            print(f'\r{message}', end='', flush=True)

    try:
        builder = AIPKGBuilder()
        result = builder.create_package(
            source_dir=source_dir,
            output_path=output_file,
            password=password,
            eaip_version=eaip_version,
            compression=compression,
            compression_level=level,
            progress_callback=progress_callback
        )

        print()  # 换行
        print("\n" + "=" * 60)
        print("✅ 打包成功！")
        print("=" * 60)
        print(f"输出文件: {result['output_path']}")
        print(f"EAIP 版本: {result['eaip_version']}")
        print(f"文件总数: {result['total_files']}")
        print(f"机场数量: {result['airports_count']}")
        print(f"原始大小: {result['original_size'] / 1024 / 1024:.2f} MB")
        print(f"最终大小: {result['final_size'] / 1024 / 1024:.2f} MB")
        print(f"压缩率: {result['final_size'] / result['original_size'] * 100:.1f}%")
        print("=" * 60)

        print("\n⚠️  重要提醒：")
        print(f"1. 请妥善保管密码（Distribution Password）")
        print(f"2. 在 EAIP_Viewer 中配置此密码")
        print(f"3. .aipkg 文件可以分发给用户")

        return 0

    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        return 130

    except Exception as e:
        logger.error(f"打包失败: {e}", exc_info=True)
        print(f"\n\n❌ 错误: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
