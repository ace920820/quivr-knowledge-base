import os
import glob
import json
from pathlib import Path
import tempfile
import shutil
import time
import sys
import traceback

# 设置编码以解决Windows中文环境的问题
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

# 检测系统编码
print(f"当前系统编码: {sys.getdefaultencoding()}")

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()  # 加载.env文件中的环境变量
except ImportError:
    print("警告: python-dotenv库未安装, 无法加载.env文件")

# 获取OpenAI API密钥和基础URL
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL")

# 格式化API基础URL
if openai_base_url and not openai_base_url.endswith('/v1'):
    openai_base_url = f"{openai_base_url.rstrip('/')}/v1"

# 设置环境变量
os.environ["OPENAI_API_KEY"] = openai_api_key
if openai_base_url:
    os.environ["OPENAI_API_BASE"] = openai_base_url

print(f"API密钥: {openai_api_key[:5] if openai_api_key else '未设置'}... | API基础URL: {openai_base_url}")

# 创建必要的目录结构
def create_data_directories():
    """创建数据目录结构"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # 创建子目录
    (data_dir / "documents").mkdir(exist_ok=True)  # 存放原始文档
    (data_dir / "processed").mkdir(exist_ok=True)  # 存放处理后的文档
    (data_dir / "brains").mkdir(exist_ok=True)    # 存放知识库模型
    
    # 创建一个简单说明文件
    readme_path = data_dir / "README.md"
    if not readme_path.exists():
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("""\
# 数据目录说明

本目录用于存放quivr知识库相关数据文件。

## 目录结构

- `documents/`: 存放原始文档文件，支持txt, pdf等格式
- `processed/`: 存放处理后的文档
- `brains/`: 存放已保存的知识库模型

## 用法

1. 将您的文档放入 `documents/` 目录
2. 运行知识库程序加载这些文档
3. 生成的知识库将保存在 `brains/` 中
            """)
    
    return data_dir

# 创建示例文档（如果不存在）
def create_sample_document(data_dir):
    """创建示例文档如果不存在"""
    docs_dir = data_dir / "documents"
    sample_file = docs_dir / "sample_info.txt"
    
    if not sample_file.exists():
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("""\
知识库示例文档

人工智能简介：
人工智能（AI）是计算机科学的一个分支，致力于开发能够模拟人类智能的系统。它的目标是创造可以学习、推理、感知、解决问题和决策的机器。

人工智能的应用领域：
1. 自然语言处理：包括机器翻译、文本生成和语音识别等。
2. 计算机视觉：光学字符识别、人脸识别和物体探测等。
3. 机器学习：数据分析、模式识别和预测分析。
4. 智能机器人学：自动驾驶、工业机器人和聊天机器人。
5. 游戏开发：智能游戏角色和自动游戏生成。

