"""
WebP转PNG转换器 - PyQt5 稳定版
作者：AI助手
日期：2024年
"""
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QTextEdit, QProgressBar, QFileDialog, QMessageBox,
                             QGroupBox, QCheckBox, QSpinBox, QComboBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon
from PIL import Image, ImageFile
import traceback
import time

# 允许加载大图片
ImageFile.LOAD_TRUNCATED_IMAGES = True


class ConversionWorker(QThread):
    """转换工作线程"""

    # 定义信号
    progress_updated = pyqtSignal(int, int)  # 当前进度, 总文件数
    file_converted = pyqtSignal(str, str, bool, str)  # 文件名, 状态, 是否成功, 消息
    conversion_finished = pyqtSignal(int, int, int)  # 成功数, 跳过数, 失败数
    log_message = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, input_folder, output_folder, options):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.options = options
        self._is_running = True

    def run(self):
        """线程主函数"""
        try:
            self.log_message.emit(f"开始转换，输入文件夹: {self.input_folder}")
            self.log_message.emit(f"输出文件夹: {self.output_folder}")

            # 创建输出文件夹
            if not os.path.exists(self.output_folder):
                try:
                    os.makedirs(self.output_folder)
                    self.log_message.emit(f"已创建输出文件夹: {self.output_folder}")
                except Exception as e:
                    self.error_occurred.emit(f"无法创建输出文件夹: {str(e)}")
                    return

            # 查找所有.webp文件（不区分大小写）
            webp_files = []
            try:
                for filename in os.listdir(self.input_folder):
                    if filename.lower().endswith('.webp'):
                        webp_files.append(filename)
            except Exception as e:
                self.error_occurred.emit(f"无法读取输入文件夹: {str(e)}")
                return

            if not webp_files:
                self.log_message.emit("未找到任何.webp文件")
                self.conversion_finished.emit(0, 0, 0)
                return

            total_files = len(webp_files)
            self.log_message.emit(f"找到 {total_files} 个.webp文件")

            success_count = 0
            skip_count = 0
            fail_count = 0

            # 开始转换每个文件
            for i, filename in enumerate(webp_files, 1):
                if not self._is_running:
                    self.log_message.emit("转换被用户停止")
                    break

                try:
                    # 构建完整路径
                    input_path = os.path.join(self.input_folder, filename)

                    # 检查输入文件是否存在且可读
                    if not os.path.exists(input_path):
                        self.file_converted.emit(filename, "文件不存在", False, "")
                        fail_count += 1
                        continue

                    if not os.access(input_path, os.R_OK):
                        self.file_converted.emit(filename, "文件不可读", False, "")
                        fail_count += 1
                        continue

                    # 生成输出文件名和路径
                    base_name = os.path.splitext(filename)[0]
                    png_filename = f"{base_name}.png"
                    output_path = os.path.join(self.output_folder, png_filename)

                    # 检查是否跳过已存在文件
                    if os.path.exists(output_path) and not self.options.get('overwrite', False):
                        self.file_converted.emit(filename, "已跳过（文件已存在）", True, "")
                        skip_count += 1
                        self.progress_updated.emit(i, total_files)
                        continue

                    # 检查输出路径是否可写
                    output_dir = os.path.dirname(output_path)
                    if not os.access(output_dir, os.W_OK):
                        self.file_converted.emit(filename, "输出文件夹不可写", False, "")
                        fail_count += 1
                        self.progress_updated.emit(i, total_files)
                        continue

                    # 执行转换
                    success, message = self.convert_single_file(input_path, output_path)

                    if success:
                        self.file_converted.emit(filename, "转换成功", True, message)
                        success_count += 1
                    else:
                        self.file_converted.emit(filename, f"转换失败: {message}", False, "")
                        fail_count += 1

                except Exception as e:
                    error_msg = f"处理文件 {filename} 时出错: {str(e)}"
                    self.file_converted.emit(filename, error_msg, False, "")
                    fail_count += 1

                # 更新进度
                self.progress_updated.emit(i, total_files)

                # 短暂延迟，避免UI卡顿
                time.sleep(0.01)

            # 发送完成信号
            self.conversion_finished.emit(success_count, skip_count, fail_count)

        except Exception as e:
            self.error_occurred.emit(f"转换过程发生错误: {str(e)}")

    def convert_single_file(self, input_path, output_path):
        """转换单个文件"""
        try:
            # 打开图片
            with Image.open(input_path) as img:
                # 获取图片信息
                img_format = img.format
                img_mode = img.mode
                img_size = img.size

                # 转换为RGB模式（如果必要）
                if img_mode in ('RGBA', 'LA', 'P', 'CMYK'):
                    if img_mode == 'RGBA':
                        # 创建一个白色背景
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        # 合并alpha通道
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = img.convert('RGB')

                # 获取压缩级别
                compress_level = self.options.get('compress_level', 6)

                # 保存为PNG
                img.save(
                    output_path,
                    format='PNG',
                    compress_level=compress_level,
                    optimize=True
                )

            # 验证输出文件
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / 1024  # KB
                return True, f"{img_size[0]}x{img_size[1]} ({file_size:.1f}KB)"
            else:
                return False, "输出文件未创建"

        except Exception as e:
            return False, str(e)

    def stop(self):
        """停止转换"""
        self._is_running = False


