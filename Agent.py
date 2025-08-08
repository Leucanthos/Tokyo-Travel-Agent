import re
import json
import openai
from typing import Dict, List, Any, Tuple
from DataReader import DataReader
from DataWriter import DataWriter

class ReActAgent:
    """
    基于Qwen API的ReAct模式Agent，用于规划东京旅游方案
    """
    
    # 通义千问模型定价（单位：元/千tokens）
    MODEL_PRICING = {
        "qwen-flash": {"input": 0.0003, "output": 0.0006},  # 假设价格
        "qwen-plus": {"input": 0.008, "output": 0.008},     # 假设价格
        "qwen-max": {"input": 0.04, "output": 0.12}         # 假设价格
    }
    
    def __init__(self, config_path: str = "config.json", model: str = "qwen-flash", budget_limit: float = 0.1):
        """
        初始化Agent
        :param config_path: 配置文件路径
        :param model: 使用的模型，默认为qwen-flash
        :param budget_limit: 预算限制（元），默认0.1元
        """
        # 从配置文件中读取API密钥
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.client = openai.OpenAI(
            api_key=config["key"],
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = model
        self.budget_limit = budget_limit
        self.total_cost = 0.0
        self.total_tokens = {"prompt_tokens": 0, "completion_tokens": 0}
        self.data_reader = DataReader()
        self.data_writer = DataWriter()
        self.max_iterations = 10  # 最大迭代次数
        
        # 定义可用的工具
        self.tools = {
            "get_all_attractions": self.data_reader.get_all_attractions,
            "get_attraction_by_name": self.data_reader.get_attraction_by_name,
            "search_attractions": self.data_reader.search_attractions,
            "get_attractions_by_category": self.data_reader.get_attractions_by_category,
            "get_attractions_by_ward": self.data_reader.get_attractions_by_ward,
            "get_transportation_info": self.data_reader.get_transportation_info,
            "get_basic_info": self.data_reader.get_basic_info
        }
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        💰 计算API调用费用
        :param prompt_tokens: 提示token数量
        :param completion_tokens: 完成token数量
        :return: 费用（元）
        """
        if self.model not in self.MODEL_PRICING:
            # 默认使用qwen-flash的价格
            pricing = self.MODEL_PRICING["qwen-flash"]
        else:
            pricing = self.MODEL_PRICING[self.model]
        
        input_cost = (prompt_tokens / 1000.0) * pricing["input"]
        output_cost = (completion_tokens / 1000.0) * pricing["output"]
        total_cost = input_cost + output_cost
        
        return total_cost
    
    def extract_action(self, response: str) -> Tuple[str, str]:
        """
        🔍 从模型响应中提取Action和Action Input
        :param response: 模型的响应文本
        :return: (action, action_input) 元组
        """
        # 查找Action
        action_match = re.search(r"Action:\s*(.*)", response)
        action = action_match.group(1).strip() if action_match else ""
        
        # 查找Action Input
        action_input_match = re.search(r"Action Input:\s*(.*)", response)
        action_input = action_input_match.group(1).strip() if action_input_match else ""
        
        return action, action_input
    
    def execute_action(self, action: str, action_input: str) -> str:
        """
        ▶️ 执行指定的Action
        :param action: 动作名称
        :param action_input: 动作输入
        :return: 执行结果
        """
        if action in self.tools:
            try:
                # 解析参数
                if action in ["get_attraction_by_name", "get_attractions_by_category", 
                             "get_attractions_by_ward", "get_transportation_info", 
                             "get_basic_info"]:
                    # 这些函数需要一个字符串参数
                    result = self.tools[action](action_input.strip('"'))
                elif action == "search_attractions":
                    # 这个函数可能需要多个参数
                    try:
                        # 尝试解析为JSON对象
                        params = json.loads(action_input)
                        result = self.tools[action](**params)
                    except json.JSONDecodeError:
                        # 如果不是JSON，则作为关键词处理
                        result = self.tools[action](keyword=action_input.strip('"'))
                else:
                    # 这些函数不需要参数
                    result = self.tools[action]()
                
                return json.dumps(result, ensure_ascii=False, indent=2)
            except Exception as e:
                return f"执行动作时出错: {str(e)}"
        else:
            return f"未知的动作: {action}"
    
    def plan_travel(self, query: str) -> str:
        """
        🧠 使用ReAct模式规划旅游行程
        :param query: 用户的查询
        :return: 最终的回答
        """
        # 检查预算是否足够
        if self.total_cost >= self.budget_limit:
            return f"已达到预算限制（{self.budget_limit}元），无法继续执行。当前费用：{self.total_cost:.4f}元"
        
        # 初始化对话历史
        history = [
            {
                "role": "system",
                "content": """你是一个专业的东京旅游规划助手。使用ReAct模式来思考和行动。
ReAct模式包含以下步骤：
1. Thought: 分析当前情况并决定下一步行动
2. Action: 从以下可用工具中选择一个执行
   - get_all_attractions: 获取所有景点信息
   - get_attraction_by_name: 获取特定景点详细信息，需要提供景点名称
   - search_attractions: 搜索景点，可以提供关键词、分类、区域等参数
   - get_attractions_by_category: 根据分类获取景点，需要提供分类名称
   - get_attractions_by_ward: 根据区域获取景点，需要提供区域名称
   - get_transportation_info: 获取景点的交通信息，需要提供景点名称
   - get_basic_info: 获取景点的基本信息，需要提供景点名称
3. Observation: 观察工具执行结果
4. 重复以上步骤直到可以回答用户问题

请严格按照以下格式输出：
Thought: 你的思考过程
Action: 工具名称
Action Input: 工具参数

最终回答用户问题时，请提供详细的旅游规划建议。
"""
            },
            {
                "role": "user",
                "content": query
            }
        ]
        
        # 开始ReAct循环
        for i in range(self.max_iterations):
            # 检查预算是否足够
            if self.total_cost >= self.budget_limit:
                return f"已达到预算限制（{self.budget_limit}元），无法继续执行。当前费用：{self.total_cost:.4f}元"
            
            # 获取模型响应
            response = self.client.chat.completions.create(
                model=self.model,
                messages=history,
                temperature=0.7
            )
            
            # 获取token使用情况
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            
            # 计算费用
            cost = self.calculate_cost(prompt_tokens, completion_tokens)
            
            # 更新总计
            self.total_cost += cost
            self.total_tokens["prompt_tokens"] += prompt_tokens
            self.total_tokens["completion_tokens"] += completion_tokens
            
            answer = response.choices[0].message.content
            history.append({"role": "assistant", "content": answer})
            
            # 检查是否需要执行Action
            action, action_input = self.extract_action(answer)
            
            # 如果没有Action，说明已经得到最终答案
            if not action:
                # 在最终回答中添加费用信息
                cost_info = f"\n\n费用信息：本次对话消耗 {prompt_tokens + completion_tokens} tokens，费用约为 {cost:.4f} 元。总计消耗 {self.total_tokens['prompt_tokens'] + self.total_tokens['completion_tokens']} tokens，总费用 {self.total_cost:.4f} 元。"
                return answer + cost_info
            
            # 执行Action并获取Observation
            observation = self.execute_action(action, action_input)
            
            # 添加Observation到历史中
            observation_message = f"Observation: {observation}"
            history.append({"role": "user", "content": observation_message})
        
        return f"抱歉，我无法在限定的步骤内完成您的请求。当前费用：{self.total_cost:.4f}元"