# Tokyo-Travel-Agent

My Tokyo Travel Agent.

## 项目介绍

这是一个基于Qwen API和ReAct模式的东京旅游规划助手。Agent可以根据用户需求，通过思考-行动-观察的循环过程，智能地规划东京旅游行程。

## 功能特点

- 使用ReAct（Reasoning + Action）模式实现智能决策
- 提供东京景点、交通、美食等信息查询
- 根据用户需求生成个性化旅游方案
- 支持多轮交互和动态信息获取
- 实时计算token使用量和费用
- 支持预算限制，防止花费过多
- 以景点为单元的数据管理，支持增删改查
- AI驱动的非结构化数据转换为结构化数据
- 数据读写分离，使用Polars与Parquet数据库进行交互
- 统一的数据写入接口，支持结构化和非结构化数据

## 安装依赖

```bash
pip install openai polars
```

## 配置API密钥

1. 在[阿里云DashScope平台](https://dashscope.aliyuncs.com/)申请Qwen API密钥
2. 将密钥添加到`config.json`文件中：
```json
{
    "key": "your-qwen-api-key"
}
```

## 初始化数据库

运行初始化脚本创建数据库：

```bash
python init_db.py
```

## 使用方法

```python
from Agent import ReActAgent

# 初始化Agent（默认使用qwen-flash模型，预算限制为0.1元）
agent = ReActAgent()

# 提出旅游规划请求
result = agent.plan_travel("我想去东京旅游，帮我规划一个3天的行程")
print(result)
```

如果需要自定义参数：
```python
# 使用qwen-max模型，预算限制为0.05元
agent = ReActAgent(model="qwen-max", budget_limit=0.05)
```

## 项目结构

- `Agent.py`: 实现ReAct模式的Agent核心逻辑
- `DataReader.py`: 数据读取模块
- `DataWriter.py`: 数据写入模块
- `init_db.py`: 数据库初始化脚本
- `config.json`: API密钥配置文件
- `tokyo_attractions.parquet`: 东京景点数据文件（Parquet格式）
- `example.py`: 使用示例

## 工作原理

Agent使用ReAct模式工作，包含以下步骤：

1. **Thought**: 分析当前情况并决定下一步行动
2. **Action**: 从可用工具中选择一个执行
3. **Observation**: 观察工具执行结果
4. 重复以上步骤直到可以回答用户问题

### 可用工具

- `get_all_attractions`: 获取所有景点信息
- `get_attraction_by_name`: 获取特定景点详细信息，需要提供景点名称
- `search_attractions`: 搜索景点，可以提供关键词、分类、区域等参数
- `get_attractions_by_category`: 根据分类获取景点，需要提供分类名称
- `get_attractions_by_ward`: 根据区域获取景点，需要提供区域名称
- `get_transportation_info`: 获取景点的交通信息，需要提供景点名称
- `get_basic_info`: 获取景点的基本信息，需要提供景点名称

## 数据管理

### 数据结构

景点数据以结构化方式存储，包含以下字段：

- `name`: 景点名称
- `city`: 城市
- `ward`: 区域
- `description`: 描述
- `address`: 地址
- `latitude/longitude`: 经纬度
- `ticket_price`: 门票价格
- `opening_hours`: 开放时间
- `recommended_duration`: 推荐游览时长
- `categories`: 分类标签
- `transportation`: 交通信息
- `nearby_attractions`: 附近景点
- `website`: 官网
- `phone`: 电话
- `last_updated`: 最后更新时间

### 数据操作

```python
from DataReader import DataReader
from DataWriter import DataWriter

# 初始化数据读取器和写入器
reader = DataReader()
writer = DataWriter()

# 读取数据
all_attractions = reader.get_all_attractions()
attraction = reader.get_attraction_by_name("景点名称")
search_results = reader.search_attractions(keyword="关键词", category="分类", ward="区域")

# 写入数据
new_attraction = {
    "name": "景点名称",
    "city": "东京",
    "ward": "区域",
    # ... 其他字段
}
writer.add_attraction(new_attraction)

# 更新景点
writer.update_attraction("景点名称", {"ticket_price": "新价格"})

# 删除景点
writer.delete_attraction("景点名称")

# 统一接口添加数据 - 结构化
structured_data = {
    "name": "景点名称",
    "city": "东京",
    "ward": "区域",
    # ... 其他字段
}
writer.add_attraction_data(True, structured_data)

# 统一接口添加数据 - 非结构化（将由AI处理为结构化数据）
unstructured_text = "关于某个景点的非结构化描述..."
writer.add_attraction_data(False, unstructured_text)
```

### 数据库

本项目使用Polars库与Parquet格式文件进行数据存储：

- 数据库文件: `tokyo_attractions.parquet`
- 使用Parquet格式提供高效的列式存储和查询性能
- 支持复杂数据类型存储（如JSON字符串）

### AI数据提取

系统支持使用AI从非结构化文本中提取结构化数据：

```python
# 从非结构化文本中提取景点信息
text = "东京晴空塔是一座高634米的塔，位于墨田区..."
writer.add_attraction_data(False, text)
```

## 费用计算和预算限制

Agent会自动计算每次API调用的token使用量和费用，并支持设置预算限制：

- **Token计数**: 自动统计prompt tokens和completion tokens
- **费用计算**: 根据模型定价自动计算费用
- **预算限制**: 可设置预算上限，防止花费过多

默认模型定价（元/千tokens）：
- qwen-flash: 输入0.0003，输出0.0006
- qwen-plus: 输入0.008，输出0.008
- qwen-max: 输入0.04，输出0.12

## 安全说明

- `config.json`文件已被添加到`.gitignore`中，不会被提交到Git仓库
- 请确保不要手动将API密钥提交到版本控制系统中

## 自定义数据

可以通过修改`DataWriter.py`中的数据来添加更多景点、交通方式和美食信息。