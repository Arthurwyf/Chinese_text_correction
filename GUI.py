import sys  # 导入sys模块，用于访问命令行参数和退出应用程序
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit  # 导入PyQt5库中的相关组件类
from transformers import AutoModelForCausalLM, AutoTokenizer  # 导入transformers库中的模型和tokenizer类
import torch  # 导入PyTorch库
from pycorrector.t5.t5_corrector import T5Corrector
import re
import os


class TextCorrectionApp(QMainWindow):
    def __init__(self):
        super().__init__()  # 调用父类的构造函数
        self.file_path = None
        self.initUI()  # 初始化用户界面

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)  # 设置窗口的位置和大小
        self.setWindowTitle('中文文本纠错')  # 设置窗口标题

        self.text_edit = QTextEdit(self)  # 创建一个文本编辑框
        self.text_edit.setGeometry(10, 10, 780, 400)  # 设置文本编辑框的位置和大小

        self.load_button = QPushButton('加载小说', self)  # 创建加载小说按钮
        self.load_button.setGeometry(10, 420, 100, 40)  # 设置加载按钮的位置和大小
        self.load_button.clicked.connect(self.loadNovel)  # 将加载按钮的点击事件连接到loadNovel函数

        self.correct_button = QPushButton('开始纠错', self)  # 创建开始纠错按钮
        self.correct_button.setGeometry(120, 420, 100, 40)  # 设置开始纠错按钮的位置和大小
        self.correct_button.clicked.connect(self.correctText)  # 将开始纠错按钮的点击事件连接到correctText函数
        
        self.show()  # 显示窗口

    def loadNovel(self):
        options = QFileDialog.Options()  # 创建文件对话框选项对象
        options |= QFileDialog.ReadOnly  # 设置文件对话框为只读模式
        file_name, _ = QFileDialog.getOpenFileName(self, '加载小说', '', '文本文件 (*.txt);;所有文件 (*)', options=options)  # 打开文件对话框以选择小说文件

        if file_name:  # 如果用户选择了文件
            self.file_path = file_name
            with open(file_name, 'r', encoding='utf-8') as file:  # 打开选定的文件以读取文本
                self.novel_text = file.read()  # 读取文件内容并存储在novel_text变量中
                self.text_edit.setPlainText(self.novel_text)  # 将文件内容显示在文本编辑框中

    def correctText(self):
        if hasattr(self, 'novel_text'):  # 如果novel_text属性存在，表示已加载小说
            nlp = T5Corrector("./mengzi-t5-base-chinese-correction").batch_t5_correct

            chapter_pattern = re.compile(r'第[零一二三四五六七八九十百千]+章 ')
            chapters = chapter_pattern.split(self.novel_text)

            # with open("aaa.txt", 'w') as writer:
            #     print("here")
            #     # 打印提取到的章节
            #     for i, chapter in enumerate(chapters, start=1):
            #         if i == 1:
            #             print(f"第{i}章内容：\n{chapter}\n")
            #         writer.write(f"第{i}章内容：\n{chapter}\n")
            

            corrected_chapters = []  # 创建一个存储纠正后章节的列表
            for index, chapter in enumerate(chapters):  # 遍历每个章节
                corrected_chapter = f"第{index}章内容：\n"
                chunks = split_text_into_chunks(chapter)
                for chunk in chunks:
                    output = nlp([chunk])
                    corrected_chapter += output[0][0]

                corrected_chapters.append(corrected_chapter)  # 将纠正后的章节添加到列表中
            corrected_novel = '\n\n'.join(corrected_chapters)  # 使用章节分隔符合并修正后的章节
            self.text_edit.setPlainText(corrected_novel)  # 将修正后的小说显示在文本编辑框中

            with open(self.file_path+"new.txt", 'w') as writer:
                writer.write(corrected_novel)

def split_text_into_chunks(text, chunk_size=127):
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

if __name__ == '__main__':
    app = QApplication(sys.argv)  # 创建Qt应用程序
    ex = TextCorrectionApp()  # 创建TextCorrectionApp实例
    sys.exit(app.exec_())  # 启动应用程序的事件循环
