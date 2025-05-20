import os
import sys
import json
from pathlib import Path
import traceback
from uuid import uuid4

# u8bbeu7f6eu7f16u7801u4ee5u89e3u51b3Windowsu4e2du6587u73afu5883u7684u95eeu9898
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

# u52a0u8f7du73afu5883u53d8u91cf
try:
    from dotenv import load_dotenv
    load_dotenv()  # u52a0u8f7d.envu6587u4ef6u4e2du7684u73afu5883u53d8u91cf
except ImportError:
    print("u8b66u544a: python-dotenvu5e93u672au5b89u88c5, u65e0u6cd5u52a0u8f7d.envu6587u4ef6")

# u83b7u53d6OpenAI APIu5bc6u94a5u548cu57fau7840URL
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL")

# u8bbeu7f6eu73afu5883u53d8u91cf
os.environ["OPENAI_API_KEY"] = openai_api_key if openai_api_key else ""
if openai_base_url:
    os.environ["OPENAI_API_BASE"] = openai_base_url

print(f"APIu5bc6u94a5: {openai_api_key[:5] if openai_api_key else 'u672au8bbeu7f6e'}... | APIu57fau7840URL: {openai_base_url}")

# u6dfbu52a0coreu76eeu5f55u5230Pythonu8defu5f84
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core')
if core_path not in sys.path:
    sys.path.append(core_path)
    print(f"u5df2u6dfbu52a0u8defu5f84u5230sys.path: {core_path}")

def load_brain():
    try:
        # u5bfcu5165Brainu7c7b
        from quivr_core import Brain
        print("u6210u529fu4eceu672cu5730quivr_coreu5bfcu5165Brain")
        
        # u83b7u53d6u6240u6709u77e5u8bc6u5e93u76eeu5f55
        brains_dir = Path("data/brains")
        if not brains_dir.exists():
            print(f"u9519u8bef: u77e5u8bc6u5e93u76eeu5f55 {brains_dir} u4e0du5b58u5728")
            return None
        
        brain_dirs = []
        
        # u67e5u627eu77e5u8bc6u5e93u76eeu5f55
        for item in brains_dir.glob("**/brain_*"):
            if item.is_dir() and (item / "config.json").exists():
                brain_dirs.append(item)
        
        if not brain_dirs:
            print(f"u9519u8bef: u5728 {brains_dir} u4e2du672au627eu5230u53efu7528u7684u77e5u8bc6u5e93")
            return None
        
        # u6309u4feeu6539u65f6u95f4u6392u5e8fuff0cu83b7u53d6u6700u65b0u7684u77e5u8bc6u5e93
        brain_dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        brain_path = brain_dirs[0]  # u9009u62e9u6700u65b0u7684u77e5u8bc6u5e93
        
        print(f"u4f7fu7528u77e5u8bc6u5e93: {brain_path}")
        
        # u663eu793au77e5u8bc6u5e93u7684u914du7f6eu4fe1u606f
        config_file = brain_path / "config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"u77e5u8bc6u5e93u540du79f0: {config.get('name', 'Unknown')}")
                print(f"u77e5u8bc6u5e93ID: {config.get('id', 'Unknown')}")
        
        # u52a0u8f7du77e5u8bc6u5e93
        brain = Brain.load(brain_path)
        print(f"u6210u529fu52a0u8f7du77e5u8bc6u5e93: {brain.info().brain_id}")
        return brain
    except Exception as e:
        print(f"u52a0u8f7du77e5u8bc6u5e93u51fau9519: {e}")
        traceback.print_exc()
        return None

async def simple_query(brain, question):
    """u7b80u5355u76f4u63a5u67e5u8be2u77e5u8bc6u5e93"""
    try:
        print(f"\nu6b63u5728u67e5u8be2: {question}")
        # u76f4u63a5u4f7fu7528u6700u7b80u5355u7684u65b9u5f0fu8c03u7528
        response = await brain.aask(question=question)
        print("\nu56deu7b54:")
        print("-" * 50)
        print(response.answer)
        print("-" * 50)
        return response.answer
    except Exception as e:
        print(f"u67e5u8be2u65f6u51fau9519: {e}")
        traceback.print_exc()
        return f"u67e5u8be2u8fc7u7a0bu4e2du51fau9519: {e}"

async def main():
    # u52a0u8f7du77e5u8bc6u5e93
    brain = load_brain()
    if not brain:
        print("u9519u8bef: u65e0u6cd5u52a0u8f7du77e5u8bc6u5e93")
        return
    
    # u8bbeu7f6eu6d4bu8bd5u95eeu9898
    test_questions = [
        "u5173u4e8eu574fu4e60u60efu4f1au5347u7ea7u7684u89c2u70b9u662fu4ec0u4e48uff1f",
        "u6e29u6c34u716eu9752u86d9u7684u6bd4u55bbu662fu4ec0u4e48uff1f",
        "u53efu4ee5u6839u636eu77e5u8bc6u5e93u4e2du7684u4fe1u606fuff0cu63cfu8ff0u300au518du770bu4e00u773cu300bu8fd9u672cu4e66u4e3bu8981u8bb2u4e86u4ec0u4e48uff1f"
    ]
    
    # u6267u884cu67e5u8be2
    for i, question in enumerate(test_questions):
        print(f"\n[{i+1}/{len(test_questions)}] u6d4bu8bd5u95eeu9898: {question}")
        await simple_query(brain, question)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
