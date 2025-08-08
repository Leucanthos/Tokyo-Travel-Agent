import polars as pl
import json
from typing import Dict, List, Any, Optional

class DataReader:
    """
    数据读取类，负责从数据库读取东京旅游相关数据
    """
    
    def __init__(self, db_path: str = "tokyo_attractions.parquet"):
        """
        初始化数据读取器
        :param db_path: 数据库文件路径
        """
        self.db_path = db_path
    
    # =============================================================================
    # 数据库操作基础功能
    # =============================================================================
    
    def _load_data(self) -> pl.DataFrame:
        """
        🔍 从数据库加载数据
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
    
    # =============================================================================
    # 数据转换功能
    # =============================================================================
    
    def _df_to_dict_list(self, df: pl.DataFrame) -> List[Dict[str, Any]]:
        """
        🔄 将DataFrame转换为字典列表
        :param df: DataFrame
        :return: 字典列表
        """
        result = []
        for row in df.iter_rows(named=True):
            # 处理特殊字段
            processed_row = dict(row)
            
            # 处理categories字段
            if processed_row["categories"]:
                processed_row["categories"] = processed_row["categories"].split(",")
            else:
                processed_row["categories"] = []
            
            # 处理nearby_attractions字段
            if processed_row["nearby_attractions"]:
                processed_row["nearby_attractions"] = processed_row["nearby_attractions"].split(",")
            else:
                processed_row["nearby_attractions"] = []
            
            # 处理transportation字段
            if processed_row["transportation"]:
                try:
                    processed_row["transportation"] = json.loads(processed_row["transportation"])
                except json.JSONDecodeError:
                    processed_row["transportation"] = {}
            else:
                processed_row["transportation"] = {}
            
            result.append(processed_row)
        
        return result
    
    # =============================================================================
    # 数据查询功能
    # =============================================================================
    
    def get_all_attractions(self) -> List[Dict[str, Any]]:
        """
        📋 获取所有景点信息
        :return: 景点信息列表
        """
        df = self._load_data()
        return self._df_to_dict_list(df)
    
    def get_attraction_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        🎯 根据名称获取特定景点信息
        :param name: 景点名称
        :return: 景点信息或None
        """
        df = self._load_data()
        filtered_df = df.filter(pl.col("name") == name)
        
        if filtered_df.height == 0:
            return None
        
        result = self._df_to_dict_list(filtered_df)
        return result[0] if result else None
    
    def search_attractions(self, keyword: str = "", category: str = "", ward: str = "") -> List[Dict[str, Any]]:
        """
        🔍 搜索景点
        :param keyword: 关键词（景点名称或描述中包含）
        :param category: 分类
        :param ward: 区域
        :return: 符合条件的景点列表
        """
        df = self._load_data()
        
        # 应用过滤条件
        if keyword:
            df = df.filter(
                (pl.col("name").str.contains(keyword, literal=True)) |
                (pl.col("description").str.contains(keyword, literal=True)) |
                (pl.col("address").str.contains(keyword, literal=True))
            )
        
        if category:
            df = df.filter(pl.col("categories").str.contains(category, literal=True))
        
        if ward:
            df = df.filter(pl.col("ward") == ward)
        
        return self._df_to_dict_list(df)
    
    def get_attractions_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        🏷️ 根据分类获取景点
        :param category: 分类
        :return: 属于该分类的景点列表
        """
        return self.search_attractions(category=category)
    
    def get_attractions_by_ward(self, ward: str) -> List[Dict[str, Any]]:
        """
        📍 根据区域获取景点
        :param ward: 区域
        :return: 属于该区域的景点列表
        """
        return self.search_attractions(ward=ward)
    
    # =============================================================================
    # 特定信息查询功能
    # =============================================================================
    
    def get_transportation_info(self, name: str) -> Dict[str, str]:
        """
        🚌 获取景点的交通信息
        :param name: 景点名称
        :return: 交通信息
        """
        attraction = self.get_attraction_by_name(name)
        if attraction and "transportation" in attraction:
            try:
                return json.loads(attraction["transportation"])
            except json.JSONDecodeError:
                return {}
        return {}
    
    def get_basic_info(self, name: str) -> Dict[str, str]:
        """
        📄 获取景点的基本信息
        :param name: 景点名称
        :return: 基本信息
        """
        attraction = self.get_attraction_by_name(name)
        if attraction:
            return {
                "name": attraction.get("name", ""),
                "description": attraction.get("description", ""),
                "address": attraction.get("address", ""),
                "ticket_price": attraction.get("ticket_price", ""),
                "opening_hours": attraction.get("opening_hours", ""),
                "recommended_duration": attraction.get("recommended_duration", "")
            }
        return {}