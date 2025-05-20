# u6d4bu8bd5ChatHistoryu7c7bu7684u4f7fu7528u65b9u6cd5

import os
import sys
import traceback
from pathlib import Path

# u6dfbu52a0coreu76eeu5f55u5230Pythonu8defu5f84
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core')
if core_path not in sys.path:
    sys.path.append(core_path)
    print(f"u5df2u6dfbu52a0u8defu5f84u5230sys.path: {core_path}")

try:
    # u5bfcu5165ChatHistoryu7c7b
    from quivr_core.rag.entities.chat import ChatHistory
    from uuid import uuid4
    
    # u521bu5efau4e00u4e2aChatHistoryu5bf9u8c61
    chat_id = str(uuid4())
    brain_id = str(uuid4())
    chat_history = ChatHistory(chat_id=chat_id, brain_id=brain_id)
    
    # u83b7u53d6u5bf9u8c61u5c5eu6027u548cu65b9u6cd5
    print(f"ChatHistoryu5bf9u8c61u5c5eu6027u548cu65b9u6cd5: {dir(chat_history)}")
    
    # u6d4bu8bd5u6dfbu52a0u6d88u606f
    from langchain_core.messages import HumanMessage, AIMessage
    
    # u68c0u67e5appendu65b9u6cd5
    try:
        print("\nu6d4bu8bd5u4f7fu7528appendu65b9u6cd5:")
        chat_history.append(HumanMessage(content="u6d4bu8bd5u95eeu9898"))
        chat_history.append(AIMessage(content="u6d4bu8bd5u56deu7b54"))
        print("u6210u529fu4f7fu7528appendu65b9u6cd5u6dfbu52a0u6d88u606f")
        print(f"\u6d88\u606f\u5185\u5bb9: {chat_history.messages}")
    except Exception as e:
        print(f"\u4f7f\u7528append\u65b9\u6cd5\u51fa\u9519: {e}")
        traceback.print_exc()
    
    # u68c0u67e5add_messageu65b9u6cd5
    try:
        print("\nu6d4bu8bd5u4f7fu7528add_messageu65b9u6cd5:")
        chat_history.add_message(HumanMessage(content="u53e6u4e00u4e2au6d4bu8bd5u95eeu9898"))
        chat_history.add_message(AIMessage(content="u53e6u4e00u4e2au6d4bu8bd5u56deu7b54"))
        print("u6210u529fu4f7fu7528add_messageu65b9u6cd5u6dfbu52a0u6d88u606f")
        print(f"\u6d88\u606f\u5185\u5bb9: {chat_history.messages}")
    except Exception as e:
        print(f"\u4f7f\u7528add_message\u65b9\u6cd5\u51fa\u9519: {e}")
        traceback.print_exc()
    
    # u68c0u67e5u76f4u63a5u5199u5165messagesu5c5eu6027
    try:
        print("\nu6d4bu8bd5u76f4u63a5u64cdu4f5cmessagesu5c5eu6027:")
        if hasattr(chat_history, 'messages'):
            chat_history.messages.append(HumanMessage(content="u4f7fu7528messagesu5c5eu6027u76f4u63a5u6dfbu52a0"))
            chat_history.messages.append(AIMessage(content="u4f7fu7528messagesu5c5eu6027u76f4u63a5u56deu7b54"))
            print("u6210u529fu76f4u63a5u5411messagesu5c5eu6027u6dfbu52a0u6d88u606f")
            print(f"\u6d88\u606f\u5185\u5bb9: {chat_history.messages}")
        else:
            print("ChatHistoryu5bf9u8c61u6ca1u6709messagesu5c5eu6027")
    except Exception as e:
        print(f"\u64cd\u4f5cmessages\u5c5e\u6027\u51fa\u9519: {e}")
        traceback.print_exc()
    
    # u68c0u67e5u5176u4ed6u6dfbu52a0u65b9u6cd5
    possible_methods = [
        'add', 'add_message', 'add_user_message', 'add_assistant_message',
        'append', 'extend', 'insert'
    ]
    
    for method in possible_methods:
        if hasattr(chat_history, method):
            print(f"ChatHistoryu5bf9u8c61u6709{method}u65b9u6cd5")
    
    # u6253u5370ChatHistoryu7c7bu7684u5b9au4e49u6e90u7801u4f4du7f6e
    import inspect
    print(f"\nChatHistoryu7c7bu7684u5b9au4e49u6587u4ef6: {inspect.getfile(ChatHistory)}")
    
    # u5c1du8bd5u63a5u6536u4e24u4e2au53c2u6570u521bu5efau65b9u6cd5
    if hasattr(chat_history, 'create'):
        print("\nu6d4bu8bd5u4f7fu7528createu65b9u6cd5:")
        chat_history.create("user", "u4f7fu7528createu65b9u6cd5u6d4bu8bd5")
        print("u6210u529fu4f7fu7528createu65b9u6cd5")
    else:
        print("\nChatHistoryu5bf9u8c61u6ca1u6709createu65b9u6cd5")
    
    # u5c1du8bd5u67e5u770bu5b9eu9645u7c7bu578b
    print(f"\nChatHistoryu5bf9u8c61u7684u7c7bu578b: {type(chat_history).__name__}")
    print(f"ChatHistoryu7c7bu7684u5185u5bb9: {chat_history}")
    
    # u6253u5370u7236u7c7bu7684u65b9u6cd5
    print(f"\nChatHistoryu7c7bu7684u7236u7c7b: {ChatHistory.__bases__}")
    for base in ChatHistory.__bases__:
        print(f"{base.__name__}u7c7bu7684u65b9u6cd5: {[m for m in dir(base) if not m.startswith('_')]}")
    
except Exception as e:
    print(f"u51fau9519: {e}")
    traceback.print_exc()
