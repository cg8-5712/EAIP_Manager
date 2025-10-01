#!/usr/bin/env python3
"""
AIPKG 验证工具
验证 .aipkg 文件的完整性和有效性
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.builder.aipkg_format import AIPKGHeader, PackageIndex
from src.utils.encryption_utils import derive_master_key, decrypt_data
from src.utils.logger import setup_logger, logger
import argparse
import hashlib
import getpass


def verify_aipkg(package_path: str, password: str = None) -> bool:
    """
    验证 AIPKG 文件

    Args:
        package_path: .aipkg 文件路径
        password: 解密密码（可选）

    Returns:
        是否有效
    """
    try:
        with open(package_path, 'rb') as f:
            # 读取 Header
            header_bytes = f.read(512)
            header = AIPKGHeader.from_bytes(header_bytes)

            print("\n" + "=" * 60)
            print("AIPKG 文件信息")
            print("=" * 60)
            print(f"文件: {package_path}")
            print(f"版本: {header.version_major}.{header.version_minor}")
            print(f"总文件数: {header.total_files}")
            print(f"总数据大小: {header.total_data_size / 1024 / 1024:.2f} MB")
            print(f"压缩算法: {header._get_compression_name()}")
            print(f"加密算法: {header._get_encryption_name()}")
            print(f"创建时间: {header.created_timestamp}")
            print(f"元数据: {header.metadata}")
            print("=" * 60)

            logger.debug(f"[VERIFY] Header details:")
            logger.debug(f"  - index_offset: {header.index_offset}")
            logger.debug(f"  - index_length: {header.index_length}")
            logger.debug(f"  - index_iv (hex): {header.index_iv.hex()}")
            logger.debug(f"  - index_iv (length): {len(header.index_iv)}")
            logger.debug(f"  - master_salt (hex): {header.master_salt.hex()}")
            logger.debug(f"  - file_hash (from header): {header.file_hash.hex()}")

            # 验证文件哈希
            print("\n验证文件完整性...")
            logger.info(f"[VERIFY] Computing hash from offset {512}...")

            f.seek(512)  # 跳过 Header
            hasher = hashlib.sha256()
            bytes_hashed = 0
            while chunk := f.read(8192):
                hasher.update(chunk)
                bytes_hashed += len(chunk)

            computed_hash = hasher.digest()

            # SHA256 是 32 字节，需要填充到 64 字节以匹配 Header 格式
            computed_hash_padded = computed_hash + b'\x00' * 32

            logger.info(f"[VERIFY] Hashed {bytes_hashed} bytes")
            logger.info(f"[VERIFY] Expected hash: {header.file_hash.hex()}")
            logger.info(f"[VERIFY] Computed hash (32 bytes): {computed_hash.hex()}")
            logger.info(f"[VERIFY] Computed hash (padded to 64 bytes): {computed_hash_padded.hex()}")

            if computed_hash_padded != header.file_hash:
                print("❌ 文件完整性验证失败（文件可能已损坏）")
                logger.error(f"[VERIFY] Hash mismatch!")
                logger.error(f"  Expected: {header.file_hash.hex()}")
                logger.error(f"  Got:      {computed_hash_padded.hex()}")
                return False

            print("✅ 文件完整性验证通过")
            logger.info(f"[VERIFY] File integrity verified successfully")

            # 如果提供了密码，验证解密
            if password:
                print("\n验证密码和加密...")
                logger.info(f"[VERIFY] Starting password verification...")

                # 派生密钥
                master_key = derive_master_key(password, header.master_salt)
                logger.debug(f"[VERIFY] Derived master key from password")
                logger.debug(f"[VERIFY] master_salt: {header.master_salt.hex()}")

                # 读取加密的索引
                f.seek(header.index_offset)
                encrypted_index = f.read(header.index_length)
                logger.info(f"[VERIFY] Read encrypted index: {len(encrypted_index)} bytes from offset {header.index_offset}")

                # 尝试解密索引
                logger.debug(f"[VERIFY] Decryption parameters:")
                logger.debug(f"  - IV (hex): {header.index_iv.hex()}")
                logger.debug(f"  - IV (length): {len(header.index_iv)}")
                logger.debug(f"  - associated_data: {b'AIPKG_INDEX_V1'}")

                try:
                    decrypted_index = decrypt_data(
                        encrypted_index,
                        master_key,
                        header.index_iv,
                        associated_data=b'AIPKG_INDEX_V1'
                    )

                    logger.info(f"[VERIFY] Successfully decrypted index: {len(decrypted_index)} bytes")

                    # 尝试解析索引
                    index_json = decrypted_index.decode('utf-8')
                    index = PackageIndex.from_json(index_json)

                    print(f"✅ 密码验证通过")
                    print(f"✅ 成功解密索引（{len(index.files)} 个文件记录）")
                    logger.info(f"[VERIFY] Index parsed successfully: {len(index.files)} file entries")
                    return True

                except Exception as e:
                    print(f"❌ 密码验证失败或解密错误: {e}")
                    logger.error(f"[VERIFY] Password verification failed: {e}", exc_info=True)
                    return False
            else:
                print("\n💡 提示: 使用 --password 参数可以验证密码和解密功能")
                return True

    except Exception as e:
        logger.error(f"验证失败: {e}", exc_info=True)
        print(f"❌ 错误: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='验证 AIPKG 文件')
    parser.add_argument('package', help='.aipkg 文件路径')
    parser.add_argument('--password', '-p', help='解密密码（验证解密功能）')
    parser.add_argument('--password-prompt', action='store_true', help='交互式输入密码')
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别（默认: INFO）'
    )
    args = parser.parse_args()

    setup_logger(level=args.log_level)

    if not Path(args.package).exists():
        print(f"❌ 错误：文件不存在: {args.package}")
        return 1

    # 获取密码
    password = None
    if args.password_prompt:
        password = getpass.getpass("请输入密码: ")
    elif args.password:
        password = args.password

    success = verify_aipkg(args.package, password)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
