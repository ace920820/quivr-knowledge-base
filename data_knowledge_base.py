import os
import sys
import glob
from pathlib import Path
import traceback

# 设置编码以解决Windows中文环境的问题
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

# 确保控制台可以正确显示中文
import locale
print(f"当前系统编码: {locale.getpreferredencoding()}")

# 从环境变量加载API凭证
from dotenv import load_dotenv
load_dotenv()

# 设置OpenAI API凭证为环境变量
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
        )
        
        print(f"使用模型: gpt-3.5-turbo, 嵌入模型: OpenAIEmbeddings")
        
        # 创建Brain对象 - 直接使用OpenAI客户端
        # 注意：这里我们直接传递OpenAI客户端而不是LLMEndpoint
        print("准备创建Brain对象...")
        brain = Brain.from_files(
            name=brain_name,
            file_paths=files,
            # 不再使用llm参数，Brain内部会处理
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
        return None
    
    try:
        brains_dir = data_dir / "brains"
        save_path = brain.save(str(brains_dir))
        print(f"知识库已保存到: {save_path}")
        return save_path
    except Exception as e:
        print(f"保存知识库时出错: {str(e)}")
        return None

# 交互式问答循环
def interactive_qa(brain):
    """启动交互式问答循环"""
    if brain is None:
        print("错误: 知识库未创建成功，无法启动问答服务")
        return
    
    # 初始化聊天历史
    from langchain_core.messages import HumanMessage, AIMessage
    from uuid import uuid4
    chat_history = []
    
    print("\n" + "=" * 50)
    print("欢迎使用 Quivr 知识库问答系统!")
    print("您可以向知识库提问，输入 'exit' 或 'quit' 或 '退出' 退出对话")
    print("=" * 50 + "\n")
    
    try:
        while True:
            # 获取用户输入
            question = input("\n问题: ")
            
            # 检查退出命令
            if question.lower() in ['exit', 'quit', '退出']:
                print("感谢使用Quivr知识库，再见！")
                break
            
            # 生成每次请求的唯一run_id
            run_id = uuid4()
            
            # 获取回答
            print("正在思考...")
            
            try:
                # 直接使用Brain的ask方法，传递必要参数
                response = brain.ask(
                    run_id=run_id, 
                    question=question,
                    chat_history=chat_history
                )
                print(f"使用Brain.ask成功")
            except Exception as e:
                # 如果失败，尝试其他可能的调用方式
                print(f"Brain.ask调用失败: {e}")
                print("尝试其他方式调用ask...")
                
                try:
                    # 检查Brain类中可用的方法
                    methods = [method for method in dir(brain) if callable(getattr(brain, method)) and not method.startswith('_')]
                    print(f"Brain类的可用方法: {methods}")
                    
                    # 尝试不同参数调用ask
                    response = brain.ask(question)
                except Exception as e2:
                    print(f"替代调用也失败: {e2}")
                    # 如果所有尝试都失败，创建一个模拟的响应
                    from dataclasses import dataclass
                    
                    @dataclass
                    class MockResponse:
                        answer: str
                    
                    response = MockResponse(
                        answer=f"无法连接到知识库服务。错误: {e}"
                    )
            print("回答:")
            print(response.answer)
            print("-" * 50)
            
            # 更新聊天历史
            chat_history.append(HumanMessage(content=question))
            chat_history.append(AIMessage(content=response.answer))
    except KeyboardInterrupt:
        print("\n程序已被用户中断。谢谢使用Quivr知识库！")
    except Exception as e:
        print(f"\n处理问题时出错: {str(e)}")

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
