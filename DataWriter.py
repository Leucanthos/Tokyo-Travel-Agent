import polars as pl
import json
import openai
from typing import Dict, List, Any, Union
from datetime import datetime

class DataWriter:
    """
    数据写入类，负责向数据库写入东京旅游相关数据
    """
    
    def __init__(self, db_path: str = "tokyo_attractions.parquet", config_path: str = "config.json"):
        """
        初始化数据写入器
        :param db_path: 数据库文件路径
        :param config_path: 配置文件路径
        """
        self.db_path = db_path
        self.config_path = config_path
        self._load_config()
    
    # =============================================================================
    # 配置加载相关功能
    # =============================================================================
    
    def _load_config(self) -> None:
        """
        从配置文件加载API密钥
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.api_key = config.get("key", "")
        except FileNotFoundError:
            self.api_key = ""
    
    # =============================================================================
    # 数据库操作基础功能
    # =============================================================================
    
    def _load_data(self) -> pl.DataFrame:
        """
        从数据库加载现有数据
        :return: 数据DataFrame
        """
        try:
            return pl.read_parquet(self.db_path)
        except Exception as e:
            print(f"加载数据失败: {e}")
            # 返回空的DataFrame
            schema = {
                "name": pl.Utf8,
                "city": pl.Utf8,
                "ward": pl.Utf8,
                "description": pl.Utf8,
                "address": pl.Utf8,
                "latitude": pl.Float64,
                "longitude": pl.Float64,
                "ticket_price": pl.Utf8,
                "opening_hours": pl.Utf8,
                "recommended_duration": pl.Utf8,
                "categories": pl.Utf8,
                "transportation": pl.Utf8,
                "nearby_attractions": pl.Utf8,
                "website": pl.Utf8,
                "phone": pl.Utf8,
                "last_updated": pl.Utf8
            }
            return pl.DataFrame(schema=schema)
    
    def _save_data(self, df: pl.DataFrame) -> bool:
        """
        保存数据到数据库
        :param df: 要保存的DataFrame
        :return: 是否保存成功
        """
        try:
            df.write_parquet(self.db_path)
            return True
        except Exception as e:
            print(f"保存数据失败: {e}")
            return False
    
    # =============================================================================
    # AI数据处理功能
    # =============================================================================
    
    def extract_structured_data(self, unstructured_text: str) -> Dict[str, Any]:
        """
        🤖 使用AI从非结构化文本中提取结构化数据
        :param unstructured_text: 非结构化文本
        :return: 结构化数据
        """
        if not self.api_key:
            raise ValueError("API密钥未配置")
        
        client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        prompt = f"""
        请从以下文本中提取东京景点的结构化信息，并以JSON格式返回：

        文本内容：
        {unstructured_text}

        请提取以下字段信息：
        - name: 景点名称
        - city: 城市（默认为"东京"）
        - ward: 区域（如台东区、港区等）
        - description: 景点描述
        - address: 详细地址
        - latitude: 纬度（如果不知道则填0.0）
        - longitude: 经度（如果不知道则填0.0）
        - ticket_price: 门票价格
        - opening_hours: 开放时间
        - recommended_duration: 推荐游览时长
        - categories: 分类标签（以数组形式返回，如["寺庙", "文化"]）
        - transportation: 交通信息（以字典形式返回，如{{"地铁": "银座线浅草站步行5分钟"}}）
        - nearby_attractions: 附近景点（以数组形式返回）
        - website: 官方网站
        - phone: 联系电话

        只返回JSON格式的数据，不要包含其他内容。
        """
        
        try:
            response = client.chat.completions.create(
                model="qwen-flash",
                messages=[
                    {"role": "system", "content": "你是一个专业的数据提取助手，能够从非结构化文本中提取结构化信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # 提取JSON内容
            content = response.choices[0].message.content
            # 尝试解析JSON
            structured_data = json.loads(content)
            return structured_data
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试从内容中提取JSON
            try:
                # 查找第一个{{和最后一个}}之间的内容
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = content[start:end]
                    structured_data = json.loads(json_str)
                    return structured_data
                else:
                    raise ValueError("无法从响应中提取JSON数据")
            except Exception as e:
                raise ValueError(f"数据提取失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"AI调用失败: {str(e)}")
    
    # =============================================================================
    # 统一数据写入接口
    # =============================================================================
    
    def add_attraction_data(self, is_structured: bool, input_data: Union[Dict[str, Any], str]) -> bool:
        """
        🔄 统一的数据写入接口，根据输入类型自动处理结构化或非结构化数据
        :param is_structured: 输入数据是否为结构化字典
        :param input_data: 输入数据，可以是结构化字典或非结构化文本
        :return: 是否添加成功
        """
        try:
            if is_structured and isinstance(input_data, dict):
                # 直接处理结构化数据
                return self._add_structured_attraction(input_data)
            else:
                # 处理非结构化数据
                if isinstance(input_data, str):
                    # 提取结构化数据
                    structured_data = self.extract_structured_data(input_data)
                    # 添加景点
                    return self._add_structured_attraction(structured_data)
                else:
                    raise ValueError("非结构化数据必须是字符串类型")
        except Exception as e:
            print(f"添加景点数据失败: {e}")
            return False
    
    def _add_structured_attraction(self, attraction_data: Dict[str, Any]) -> bool:
        """
        🔧 添加结构化景点数据到数据库
        :param attraction_data: 结构化的景点数据
        :return: 是否添加成功
        """
        try:
            # 检查必填字段
            required_fields = ["name", "city", "ward", "description"]
            for field in required_fields:
                if field not in attraction_data:
                    raise ValueError(f"缺少必填字段: {field}")
            
            # 设置默认值
            attraction_data.setdefault("latitude", 0.0)
            attraction_data.setdefault("longitude", 0.0)
            attraction_data.setdefault("ticket_price", "未知")
            attraction_data.setdefault("opening_hours", "未知")
            attraction_data.setdefault("recommended_duration", "未知")
            attraction_data.setdefault("categories", [])
            attraction_data.setdefault("transportation", {})
            attraction_data.setdefault("nearby_attractions", [])
            attraction_data.setdefault("website", "")
            attraction_data.setdefault("phone", "")
            attraction_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            
            # 处理特殊字段格式
            if isinstance(attraction_data["categories"], list):
                attraction_data["categories"] = ",".join(attraction_data["categories"])
            
            if isinstance(attraction_data["transportation"], dict):
                attraction_data["transportation"] = json.dumps(attraction_data["transportation"], ensure_ascii=False)
            
            if isinstance(attraction_data["nearby_attractions"], list):
                attraction_data["nearby_attractions"] = ",".join(attraction_data["nearby_attractions"])
            
            # 加载现有数据
            df = self._load_data()
            
            # 检查是否已存在同名景点
            if df.filter(pl.col("name") == attraction_data["name"]).height > 0:
                print(f"⚠️ 景点 {attraction_data['name']} 已存在")
                return False
            
            # 创建新记录
            new_record = pl.DataFrame([attraction_data])
            
            # 合并数据
            if df.height > 0:
                df = pl.concat([df, new_record])
            else:
                df = new_record
            
            # 保存数据
            return self._save_data(df)
        except Exception as e:
            print(f"添加结构化景点失败: {e}")
            return False