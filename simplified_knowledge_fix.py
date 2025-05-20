# u8fd9u4e2au6587u4ef6u5305u542bu6b63u786eu7684QuivrKnowledgeu8c03u7528u4ee3u7801

import sys
from pathlib import Path
import traceback
from uuid import uuid4

# u8bbeu7f6ePythonu8defu5f84
core_path = str(Path(".") / "core")
if core_path not in sys.path:
    sys.path.append(core_path)

try:
    # u5bfcu5165u9700u8981u7684u7c7b
    from quivr_core.rag.entities.models import QuivrKnowledge
    
    # u521bu5efau4e00u4e2aQuivrKnowledgeu5bf9u8c61
    knowledge = QuivrKnowledge(
        id=str(uuid4()),
        file_name="test_file.pdf",  # u8fd9u662fu5fc5u586bu5b57u6bb5
        file_path="/path/to/test_file.pdf"
    )
    
    print(f"\u6210\u529f\u521b\u5efa\u77e5\u8bc6\u6761\u76ee: {knowledge}")
    
    # u5c1du8bd5u4e0du540cu7684u7ec4u5408
    knowledge_simple = QuivrKnowledge(
        id=str(uuid4()),
        file_name="simple_file.txt"  # u53eau63d0u4f9bfile_nameu4e5fu80fdu5de5u4f5c
    )
    
    print(f"\u7b80\u5316\u7248\u77e5\u8bc6\u6761\u76ee: {knowledge_simple}")
    
except Exception as e:
    print(f"\u53d1\u751f\u9519\u8bef: {e}")
    traceback.print_exc()
