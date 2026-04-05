import sys
import os
import fitz  # PyMuPDF
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QListWidget, QListWidgetItem,
    QLabel, QMessageBox, QProgressDialog, QScrollArea
)
from PyQt6.QtGui import QPixmap, QImage, QIcon, QPainter
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

class PDFEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF 编辑器 (Windows 11)")
        self.setMinimumSize(1000, 700)
        
        self.doc = None
        self.file_path = None
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 顶部工具栏按钮
        toolbar_layout = QHBoxLayout()
        
        self.btn_open = QPushButton("打开 PDF")
        self.btn_open.clicked.connect(self.open_pdf)
        toolbar_layout.addWidget(self.btn_open)

        self.btn_add = QPushButton("添加页面")
        self.btn_add.clicked.connect(self.add_pages)
        self.btn_add.setEnabled(False)
        toolbar_layout.addWidget(self.btn_add)

        self.btn_delete = QPushButton("删除选中页")
        self.btn_delete.clicked.connect(self.delete_pages)
        self.btn_delete.setEnabled(False)
        toolbar_layout.addWidget(self.btn_delete)

        self.btn_print = QPushButton("打印选中页")
        self.btn_print.clicked.connect(self.print_pages)
        self.btn_print.setEnabled(False)
        toolbar_layout.addWidget(self.btn_print)

        self.btn_preview = QPushButton("打印预览")
        self.btn_preview.clicked.connect(self.print_preview)
        self.btn_preview.setEnabled(False)
        toolbar_layout.addWidget(self.btn_preview)

        self.btn_save = QPushButton("保存 PDF")
        self.btn_save.clicked.connect(self.save_pdf)
        self.btn_save.setEnabled(False)
        toolbar_layout.addWidget(self.btn_save)

        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        # 页面列表显示（缩略图）
        self.page_list = QListWidget()
        self.page_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.page_list.setIconSize(QSize(200, 280))
        self.page_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.page_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.page_list.setSpacing(10)
        main_layout.addWidget(self.page_list)

        # 底部状态栏
        self.status_label = QLabel("准备就绪")
        main_layout.addWidget(self.status_label)

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "打开 PDF 文件", "", "PDF Files (*.pdf)")
        if file_path:
            try:
                self.doc = fitz.open(file_path)
                self.file_path = file_path
                self.load_pages()
                self.update_ui_state()
                self.status_label.setText(f"已加载: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开 PDF: {str(e)}")

    def load_pages(self):
        self.page_list.clear()
        if not self.doc:
            return

        progress = QProgressDialog("正在加载页面缩略图...", "取消", 0, len(self.doc), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)

        for i in range(len(self.doc)):
            if progress.wasCanceled():
                break
            
            page = self.doc[i]
            # 渲染缩略图
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2)) # 缩小比例以提高性能
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            qpixmap = QPixmap.fromImage(img)
            
            item = QListWidgetItem(f"第 {i+1} 页")
            item.setIcon(QIcon(qpixmap))
            item.setData(Qt.ItemDataRole.UserRole, i) # 存储原始页码
            self.page_list.addItem(item)
            
            progress.setValue(i + 1)
        
        progress.setValue(len(self.doc))

    def update_ui_state(self):
        has_doc = self.doc is not None
        self.btn_add.setEnabled(has_doc)
        self.btn_delete.setEnabled(has_doc)
        self.btn_print.setEnabled(has_doc)
        self.btn_preview.setEnabled(has_doc)
        self.btn_save.setEnabled(has_doc)

    def delete_pages(self):
        selected_items = self.page_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "提示", "请先选择要删除的页面。")
            return

        indices = sorted([item.data(Qt.ItemDataRole.UserRole) for item in selected_items], reverse=True)
        
        reply = QMessageBox.question(self, "确认删除", f"确定要删除选中的 {len(indices)} 个页面吗？",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            for idx in indices:
                self.doc.delete_page(idx)
            
            self.load_pages()
            self.status_label.setText("页面已删除")

    def add_pages(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择要添加的 PDF 文件", "", "PDF Files (*.pdf)")
        if file_path:
            try:
                other_doc = fitz.open(file_path)
                # 将新 PDF 的所有页添加到当前文档末尾
                self.doc.insert_pdf(other_doc)
                other_doc.close()
                self.load_pages()
                self.status_label.setText(f"已从 {os.path.basename(file_path)} 添加页面")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法添加 PDF: {str(e)}")

    def print_pages(self):
        selected_items = self.page_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "提示", "请先选择要打印的页面。")
            return

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.render_for_printing(printer)
            self.status_label.setText("打印任务已发送")

    def print_preview(self):
        selected_items = self.page_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "提示", "请先选择要预览的页面。")
            return

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.setWindowTitle("打印预览")
        preview.setWindowFlags(preview.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        preview.paintRequested.connect(self.render_for_printing)
        preview.exec()

    def render_for_printing(self, printer):
        selected_items = self.page_list.selectedItems()
        if not selected_items:
            return

        painter = QPainter(printer)
        indices = sorted([item.data(Qt.ItemDataRole.UserRole) for item in selected_items])
        
        for i, idx in enumerate(indices):
            if i > 0:
                printer.newPage()
            
            page = self.doc[idx]
            # 获取高分辨率图像用于打印
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            
            # 绘制到打印机，自动缩放以适应页面
            rect = painter.viewport()
            size = img.size()
            size.scale(rect.size(), Qt.AspectRatioMode.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(img.rect())
            painter.drawImage(0, 0, img)
        
        painter.end()

    def save_pdf(self):
        if not self.doc:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "保存 PDF", self.file_path, "PDF Files (*.pdf)")
        if file_path:
            try:
                # 必须增量保存或完全保存。这里使用完全保存。
                self.doc.save(file_path, garbage=3, deflate=True)
                self.status_label.setText(f"已保存到: {os.path.basename(file_path)}")
                self.file_path = file_path
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = PDFEditor()
    editor.show()
    sys.exit(app.exec())
