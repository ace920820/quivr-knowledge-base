import os
import sys
import traceback
import asyncio
from pathlib import Path

# 检查PyPDF2是否已正确安装
try:
    import PyPDF2
    print(f"成功加载PyPDF2库，版本: {PyPDF2.__version__ if hasattr(PyPDF2, '__version__') else '未知'}")
except ImportError as e:
    print(f"错误: 无法加载PyPDF2库 - {e}")
    # 尝试重新安装
    print("正在尝试重新安装PyPDF2...")
    try:
        import pip
        pip.main(['install', 'PyPDF2', '--upgrade'])
        import PyPDF2
        print(f"重新安装PyPDF2成功，版本: {PyPDF2.__version__ if hasattr(PyPDF2, '__version__') else '未知'}")
    except Exception as e2:
        print(f"安装PyPDF2失败: {e2}")

from langchain_core.documents import Document

class CustomPDFProcessor:
    """自定义 PDF 处理器，不依赖 Tika 服务器"""
    
    async def process_file(self, file_path):
        """
        处理 PDF 文件并返回文档列表
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            list[Document]: 处理后的文档列表
        """
        print(f"开始处理 PDF 文件: {file_path}")
        
        # 转换路径对象
        try:
            if isinstance(file_path, str):
                file_path = Path(file_path)
                print(f"路径转换为 Path 对象: {file_path}")
        except Exception as path_err:
            print(f"路径转换错误: {path_err}")
            file_path = Path(str(file_path))  # 强制尝试转换
            
        # 检查文件是否存在
        try:
            if not file_path.exists():
                print(f"警告: 文件不存在: {file_path}")
                print(f"当前工作目录: {os.getcwd()}")
                print(f"尝试使用绝对路径: {os.path.abspath(str(file_path))}")
                
                # 检查绝对路径是否存在
                abs_path = os.path.abspath(str(file_path))
                if os.path.exists(abs_path):
                    print(f"找到了绝对路径文件: {abs_path}")
                    file_path = Path(abs_path)
                else:
                    raise FileNotFoundError(f"文件不存在: {file_path} (绝对路径: {abs_path})")
        except Exception as exists_err:
            print(f"检查文件存在时出错: {exists_err}")
            traceback.print_exc()
            raise
            
        # 确保是 PDF 文件
        try:
            if file_path.suffix.lower() != '.pdf':
                print(f"警告: 文件不是 PDF 格式: {file_path.suffix}")
                raise ValueError(f"不是 PDF 文件: {file_path}")
            else:
                print(f"确认是 PDF 文件: {file_path}")
        except Exception as suffix_err:
            print(f"检查文件后缀时出错: {suffix_err}")
            traceback.print_exc()
        
        # 处理 PDF 文件
        try:
            # 使用 PyPDF2 读取 PDF 内容
            print(f"开始读取 PDF 文件: {file_path}")
            text_content = ""
            
            # 打印更详细的 PyPDF2 信息
            print(f"PyPDF2 模块路径: {PyPDF2.__file__}")
            print(f"PyPDF2 版本: {getattr(PyPDF2, '__version__', '未知')}")
            
            # 打开并处理 PDF
            with open(str(file_path), 'rb') as pdf_file:
                print(f"成功打开 PDF 文件: {file_path}")
                reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(reader.pages)
                
                print(f"PDF 文件 {file_path.name} 共有 {num_pages} 页")
                
                # 提取每一页的文本
                for page_num in range(num_pages):
                    try:
                        page = reader.pages[page_num]
                        page_text = page.extract_text() or f"[空白页 {page_num+1}]"
                        text_content += f"第 {page_num+1} 页:\n{page_text}\n\n"
                        print(f"已提取第 {page_num+1}/{num_pages} 页文本, 长度: {len(page_text)} 字符")
                    except Exception as page_err:
                        print(f"提取第 {page_num+1} 页文本时出错: {page_err}")
                        text_content += f"[无法提取第 {page_num+1} 页]\n\n"
            
            # 创建 langchain Document 对象并添加必需的元数据字段
            metadata = {
                "source": str(file_path),
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_type": "pdf",
                "page_count": num_pages,
                # 添加必需元数据字段
                "index": 0,  # 默认索引
                "original_file_name": file_path.name  # 原始文件名
            }
            
            print(f"处理完成, 提取的文本长度: {len(text_content)} 字符")
            
            # 检查文本是否为空
            if not text_content.strip():
                print("警告: 提取的文本为空!")
                text_content = f"[PDF文件 {file_path.name} 无法提取文本内容]"
            
            # 返回文档列表
            result = [Document(page_content=text_content, metadata=metadata)]
            print(f"成功创建文档对象, 数量: {len(result)}")
            print(f"文档元数据: {metadata}")
            return result
            
        except Exception as e:
            print(f"处理 PDF 文件时出错: {str(e)}")
            traceback.print_exc()
            raise

def create_pdf_processors():
    """创建 PDF 处理器"""
    return CustomPDFProcessor()
