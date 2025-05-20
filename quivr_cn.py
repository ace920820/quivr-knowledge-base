import os
import sys
import tempfile
from pathlib import Path
import traceback

# u8bbeu7f6eu7f16u7801u4ee5u89e3u51b3Windowsu4e2du6587u73afu5883u7684u95eeu9898
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

# u8bbeu7f6eu73afu5883u53d8u91cf
os.environ["OPENAI_API_KEY"] = openai_api_key
if openai_base_url:
    os.environ["OPENAI_API_BASE"] = openai_base_url

print(f"API密钥: {openai_api_key[:5]}... | API基础URL: {openai_base_url}")

# 创建简单的知识库文件
def create_sample_file():
    # 创建示例文件夹（如果不存在）
    sample_dir = Path("sample_docs")
    sample_dir.mkdir(exist_ok=True)
    
    # 创建简单的ASCII文本文件（避免中文编码问题）
    sample_file = sample_dir / "sample_ascii.txt"
    
    with open(sample_file, "w", encoding="ascii") as f:
        f.write("Gold is a valuable metal with excellent conductivity and malleability.\n")
        f.write("It is often used in jewelry and electronics.\n")
        f.write("Gold does not corrode easily and maintains its luster over time.")
    
    print(f"创建的示例文件: {sample_file}")
    return str(sample_file)

# 主函数
def main():
    try:
        # 导入Quivr的Brain类
        from quivr_core import Brain
        
        # 创建简单的示例文件
        sample_file = create_sample_file()
        
        print("正在创建知识库...")
        # 使用简单的ASCII文件创建Brain对象
        brain = Brain.from_files(
            name="test_brain",
            file_paths=[sample_file],
        )
        
        print("知识库创建成功！")
        print(f"- 知识库名称: {brain.name}")
        
        # 询问问题（使用英文，但要求中文回答）
        question = "What are the properties of gold? Please answer in Chinese."
        print(f"\n提问: {question}")
        
        # 获取回答
        print("正在思考...")
        answer = brain.ask(question)
        print("回答:")
        print(answer)
        print("-" * 50)
        
    except Exception as e:
        print(f"错误: {str(e)}")
        print("详细错误信息:")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
