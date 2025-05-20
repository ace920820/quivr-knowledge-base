import os
import sys
import json
from pathlib import Path
import traceback
from uuid import uuid4

# 设置编码以解决Windows中文环境的问题
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()  # 加载.env文件中的环境变量
except ImportError:
    print("警告: python-dotenv库未安装, 无法加载.env文件")

# 获取OpenAI API密钥和基础URL
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL")

# 设置环境变量
os.environ["OPENAI_API_KEY"] = openai_api_key if openai_api_key else ""
if openai_base_url:
    os.environ["OPENAI_API_BASE"] = openai_base_url

print(f"API密钥: {openai_api_key[:5] if openai_api_key else '未设置'}... | API基础URL: {openai_base_url}")

# 添加core目录到Python路径
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core')
if core_path not in sys.path:
    sys.path.append(core_path)
    print(f"已添加路径到sys.path: {core_path}")

try:
    # 导入Brain类
    from quivr_core import Brain
    from quivr_core.rag.entities.models import QuivrKnowledge
    print("成功从本地quivr_core导入Brain")
    
    # 获取所有知识库目录
    brains_dir = Path("data/brains")
    if not brains_dir.exists():
        print(f"错误: 知识库目录 {brains_dir} 不存在")
        sys.exit(1)
    
    brain_dirs = []
    
    # 查找知识库目录
    for item in brains_dir.glob("**/brain_*"):
        if item.is_dir() and (item / "config.json").exists():
            brain_dirs.append(item)
    
    if not brain_dirs:
        print("错误: 未找到可用的知识库目录")
        sys.exit(1)
    
    # 按修改时间排序，获取最新的知识库
    brain_dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    brain_path = brain_dirs[0]  # 选择最新的知识库
    
    print(f"使用知识库: {brain_path}")
    
    # 显示知识库的配置信息
    config_file = brain_path / "config.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f"知识库名称: {config.get('name', 'Unknown')}")
            print(f"知识库ID: {config.get('id', 'Unknown')}")
    
    # 加载知识库
    brain = Brain.load(brain_path)
    print(f"成功加载知识库: {brain.info().brain_id}")
    
    # 创建事件循环
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # 测试问题
    question = "关于坏习惯会升级的观点是什么？"
    print(f"\n测试问题: {question}")
    
    # 先尝试直接搜索相关文档
    print("\n1. 搜索相关文档:")
    search_results = loop.run_until_complete(brain.asearch(query=question))
    
    if search_results and len(search_results) > 0:
        print(f"找到 {len(search_results)} 个相关文档")
        
        # 提取第一个结果的内容
        result = search_results[0]
        content = None
        
        # 检查并提取内容
        if hasattr(result, 'chunk') and hasattr(result.chunk, 'page_content'):
            content = result.chunk.page_content[:300] + "..."  # 只显示前300字符
            print(f"\n文档内容片段: {content}")
        else:
            print("\n无法直接提取文档内容，使用文件名作为知识条目")
        
        # 创建知识条目
        knowledge_items = []
        for i, result in enumerate(search_results[:3]):  # 只使用前3条结果
            try:
                if hasattr(result, 'chunk') and hasattr(result.chunk, 'metadata') and 'file_name' in result.chunk.metadata:
                    file_name = result.chunk.metadata['file_name']
                else:
                    file_name = f"document_{i+1}.txt"
                
                # 创建知识条目 - 只使用必要的参数
                item = QuivrKnowledge(
                    id=str(uuid4()),
                    file_name=file_name  # 必填参数
                )
                knowledge_items.append(item)
                print(f"添加知识条目: {file_name}")
            except Exception as e:
                print(f"创建知识条目时出错: {e}")
                traceback.print_exc()
        
        # 使用知识条目提问
        if knowledge_items:
            print("\n2. 使用找到的文档进行回答:")
            try:
                response = loop.run_until_complete(brain.aask(
                    question=question,
                    list_files=knowledge_items
                ))
                print("\n回答:")
                print("-" * 50)
                print(response.answer)
                print("-" * 50)
            except Exception as e:
                print(f"回答问题时出错: {e}")
                traceback.print_exc()
        else:
            print("\n没有有效的知识条目可以使用")
    else:
        print("未找到相关文档")

except Exception as e:
    print(f"出现错误: {e}")
    traceback.print_exc()