Quivr知识库简介：
Quivr是一个基于人工智能的知识库系统，可以处理多种格式的文档并使用先进的生成式AI技术取得关联信息。它支持PDF、文本文件等多种格式，并能够回答基于其知识库的问题。
            """)
        print(f"创建了示例文档: {sample_file}")
    else:
        print(f"示例文档已存在: {sample_file}")
    
    return str(sample_file)

# 收集知识库文档
def collect_documents(data_dir, extensions=None):
    """从指定目录收集文档"""
    if extensions is None:
        extensions = [".txt", ".pdf", ".md", ".doc", ".docx"]  # 默认支持的文件类型
    
    docs_dir = data_dir / "documents"
    files = []
    
    # 递归查找所有匹配的文件
    for ext in extensions:
        files.extend(list(docs_dir.glob(f"**/*{ext}")))
    
    if not files:
        print(f"警告: 在 {docs_dir} 中没有找到支持的文档。")
        return []
    
    print(f"共找到 {len(files)} 个文档:")
    for file in files:
        print(f"- {file.relative_to(data_dir)}")
    
    return [str(f) for f in files]

# 创建Quivr知识库并加载文档
def create_brain_from_documents(files, brain_name="data_knowledge_base"):
    """从文档列表创建知识库"""
    try:
        # 加载Quivr核心类
        import sys
        import os
        from uuid import uuid4
        import asyncio
        from pathlib import Path
        from langchain_core.documents import Document
        
        # 导入所需的模块
        from importlib import import_module
        
        # 声明全局变量
        global CustomPDFProcessor
        CustomPDFProcessor = None
        
        # 检查是否有PDF文件
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if pdf_files:
            print(f"检测到{len(pdf_files)}个PDF文件，将使用自定义处理器")
            try:
                # 尝试导入我们的自定义PDF处理器
                module = import_module('custom_pdf_processor')
                CustomPDFProcessor = module.CustomPDFProcessor
                print("成功导入自定义PDF处理器")
            except ImportError as e:
                print(f"未找到自定义PDF处理器，将尝试其他方法: {e}")
        
        # 添加core目录到Python路径
        core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core')
        if core_path not in sys.path:
            sys.path.append(core_path)
            print(f"已添加路径到sys.path: {core_path}")
        
        try:
            # 只导入Brain类，不使用LLMEndpoint
            from quivr_core import Brain
            print("成功从本地quivr_core导入Brain")
        except ImportError as e:
            print(f"导入本地Brain时出错: {e}")
            raise
        
        print("正在创建知识库...")
        # 创建Brain对象，按照官方示例配置
        from langchain_openai import OpenAIEmbeddings
        
        # 使用OpenAI API作为默认模型
        from openai import OpenAI
        
        # 创建OpenAI客户端
        client = OpenAI(
            api_key=openai_api_key,
            base_url=openai_base_url
        )
        
        # 测试OpenAI客户端连接
        try:
            # 发送简单请求测试连接
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print(f"OpenAI API连接测试成功: {response.choices[0].message.content}")
        except Exception as e:
            print(f"OpenAI API连接测试失败: {e}")
        
        # 创建OpenAI嵌入模型
        embedder = OpenAIEmbeddings(
            openai_api_key=openai_api_key,
            openai_api_base=openai_base_url or None,
            model="text-embedding-3-small"  # 使用最新的嵌入模型
        )
        
        print(f"使用模型: gpt-3.5-turbo, 嵌入模型: text-embedding-3-small")
        
        # 检查是否有PDF文件，如果有，使用我们的自定义处理器
        pdf_files = [f for f in files if str(f).lower().endswith('.pdf')]
        
        if pdf_files and CustomPDFProcessor is not None:
            print(f"开始手动处理 {len(pdf_files)} 个 PDF 文件")
            
            # 手动处理PDF文件，生成文档对象
            text_documents = []
            
            try:
                # 实例化我们的自定义PDF处理器
                # 创建 CustomPDFProcessor 实例
                pdf_processor = CustomPDFProcessor()
                print(f"已创建PDF处理器实例: {type(pdf_processor).__name__}")
                
                # 创建事件循环
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    # 如果当前线程没有事件循环，创建一个新的
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    print("创建了新的事件循环")
                
                # 处理每个PDF文件
                for pdf_file in pdf_files:
                    print(f"处理PDF文件: {pdf_file}")
                    try:
                        # 直接调用处理函数，不使用异步
                        docs = loop.run_until_complete(pdf_processor.process_file(pdf_file))
                        if docs:
                            text_documents.extend(docs)
                            print(f"成功处理PDF文件: {pdf_file}, 提取了 {len(docs)} 个文档")
                        else:
                            print(f"警告: {pdf_file} 没有提取到内容")
                    except Exception as e:
                        print(f"处理PDF文件 {pdf_file} 时出错: {str(e)}")
                        print(traceback.format_exc())
                
                print(f"共处理了 {len(text_documents)} 个文档")
                
                # 如果我们成功提取了文本，则构建知识库
                if text_documents:
                    print("使用提取的文本构建知识库...")
                    # 尝试使用正确的Brain方法来处理文档
                    try:
                        # 打印Brain类所有可用的方法，帮助确定正确的方法名
                        methods = [m for m in dir(Brain) if not m.startswith('_') and callable(getattr(Brain, m))]
                        print(f"Brain类的可用方法: {methods}")
                        
                        # 使用正确的afrom_langchain_documents方法
                        # 首先创建异步事件循环
                        event_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(event_loop)
                        
                        # 调用异步方法
                        brain = event_loop.run_until_complete(Brain.afrom_langchain_documents(
                            name=brain_name,
                            langchain_documents=text_documents,
                            embedder=embedder
                        ))
                        print("使用自定义处理器成功创建Brain!")
                        return brain
                    except Exception as e:
                        print(f"使用from_langchain_documents时出错: {str(e)}")
                        # 可能是方法名称不同，尝试检查可用方法
                        methods = [m for m in dir(Brain) if not m.startswith('_') and callable(getattr(Brain, m))]
                        print(f"Brain可用方法: {methods}")
            except Exception as e:
                print(f"使用自定义处理器时出错: {str(e)}")
                traceback.print_exc()
                print("将尝试使用默认方法...")
        
        # 如果没有PDF文件或自定义处理失败，则使用默认方法
        print("准备创建Brain对象...")
        try:
            # 使用最新的OpenAI embeddings模型
            embedder = OpenAIEmbeddings(
                openai_api_key=openai_api_key,
                openai_api_base=openai_base_url,
                model="text-embedding-3-small"  # 使用最新的嵌入模型
            )
            print(f"已创建OpenAI embeddings对象: {type(embedder).__name__}，模型: text-embedding-3-small")
        except Exception as e:
            print(f"创建OpenAI embeddings时出错: {str(e)}")
            print("详细错误信息:")
            traceback.print_exc()
            return None
        
        brain = Brain.from_files(
            name=brain_name,
            file_paths=files,
            embedder=embedder,
        )
        
        print("知识库创建成功！")
        
        # 打印知识库信息
        print(f"- 知识库名称: {brain.name}")
        print(f"- 知识库ID: {brain.id}")
        
        return brain
    except Exception as e:
        print(f"创建知识库时出错: {str(e)}")
        print("详细错误信息:")
        print(traceback.format_exc())
        return None

# 保存知识库供未来使用
def save_brain(brain, data_dir):
    """保存知识库供未来使用"""
    if brain is None:
        print("错误: 传入的brain对象为空")
        return None
    
    try:
        # 生成保存路径
        brains_dir = data_dir / "brains"
        save_path = brains_dir / f"{brain.info().brain_id}.zip"
        
        # 保存brain - 异步方法需要特殊处理
        import asyncio
        
        # 获取或创建事件循环
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # 执行保存操作
        saved_path = loop.run_until_complete(brain.save(save_path))
        print(f"知识库已保存到: {saved_path}")
        return save_path
    except Exception as e:
        print(f"保存知识库时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# 交互式问答循环
def interactive_qa(brain):
    """启动交互式问答循环"""
    if brain is None:
        print("错误: 知识库未创建成功，无法启动问答服务")
        return
    
    # 初始化聊天历史
    try:
        from langchain_core.messages import HumanMessage, AIMessage
    except ImportError:
        print("警告: langchain_core未安装，将无法记录聊天历史")
        HumanMessage = AIMessage = lambda content: type('Message', (), {'content': content})
    
    chat_history = []
    
    print("\n" + "=" * 50)
    print("欢迎使用 Quivr 知识库问答系统!")
    print("您可以向知识库提问，输入 'exit' 或 'quit' 或 '退出' 退出对话")
    print("=" * 50 + "\n")
    
    # 创建事件循环
    try:
        import asyncio
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        while True:
            # 获取用户输入
            question = input("\n问题: ")
            
            # 检查退出命令
            if question.lower() in ['exit', 'quit', '退出']:
                print("感谢使用Quivr知识库，再见！")
                break
            
            # 获取回答
            print("正在思考...")
            
            # 检查Brain类中可用的方法
            methods = [method for method in dir(brain) if callable(getattr(brain, method)) and not method.startswith('_')]
            print(f"Brain类的可用方法: {methods}")
            
            # 查看brain的信息
            try:
                info = brain.info()
                print(f"Brain ID: {info.brain_id}")
                doc_count = '未知'
                if hasattr(info, 'documents') and info.documents is not None:
                    doc_count = len(info.documents)
                print(f"Brain中文档总数: {doc_count}")
            except Exception as info_err:
                print(f"获取Brain信息失败: {info_err}")
            
            # 默认响应，如果所有方法都失败时使用
            from dataclasses import dataclass
            @dataclass
            class MockResponse:
                answer: str
            
            response = None
            
            # 先尝试使用asearch直接检索文档
            print("先直接进行文档检索...")
            search_results = None
            try:
                # 只使用query参数，不传递额外参数
                search_results = loop.run_until_complete(brain.asearch(query=question))
                
                if search_results and len(search_results) > 0:
                    print(f"文档搜索结果数量: {len(search_results)}")
                    print("搜索到的第一个文档片段:")
                    print("----内容开始----")
                    print(f"{search_results[0].page_content}")
                    print("----内容结束----")
                    print("----元数据----")
                    print(f"{search_results[0].metadata}")
                    print("----元数据结束----")
                else:
                    print("警告: 搜索未返回任何文档！这可能是问题所在。")
            except Exception as search_err:
                print(f"搜索出错: {search_err}")
                import traceback
                traceback.print_exc()
            
            # 尝试使用aask方法获取回答
            print("调用aask方法获取回答...")
            try:
                # 获取Brain.aask方法的参数信息
                import inspect
                aask_params = str(inspect.signature(brain.aask))
                print(f"Brain.aask方法的参数: {aask_params}")
                
                # 不使用额外参数，只传递必需的参数
                try:
                    # 先尝试最简单的调用方式，只传递question
                    response = loop.run_until_complete(brain.aask(question=question))
                    print("使用Brain.aask成功 (简单模式)")
                except Exception as simple_err:
                    print(f"简单模式调用失败: {simple_err}")
                    
                    # 如果简单模式失败，尝试添加chat_history参数
                    response = loop.run_until_complete(brain.aask(
                        question=question,
                        chat_history=chat_history
                    ))
                    print("使用Brain.aask成功 (带聊天历史)")
            except Exception as e:
                print(f"Brain.aask调用失败: {e}")
                import traceback
                traceback.print_exc()
                print("尝试其他方式...")
                
                # 如果所有方法都失败，创建一个模拟的响应
                response = MockResponse(
                    answer=f"无法连接到知识库服务。错误: {e}"
                )
            
            # 打印回答
            print("回答:")
            if response:
                print(response.answer)
            else:
                print("未能获取有效回答")
            print("-" * 50)
            
            # 更新聊天历史 (如果回答有效)
            if response:
                chat_history.append(HumanMessage(content=question))
                chat_history.append(AIMessage(content=response.answer))
    except KeyboardInterrupt:
        print("\n程序已被用户中断。谢谢使用Quivr知识库！")
    except Exception as e:
        print(f"\n处理问题时出错: {str(e)}")
        import traceback
        traceback.print_exc()

# 主程序
def main():
    """主程序入口"""
    print("=" * 50)
    print("Quivr 本地知识库测试程序")
    print("=" * 50)
    
    # 创建数据目录
    data_dir = create_data_directories()
    print(f"已创建数据目录: {data_dir}")
    
    # # 创建示例文档
    # sample_doc = create_sample_document(data_dir)
    # print(f"示例文档路径: {sample_doc}")
    
    # 收集文档
    print("\n正在收集文档...")
    documents = collect_documents(data_dir)
    
    if not documents:
        print("错误: 没有找到可用的文档。请将文档添加到 'data/documents' 目录中")
        return
    
    # 创建知识库
    brain = create_brain_from_documents(documents)
    
    if brain is None:
        print("错误: 知识库创建失败。")
        return
    
    # 保存知识库
    save_path = save_brain(brain, data_dir)
    
    # 启动问答模式
    interactive_qa(brain)

if __name__ == "__main__":
    main()
