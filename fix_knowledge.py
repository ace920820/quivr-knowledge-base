# 这是一个辅助脚本，用于修复QuivrKnowledge参数问题

import sys
from pathlib import Path
import inspect

# 设置Python路径
core_path = str(Path(".") / "core")
if core_path not in sys.path:
    sys.path.append(core_path)

# 导入需要的类
try:
    from quivr_core.rag.entities.models import QuivrKnowledge
    print("成功导入QuivrKnowledge类")
    
    # 打印QuivrKnowledge的构造参数
    print(f"QuivrKnowledge的构造函数: {inspect.signature(QuivrKnowledge.__init__)}")
    
    # 测试创建一个实例
    from uuid import uuid4
    test_knowledge = QuivrKnowledge(
        id=str(uuid4()),
        # 尝试不同的参数组合
        name="测试知识",
        file_path="测试路径"
    )
    print(f"成功创建QuivrKnowledge实例: {test_knowledge}")
    print(f"可用属性: {dir(test_knowledge)}")
    
    # 再尝试另一种参数组合
    test_knowledge2 = QuivrKnowledge(
        id=str(uuid4()),
        file_name="测试文件.pdf", 
        file_path="测试路径/测试文件.pdf"
    )
    print(f"成功创建第二个QuivrKnowledge实例: {test_knowledge2}")
    
    # 再尝试第三种参数组合
    test_knowledge3 = QuivrKnowledge(
        id=str(uuid4())
    )
    print(f"成功创建第三个QuivrKnowledge实例: {test_knowledge3}")
    
except ImportError as e:
    print(f"无法导入QuivrKnowledge类: {e}")
except Exception as e:
    print(f"创建QuivrKnowledge示例时出错: {e}")