class WebPConverterApp(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.worker = None
        self.current_folder = os.getcwd()
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("WebP转PNG转换器")
        self.setGeometry(100, 100, 700, 600)

        # 设置窗口图标（如果有的话）
        self.setWindowIcon(QIcon())

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)

        # 标题
        title_label = QLabel("WebP转PNG转换器")
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)

        # 文件夹设置组
        folder_group = QGroupBox("文件夹设置")
        folder_layout = QVBoxLayout()

        # 输入文件夹
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("输入文件夹:"))
        self.input_path_edit = QLineEdit(self.current_folder)
        self.input_path_edit.setReadOnly(True)
        input_layout.addWidget(self.input_path_edit)

        self.browse_input_btn = QPushButton("浏览...")
        self.browse_input_btn.setFixedWidth(80)
        input_layout.addWidget(self.browse_input_btn)
        folder_layout.addLayout(input_layout)

        # 输出文件夹名
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出文件夹名:"))
        self.output_name_edit = QLineEdit("PNG_转换结果")
        self.output_name_edit.setFixedWidth(150)
        output_layout.addWidget(self.output_name_edit)
        output_layout.addStretch()
        folder_layout.addLayout(output_layout)

        folder_group.setLayout(folder_layout)
        main_layout.addWidget(folder_group)

        # 转换选项组
        options_group = QGroupBox("转换选项")
        options_layout = QVBoxLayout()

        # 覆盖选项
        self.overwrite_check = QCheckBox("覆盖已存在的文件")
        options_layout.addWidget(self.overwrite_check)

        # 压缩级别
        compression_layout = QHBoxLayout()
        compression_layout.addWidget(QLabel("PNG压缩级别:"))
        self.compression_combo = QComboBox()
        for i in range(10):
            self.compression_combo.addItem(f"{i} - {'最快' if i == 0 else '最小' if i == 9 else f'级别{i}'}")
        self.compression_combo.setCurrentIndex(6)  # 默认级别6
        self.compression_combo.setToolTip("0=最快（文件大）~ 9=最慢（文件小）")
        self.compression_combo.setFixedWidth(200)
        compression_layout.addWidget(self.compression_combo)
        compression_layout.addStretch()
        options_layout.addLayout(compression_layout)

        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.convert_btn = QPushButton("▶ 开始转换")
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.convert_btn.setFixedHeight(40)
        button_layout.addWidget(self.convert_btn)

        self.stop_btn = QPushButton("■ 停止")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)

        self.open_folder_btn = QPushButton("📂 打开输出文件夹")
        self.open_folder_btn.setFixedHeight(40)
        button_layout.addWidget(self.open_folder_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% (%v/%m)")
        main_layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        main_layout.addWidget(self.status_label)

        # 日志区域
        log_group = QGroupBox("转换日志")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 10pt;
            }
        """)
        log_layout.addWidget(self.log_text)

        # 日志操作按钮
        log_buttons_layout = QHBoxLayout()
        self.clear_log_btn = QPushButton("清空日志")
        log_buttons_layout.addWidget(self.clear_log_btn)
        log_buttons_layout.addStretch()

        self.copy_log_btn = QPushButton("复制日志")
        log_buttons_layout.addWidget(self.copy_log_btn)
        log_layout.addLayout(log_buttons_layout)

        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        # 设置布局比例
        main_layout.setStretch(0, 0)  # 标题
        main_layout.setStretch(1, 0)  # 文件夹设置
        main_layout.setStretch(2, 0)  # 转换选项
        main_layout.setStretch(3, 0)  # 按钮
        main_layout.setStretch(4, 0)  # 进度条
        main_layout.setStretch(5, 0)  # 状态标签
        main_layout.setStretch(6, 1)  # 日志区域（可伸缩）

    def setup_connections(self):
        """设置信号和槽的连接"""
        self.browse_input_btn.clicked.connect(self.browse_input_folder)
        self.convert_btn.clicked.connect(self.start_conversion)
        self.stop_btn.clicked.connect(self.stop_conversion)
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        self.clear_log_btn.clicked.connect(self.clear_log)
        self.copy_log_btn.clicked.connect(self.copy_log)

    def browse_input_folder(self):
        """浏览输入文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择包含WebP图片的文件夹",
            self.current_folder
        )
        if folder:
            self.current_folder = folder
            self.input_path_edit.setText(folder)
            self.log_message(f"已选择文件夹: {folder}")

    def log_message(self, message):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.log_text.append(f"[{timestamp}] {message}")
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.log_message("日志已清空")

    def copy_log(self):
        """复制日志到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.log_text.toPlainText())
        self.log_message("日志已复制到剪贴板")

    def start_conversion(self):
        """开始转换"""
        # 检查输入文件夹
        input_folder = self.input_path_edit.text()
        if not input_folder or not os.path.exists(input_folder):
            QMessageBox.warning(self, "警告", "请输入有效的输入文件夹路径！")
            return

        # 检查输出文件夹名
        output_folder_name = self.output_name_edit.text().strip()
        if not output_folder_name:
            QMessageBox.warning(self, "警告", "请输入输出文件夹名！")
            return

        # 构建输出文件夹路径
        output_folder = os.path.join(input_folder, output_folder_name)

        # 准备选项
        options = {
            'overwrite': self.overwrite_check.isChecked(),
            'compress_level': self.compression_combo.currentIndex()
        }

        # 创建并启动工作线程
        self.worker = ConversionWorker(input_folder, output_folder, options)

        # 连接信号
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.file_converted.connect(self.handle_file_converted)
        self.worker.conversion_finished.connect(self.handle_conversion_finished)
        self.worker.log_message.connect(self.log_message)
        self.worker.error_occurred.connect(self.handle_error)

        # 更新UI状态
        self.convert_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在转换...")
        self.status_label.setStyleSheet("color: #e67e22; font-weight: bold;")

        # 清空日志（可选）
        # self.clear_log()

        # 启动线程
        self.worker.start()

        self.log_message("=" * 50)
        self.log_message("开始转换WebP文件到PNG格式")
        self.log_message(f"输入文件夹: {input_folder}")
        self.log_message(f"输出文件夹: {output_folder}")
        self.log_message(f"覆盖模式: {'是' if options['overwrite'] else '否'}")
        self.log_message(f"压缩级别: {options['compress_level']}")
        self.log_message("=" * 50)

    def stop_conversion(self):
        """停止转换"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.log_message("正在停止转换...")
            self.status_label.setText("正在停止...")

    def update_progress(self, current, total):
        """更新进度条"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
            self.status_label.setText(f"正在转换: {current}/{total} ({percentage}%)")

    def handle_file_converted(self, filename, status, success, message):
        """处理单个文件转换完成"""
        if success:
            self.log_message(f"✓ {filename}: {status} {message}")
        else:
            self.log_message(f"✗ {filename}: {status}")

    def handle_conversion_finished(self, success_count, skip_count, fail_count):
        """处理转换完成"""
        total = success_count + skip_count + fail_count

        # 更新UI状态
        self.convert_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(self.progress_bar.maximum())

        # 显示结果
        result_message = f"""
{'=' * 50}
转换完成！
{'=' * 50}
总文件数: {total}
✓ 成功转换: {success_count}
⚠️ 跳过: {skip_count}
✗ 失败: {fail_count}
{'=' * 50}
        """

        self.log_message(result_message)

        if fail_count == 0:
            self.status_label.setText(f"转换完成！成功: {success_count}/{total}")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")

            if success_count > 0:
                # 询问是否打开输出文件夹
                reply = QMessageBox.question(
                    self,
                    "转换完成",
                    f"转换完成！成功转换 {success_count} 个文件。\n是否打开输出文件夹？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if reply == QMessageBox.Yes:
                    self.open_output_folder()
        else:
            self.status_label.setText(f"转换完成，但有 {fail_count} 个文件失败")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")

            QMessageBox.warning(
                self,
                "转换完成",
                f"转换完成，但有 {fail_count} 个文件失败。\n请查看日志了解详细信息。"
            )

        self.worker = None

    def handle_error(self, error_message):
        """处理错误"""
        self.log_message(f"❌ 错误: {error_message}")

        # 更新UI状态
        self.convert_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("转换出错")
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")

        QMessageBox.critical(self, "错误", error_message)
        self.worker = None

    def open_output_folder(self):
        """打开输出文件夹"""
        input_folder = self.input_path_edit.text()
        output_folder_name = self.output_name_edit.text().strip()

        if input_folder and output_folder_name:
            output_folder = os.path.join(input_folder, output_folder_name)
            if os.path.exists(output_folder):
                try:
                    if sys.platform == "win32":
                        os.startfile(output_folder)
                    elif sys.platform == "darwin":
                        os.system(f'open "{output_folder}"')
                    else:
                        os.system(f'xdg-open "{output_folder}"')
                    self.log_message(f"已打开输出文件夹: {output_folder}")
                except Exception as e:
                    self.log_message(f"无法打开文件夹: {str(e)}")
                    QMessageBox.warning(self, "错误", f"无法打开文件夹:\n{str(e)}")
            else:
                QMessageBox.information(self, "提示", "输出文件夹不存在")
        else:
            QMessageBox.warning(self, "警告", "请先设置输入文件夹和输出文件夹名")

    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "确认退出",
                "转换正在进行中，确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.worker.stop()
                self.worker.wait(2000)  # 等待2秒让线程结束
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """主函数"""
    # 设置高DPI支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion样式，更现代

    # 创建并显示主窗口
    window = WebPConverterApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    # 检查Pillow是否支持WebP
    try:
        from PIL import features

        if not features.check_codec("webp"):
            print("警告: Pillow没有WebP支持，请安装完整版: pip install Pillow[webp]")
    except:
        pass

    main()