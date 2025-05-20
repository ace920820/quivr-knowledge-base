# u8fd9u662fu4e00u4e2au4feeu590du7248u7684interactive_qau51fdu6570

def interactive_qa(brain):
    """u542fu52a8u4ea4u4e92u5f0fu95eeu7b54u5faau73af"""
    if brain is None:
        print("u9519u8bef: u77e5u8bc6u5e93u672au521bu5efau6210u529fuff0cu65e0u6cd5u542fu52a8u95eeu7b54u670du52a1")
        return
    
    # u521du59cbu5316u804au5929u5386u53f2
    try:
        from langchain_core.messages import HumanMessage, AIMessage
    except ImportError:
        print("u8b66u544a: langchain_coreu672au5b89u88c5uff0cu5c06u65e0u6cd5u8bb0u5f55u804au5929u5386u53f2")
        HumanMessage = AIMessage = lambda content: type('Message', (), {'content': content})
    
    chat_history = []
    
    print("\n" + "=" * 50)
    print("u6b22u8fceu4f7fu7528 Quivr u77e5u8bc6u5e93u95eeu7b54u7cfbu7edf!")
    print("u60a8u53efu4ee5u5411u77e5u8bc6u5e93u63d0u95eeuff0cu8f93u5165 'exit' u6216 'quit' u6216 'u9000u51fa' u9000u51fau5bf9u8bdd")
    print("=" * 50 + "\n")
    
    # u521bu5efau4e8bu4ef6u5faau73af
    try:
        import asyncio
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        while True:
            # u83b7u53d6u7528u6237u8f93u5165
            question = input("\nu95eeu9898: ")
            
            # u68c0u67e5u9000u51fau547du4ee4
            if question.lower() in ['exit', 'quit', 'u9000u51fa']:
                print("u611fu8c22u4f7fu7528Quivru77e5u8bc6u5e93uff0cu518du89c1uff01")
                break
            
            # u83b7u53d6u56deu7b54
            print("u6b63u5728u601du8003...")
            
            # u68c0u67e5Brainu7c7bu4e2du53efu7528u7684u65b9u6cd5
            methods = [method for method in dir(brain) if callable(getattr(brain, method)) and not method.startswith('_')]
            print(f"Brainu7c7bu7684u53efu7528u65b9u6cd5: {methods}")
            
            # u67e5u770bbrainu7684u4fe1u606f
            try:
                info = brain.info()
                print(f"Brain ID: {info.brain_id}")
                doc_count = 'u672au77e5'
                if hasattr(info, 'documents') and info.documents is not None:
                    doc_count = len(info.documents)
                print(f"Brainu4e2du6587u6863u603bu6570: {doc_count}")
            except Exception as info_err:
                print(f"u83b7u53d6Brainu4fe1u606fu5931u8d25: {info_err}")
            
            # u9ed8u8ba4u54cdu5e94uff0cu5982u679cu6240u6709u65b9u6cd5u90fdu5931u8d25u65f6u4f7fu7528
            from dataclasses import dataclass
            @dataclass
            class MockResponse:
                answer: str
            
            response = None
            
            # u5148u5c1du8bd5u4f7fu7528asearchu76f4u63a5u68c0u7d22u6587u6863
            print("u5148u76f4u63a5u8fdbu884cu6587u6863u68c0u7d22...")
            search_results = None
            try:
                # u53eau4f7fu7528queryu53c2u6570uff0cu4e0du4f20u9012u989du5916u53c2u6570
                search_results = loop.run_until_complete(brain.asearch(query=question))
                
                if search_results and len(search_results) > 0:
                    print(f"u6587u6863u641cu7d22u7ed3u679cu6570u91cf: {len(search_results)}")
                    print("u641cu7d22u5230u7684u7b2cu4e00u4e2au6587u6863u7247u6bb5:")
                    print("----u5185u5bb9u5f00u59cb----")
                    # u68c0u67e5SearchResultu5bf9u8c61u7684u7ed3u6784u5e76u6b63u786eu8bbfu95eeu5185u5bb9
                    result = search_results[0]
                    if hasattr(result, 'page_content'):
                        # langchainu6587u6863u683cu5f0f
                        content = result.page_content
                        metadata = result.metadata if hasattr(result, 'metadata') else {}
                    elif hasattr(result, 'content'):
                        # u53efu80fdu662fQuivru81eau5b9au4e49u683cu5f0f
                        content = result.content
                        metadata = result.metadata if hasattr(result, 'metadata') else {}
                    elif hasattr(result, 'text'):
                        # u53efu80fdu662fu53e6u4e00u79cdu683cu5f0f
                        content = result.text
                        metadata = result.metadata if hasattr(result, 'metadata') else {}
                    elif hasattr(result, 'chunk') and hasattr(result.chunk, 'page_content'):
                        # u5305u542bu5728chunku5c5eu6027u4e2du7684Document
                        content = result.chunk.page_content
                        metadata = result.chunk.metadata if hasattr(result.chunk, 'metadata') else {}
                    else:
                        # u5904u7406u672au77e5u683cu5f0f
                        content = str(result)
                        metadata = {}
                        # u5c1du8bd5u68c0u67e5u7ed3u679cu5bf9u8c61u7684u6240u6709u5c5eu6027
                        print("u641cu7d22u7ed3u679cu5bf9u8c61u7684u5c5eu6027:", dir(result))
                    
                    print(content)
                    print("----u5185u5bb9u7ed3u675f----")
                    print("----u5143u6570u636e----")
                    print(metadata)
                    print("----u5143u6570u636eu7ed3u675f----")
                else:
                    print("u8b66u544a: u641cu7d22u672au8fd4u56deu4efbu4f55u6587u6863uff01u8fd9u53efu80fdu662fu95eeu9898u6240u5728u3002")
            except Exception as search_err:
                print(f"u641cu7d22u51fau9519: {search_err}")
                import traceback
                traceback.print_exc()
            
            # u5982u679cu6709u641cu7d22u7ed3u679cuff0cu5c1du8bd5u6784u9020u77e5u8bc6u5e93u5217u8868
            from quivr_core.rag.entities.models import QuivrKnowledge
            from langchain_core.documents import Document
            from pathlib import Path
            import inspect
            from uuid import uuid4
            
            result_chunks = []
            
            if search_results and len(search_results) > 0:
                print(f"u5c06u5e94u7528 {len(search_results)} u6761u641cu7d22u7ed3u679cu4f5cu4e3au56deu7b54u4e0au4e0bu6587...")
                
                # u4eceu641cu7d22u7ed3u679cu4e2du63d0u53d6u5185u5bb9u548cu5143u6570u636e
                for i, result in enumerate(search_results[:3]):
                    try:
                        # u63d0u53d6SearchResultu4e2du7684Document
                        if hasattr(result, 'chunk') and isinstance(result.chunk, Document):
                            chunk = result.chunk
                            result_chunks.append(chunk)
                            print(f"u5df2u63d0u53d6 SearchResult u4e2du7684 Document: {chunk.page_content[:100]}...")
                        elif hasattr(result, 'page_content'):
                            # u6807u51c6Documentu5bf9u8c61
                            result_chunks.append(result)
                    except Exception as extract_err:
                        print(f"u63d0u53d6u641cu7d22u7ed3u679cu4fe1u606fu65f6u51fau9519: {extract_err}")
                
                print(f"u5c06u4f7fu7528 {len(result_chunks)} u6761u6587u6863u6765u8fdbu884cu56deu7b54")
            
            # u5c1du8bd5u4f7fu7528aasku65b9u6cd5u83b7u53d6u56deu7b54
            print("u8c03u7528aasku65b9u6cd5u83b7u53d6u56deu7b54...")
            try:
                # u83b7u53d6Brain.aasku65b9u6cd5u7684u53c2u6570u4fe1u606f
                aask_params = str(inspect.signature(brain.aask))
                print(f"Brain.aasku65b9u6cd5u7684u53c2u6570: {aask_params}")
                
                print("u5f00u59cbu8fdbu884cRAGu68c0u7d22u5e76u56deu7b54u95eeu9898...")
                
                if result_chunks:
                    # u5c1du8bd5u8fd4u56deu6307u5b9au6587u4ef6u7684u56deu7b54(u4f7fu7528list_filesu53c2u6570)
                    knowledge_docs = []
                    for doc in result_chunks:
                        if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                            try:
                                # u4f7fu7528u6587u6863u6765u6e90u548cu5185u5bb9u6784u5efau77e5u8bc6u6761u76ee
                                # u6839u636eu6d4bu8bd5uff0cQuivrKnowledgeu5fc5u987bu63d0u4f9bfile_nameu53c2u6570
                                file_name = doc.metadata.get('file_name', 'u672au77e5u6587u4ef6')
                                if not file_name.strip():
                                    file_name = Path(doc.metadata.get('source', 'u672au77e5u6587u4ef6')).name
                                    
                                knowledge_item = QuivrKnowledge(
                                    id=str(uuid4()),  # u751fu6210u4e00u4e2au968fu673au7684UUIDu4f5cu4e3aID
                                    file_name=file_name  # u5fc5u586bu53c2u6570
                                )
                                knowledge_docs.append(knowledge_item)
                                print(f"u6dfbu52a0u77e5u8bc6u6761u76ee: {knowledge_item.file_name}")
                            except Exception as k_err:
                                print(f"u521bu5efau77e5u8bc6u6761u76eeu65f6u51fau9519: {k_err}")
                                # u5c1du8bd5u7b80u5316u53c2u6570uff0cu53eau4f7fu7528u5fc5u8981u7684u53c2u6570
                                try:
                                    # u7b80u5316u7248u672cu7684u77e5u8bc6u6761u76eeu521bu5efa
                                    knowledge_item = QuivrKnowledge(
                                        id=str(uuid4()),
                                        file_name="backup_knowledge_item.txt"
                                    )
                                    knowledge_docs.append(knowledge_item)
                                    print(f"u4f7fu7528u5907u7528u53c2u6570u521bu5efau77e5u8bc6u6761u76ee: {knowledge_item.file_name}")
                                except Exception as backup_err:
                                    print(f"u5907u7528u77e5u8bc6u6761u76eeu521bu5efau4e5fu5931u8d25: {backup_err}")
                                    traceback.print_exc()
                    
                    if knowledge_docs:
                        print(f"u6b63u5728u4f7fu7528 {len(knowledge_docs)} u4e2au77e5u8bc6u6761u76eeu56deu7b54u95eeu9898")
                        response = loop.run_until_complete(brain.aask(
                            question=question,
                            list_files=knowledge_docs,
                            chat_history=chat_history
                        ))
                    else:
                        # u9ed8u8ba4u8c03u7528
                        print("u4f7fu7528u9ed8u8ba4u65b9u5f0fu8c03u7528aask")
                        response = loop.run_until_complete(brain.aask(
                            question=question,
                            chat_history=chat_history
                        ))
                else:
                    # u5982u679cu6ca1u6709u9884u5904u7406u7684u6587u6863uff0cu7528u4e00u822cu8c03u7528
                    response = loop.run_until_complete(brain.aask(
                        question=question,
                        chat_history=chat_history
                    ))
                
                print("u4f7fu7528Brain.aasku6210u529f")
            except Exception as call_err:
                print(f"u8c03u7528aasku51fau9519: {call_err}")
                traceback.print_exc()
                
                # u5c1du8bd5u6700u7b80u5355u7684u8c03u7528u65b9u5f0f
                try:
                    print("u5c1du8bd5u6700u7b80u5355u7684u8c03u7528u65b9u5f0f...")
                    response = loop.run_until_complete(brain.aask(question=question))
                    print("u4f7fu7528Brain.aasku6210u529f (u7b80u5355u6a21u5f0f)")
                except Exception as simple_err:
                    print(f"u7b80u5355u8c03u7528u4e5fu5931u8d25: {simple_err}")
                    # u5982u679cu6240u6709u65b9u5f0fu90fdu5931u8d25uff0cu521bu5efau6a21u62dfu54cdu5e94
                    response = MockResponse(answer=f"u65e0u6cd5u8fdeu63a5u5230u77e5u8bc6u5e93u670du52a1u3002u9519u8bef: {call_err}")
            
            # u6253u5370u56deu7b54
            print("u56deu7b54:")
            if response:
                print(response.answer)
            else:
                print("u672au80fdu83b7u53d6u6709u6548u56deu7b54")
            print("-" * 50)
            
            # u66f4u65b0u804au5929u5386u53f2 (u5982u679cu56deu7b54u6709u6548)
            if response:
                chat_history.append(HumanMessage(content=question))
                chat_history.append(AIMessage(content=response.answer))
    except KeyboardInterrupt:
        print("\nu7a0bu5e8fu5df2u88abu7528u6237u4e2du65adu3002u8c22u8c22u4f7fu7528Quivru77e5u8bc6u5e93uff01")
    except Exception as e:
        print(f"\nu5904u7406u95eeu9898u65f6u51fau9519: {str(e)}")
        traceback.print_exc()
