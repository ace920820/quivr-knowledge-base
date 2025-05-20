# Quivr 本地知识库应用

基于Quivr框架的本地知识库应用，支持多种文档格式和自然语言问答。

## 项目说明

本项目使用Quivr核心框架创建了一个本地知识库应用，能够：

- **加载多种格式文档**：支持TXT、PDF等多种格式
- **创建知识库**：使用Quivr的Brain类建立知识库
- **自然语言问答**：基于知识库内容回答问题
- **支持中文**：完全支持中文问答和显示

## 如何使用

### 安装依赖

```bash
# 创建并激活conda环境
conda create -n quivr python=3.11
conda activate quivr

# 安装所需依赖
pip install quivr-core python-dotenv rich
```

### 配置API密钥

在项目根目录创建`.env`文件，添加以下内容：

```
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=your_api_base_url_here  # 可选，如使用OpenAI API代理
```

### 运行示例

```bash
# 运行知识库示例
python quivr_cn.py
```

## 功能演示

此示例创建一个简单知识库，加载示例文本文件，然后允许用户用自然语言提问。

```python
# 创建知识库
brain = Brain.from_files(
    name="test_brain",
    file_paths=[sample_file],
)

# 询问问题
answer = brain.ask("What are the properties of gold? Please answer in Chinese.")
print(answer)
```

## 扩展功能

您可以通过以下方式扩展本应用：

1. **添加更多文档**：修改代码加载更多文档
2. **支持更多格式**：Quivr本身支持多种文档格式
3. **自定义检索配置**：通过YAML配置文件自定义检索策略
4. **保存知识库**：使用`brain.save()`保存知识库供未来使用

## 注意事项

- 在Windows中文环境下，可能遇到编码问题，本项目已针对此问题进行了优化
- 使用时请确保您的API密钥有效
- 对于大型文档，请注意可能产生的API调用费用

## 许可证

本项目使用Apache 2.0许可证 - 详见[LICENSE](LICENSE)文件
