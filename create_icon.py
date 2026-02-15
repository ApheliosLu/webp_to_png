# 作者: 陆离ApheliosLu
# 2026年02月01日17时57分49秒
# Leon12097@163.com

from PIL import Image, ImageDraw, ImageFont
import os


def create_webp_converter_icon():
    """创建WebP转PNG转换器图标"""

    print("正在创建图标...")

    # 定义多个尺寸（Windows需要这些尺寸）
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []

    for width, height in sizes:
        # 创建透明背景
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # 计算内边距
        padding = max(1, width // 16)

        # 1. 绘制背景形状
        bg_color = (66, 133, 244, 200)  # Google蓝色
        draw.rounded_rectangle(
            [padding, padding, width - padding, height - padding],
            radius=width // 6,
            fill=bg_color,
            outline=(255, 255, 255, 255),
            width=max(1, width // 32)
        )

        # 2. 绘制图标元素（只在足够大的尺寸上）
        if width >= 32:
            # 左边：WebP的"W"
            webp_color = (255, 193, 7)  # 黄色/橙色
            left_center_x = width // 3
            center_y = height // 2

            # 绘制WebP圆形背景
            circle_radius = width // 6
            draw.ellipse([
                left_center_x - circle_radius,
                center_y - circle_radius,
                left_center_x + circle_radius,
                center_y + circle_radius
            ], fill=webp_color)

            # 绘制"W"字母
            if width >= 64:
                try:
                    font_size = max(8, width // 6)
                    font = ImageFont.truetype("arial.ttf", font_size)
                    draw.text(
                        (left_center_x, center_y - 2),
                        "W",
                        fill=(0, 0, 0, 255),
                        font=font,
                        anchor="mm"
                    )
                except:
                    # 如果字体不可用，绘制简单的W
                    draw.text(
                        (left_center_x - 3, center_y - 5),
                        "W",
                        fill=(0, 0, 0, 255)
                    )

            # 右边：PNG的"P"
            png_color = (76, 175, 80)  # 绿色
            right_center_x = width * 2 // 3

            # 绘制PNG圆形背景
            draw.ellipse([
                right_center_x - circle_radius,
                center_y - circle_radius,
                right_center_x + circle_radius,
                center_y + circle_radius
            ], fill=png_color)

            # 绘制"P"字母
            if width >= 64:
                try:
                    draw.text(
                        (right_center_x, center_y - 2),
                        "P",
                        fill=(255, 255, 255, 255),
                        font=font,
                        anchor="mm"
                    )
                except:
                    draw.text(
                        (right_center_x - 2, center_y - 5),
                        "P",
                        fill=(255, 255, 255, 255)
                    )

            # 3. 绘制转换箭头
            if width >= 48:
                arrow_width = width // 12
                arrow_x = width // 2

                # 绘制箭头
                draw.polygon([
                    (arrow_x - arrow_width, center_y),
                    (arrow_x + arrow_width, center_y - arrow_width),
                    (arrow_x + arrow_width, center_y + arrow_width)
                ], fill=(255, 255, 255, 255))

        images.append(img)

    # 保存为ICO文件
    output_path = "webp_converter_icon.ico"
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images],
        bitmap_format='bmp'
    )

    print(f"✅ 图标已成功创建: {output_path}")
    print(f"📁 文件大小: {os.path.getsize(output_path) // 1024} KB")
    print(f"📐 包含尺寸: {', '.join([f'{w}x{h}' for w, h in sizes])}")

    # 显示预览
    print("\n🎨 图标预览:")
    preview_size = min(256, max(sizes, key=lambda x: x[0])[0])
    preview_img = next(img for w, h in sizes if w == preview_size)

    # 简单的ASCII预览（对于256x256）
    if preview_size >= 128:
        print("(在文件管理器中查看实际效果)")

    return output_path


def create_simple_icon():
    """创建简化版图标"""

    sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    images = []

    for width, height in sizes:
        img = Image.new('RGB', (width, height), (240, 240, 240))
        draw = ImageDraw.Draw(img)

        # 绘制两个重叠的方块表示转换
        box_size = width * 2 // 3
        padding = (width - box_size) // 2

        # 左边方块（WebP - 橙色）
        draw.rectangle(
            [padding, padding, padding + box_size * 2 // 3, height - padding],
            fill=(255, 152, 0),
            outline=(0, 0, 0)
        )

        # 右边方块（PNG - 蓝色）
        draw.rectangle(
            [width - padding - box_size * 2 // 3, padding, width - padding, height - padding],
            fill=(33, 150, 243),
            outline=(0, 0, 0)
        )

        # 箭头
        if width >= 32:
            arrow_x = width // 2
            arrow_y = height // 2
            arrow_size = width // 8

            draw.polygon([
                (arrow_x, arrow_y - arrow_size),
                (arrow_x + arrow_size, arrow_y),
                (arrow_x, arrow_y + arrow_size)
            ], fill=(0, 0, 0))

        images.append(img)

    output_path = "simple_icon.ico"
    images[0].save(output_path, format='ICO', sizes=[(w, h) for w, h in sizes])
    print(f"✅ 简化图标已创建: {output_path}")

    return output_path


if __name__ == "__main__":
    print("=" * 50)
    print("      WebP转PNG转换器图标生成器")
    print("=" * 50)

    try:
        # 检查PIL是否安装
        from PIL import Image, ImageDraw

        print("\n请选择图标风格:")
        print("1. 精美风格图标 (推荐)")
        print("2. 简化风格图标")

        choice = input("请输入选择 (1 或 2): ").strip()

        if choice == "1":
            icon_file = create_webp_converter_icon()
        else:
            icon_file = create_simple_icon()

        print(f"\n🎯 使用说明:")
        print(f"1. 在 Auto-Py-To-Exe 中，点击 'Icon (optional)' 的 'Browse...'")
        print(f"2. 选择: {icon_file}")
        print(f"3. 继续打包，exe文件就会显示这个图标")

        input("\n按回车键退出...")

    except ImportError:
        print("❌ 需要安装Pillow库，请运行:")
        print("   pip install Pillow")
        input("\n按回车键退出...")