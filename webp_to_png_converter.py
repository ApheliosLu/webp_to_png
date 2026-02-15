"""
WebP转PNG转换器
将当前文件夹中的所有.webp文件转换为.png格式
"""
import sys
import os
from PIL import Image


def convert_webp_to_png():
    """
    转换当前目录下的所有WebP文件为PNG格式
    """
    try:
        print("=" * 50)
        print("    WebP 转 PNG 转换器")
        print("=" * 50)

        # 获取当前程序所在目录
        if getattr(sys, 'frozen', False):
            # 如果被打包成exe
            current_folder = os.path.dirname(sys.executable)
        else:
            # 如果以脚本形式运行
            current_folder = os.path.dirname(os.path.abspath(__file__))

        print(f"当前目录: {current_folder}")

        # 创建输出文件夹
        output_folder = os.path.join(current_folder, "PNG_转换结果")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"已创建输出文件夹: {output_folder}")

        # 查找所有.webp文件（不区分大小写）
        webp_files = []
        for filename in os.listdir(current_folder):
            if filename.lower().endswith(".webp"):
                webp_files.append(filename)

        if not webp_files:
            print("\n❌ 未找到任何.webp文件！")
            print("请将本程序放在包含.webp文件的文件夹中运行。")
            return

        print(f"\n找到 {len(webp_files)} 个.webp文件：")
        for i, file in enumerate(webp_files, 1):
            print(f"  {i}. {file}")

        print("\n开始转换...")
        print("-" * 50)

        success_count = 0
        skip_count = 0
        error_count = 0

        # 转换每个.webp文件
        for filename in webp_files:
            try:
                # 完整的文件路径
                input_path = os.path.join(current_folder, filename)

                # 生成输出文件名
                base_name = os.path.splitext(filename)[0]
                png_filename = f"{base_name}.png"
                output_path = os.path.join(output_folder, png_filename)

                # 检查文件是否已存在
                if os.path.exists(output_path):
                    print(f"⚠️  跳过: {filename} → {png_filename} (文件已存在)")
                    skip_count += 1
                    continue

                # 打开并转换图片
                with Image.open(input_path) as img:
                    # 保存为PNG格式
                    img.save(output_path, format="PNG", optimize=True)

                print(f"✅ 已转换: {filename} → {png_filename}")
                success_count += 1

            except Exception as e:
                print(f"❌ 转换失败 {filename}: {str(e)}")
                error_count += 1

        # 显示转换结果
        print("\n" + "=" * 50)
        print("转换完成！")
        print("-" * 50)
        print(f"✅ 成功转换: {success_count} 个文件")
        if skip_count > 0:
            print(f"⚠️  跳过: {skip_count} 个文件（已存在）")
        if error_count > 0:
            print(f"❌ 转换失败: {error_count} 个文件")
        print("-" * 50)
        print(f"📁 PNG文件保存在: {output_folder}")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ 程序运行出错: {str(e)}")

    finally:
        # 如果是exe运行，等待用户按键退出
        if getattr(sys, 'frozen', False):
            input("\n按回车键退出程序...")


def main():
    """主函数"""
    convert_webp_to_png()


if __name__ == "__main__":
    main()