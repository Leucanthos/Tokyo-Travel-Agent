"""
使用示例：展示如何使用ReActAgent规划东京旅游
"""

from Agent import ReActAgent
from DataReader import DataReader
from DataWriter import DataWriter

def main():
    # 演示数据读取功能
    print("=== 数据读取功能演示 ===")
    data_reader = DataReader()
    
    # 获取所有景点
    print("📋 获取所有景点:")
    all_attractions = data_reader.get_all_attractions()
    for attraction in all_attractions[:3]:  # 只显示前3个
        print(f"- {attraction['name']}: {attraction['description']}")
    
    # 根据名称获取特定景点
    print("\n🎯 获取特定景点(浅草寺):")
    temple = data_reader.get_attraction_by_name("浅草寺")
    if temple:
        print(f"名称: {temple['name']}")
        print(f"描述: {temple['description']}")
        print(f"区域: {temple['ward']}")
        print(f"交通: {temple['transportation']}")
    
    # 搜索景点
    print("\n🔍 搜索'迪士尼'相关景点：")
    disney_attractions = data_reader.search_attractions(keyword="迪士尼")
    for attraction in disney_attractions:
        print(f"- {attraction['name']}: {attraction['description']}")
    
    # 根据分类获取景点
    print("\n🏷️ 获取'寺庙'分类的景点：")
    temple_attractions = data_reader.get_attractions_by_category("寺庙")
    for attraction in temple_attractions:
        print(f"- {attraction['name']}: {attraction['description']}")
    
    # 根据区域获取景点
    print("\n📍 获取'台东区'的景点：")
    taito_attractions = data_reader.get_attractions_by_ward("台东区")
    for attraction in taito_attractions:
        print(f"- {attraction['name']}: {attraction['description']}")
    
    # 演示新宿区景点查询
    print("\n🏢 获取'新宿区'的景点：")
    shinjuku_attractions = data_reader.get_attractions_by_ward("新宿区")
    for attraction in shinjuku_attractions:
        print(f"- {attraction['name']}: {attraction['description']}")
    
    # 演示数据写入功能
    print("\n=== 数据写入功能演示 ===")
    data_writer = DataWriter()
    
    # =====================================================
    # 使用结构化数据添加景点
    # =====================================================
    print("\n🧩 使用结构化数据添加景点:")
    structured_attraction = {
        "name": "东京迪士尼乐园",
        "city": "东京",
        "ward": "浦安市",
        "description": "东京迪士尼乐园是东京迪士尼度假区的一部分，拥有多个主题区域",
        "address": "东京都浦安市舞滨1-1",
        "latitude": 35.634800,
        "longitude": 139.879800,
        "ticket_price": "大人8200日元",
        "opening_hours": "8:00-22:00",
        "recommended_duration": "1天",
        "categories": ["主题公园", "娱乐", "家庭"],
        "transportation": {
            "JR": "JR京叶线舞滨站步行5分钟"
        },
        "nearby_attractions": ["东京迪士尼海洋"],
        "website": "https://www.tokyodisneyresort.jp/tdl/",
        "phone": "+81-50-3377-3000"
    }
    
    # 使用统一接口添加结构化数据
    if data_writer.add_attraction_data(True, structured_attraction):
        print("✅ 成功添加新景点：东京迪士尼乐园")
    else:
        print("❌ 添加新景点失败")
    
    # =====================================================
    # 使用非结构化数据添加景点
    # =====================================================
    print("\n📝 使用非结构化数据添加景点:")
    unstructured_text = """
    东京晴空塔（Tokyo Skytree）是位于日本东京都墨田区的一座巨型高塔，高度为634米，
    是世界上第二高的建筑结构。晴空塔的主要功能包括观光、广播和餐饮。塔内设有两个观景台，
    分别位于350米和450米的高度。地址是东京都墨田区押上1-1-2。开放时间通常是早上8点到晚上9点。
    门票价格根据楼层不同而异，大约在2000-3000日元之间。推荐游览时长为2-3小时。
    可以乘坐东京地铁半藏门线到押上站，然后步行约3分钟即可到达。
    附近有隅田公园和东京晴空塔城等景点。
    官方网站是https://www.tokyo-skytree.jp/，电话是+81-50-3377-3000。
    """
    
    # 使用统一接口添加非结构化数据
    if data_writer.add_attraction_data(False, unstructured_text):
        print("✅ 成功从非结构化文本中提取并添加景点：东京晴空塔")
    else:
        print("❌ 从非结构化文本中提取景点失败")
    
    # 从config.json中读取API密钥
    # 确保config.json文件存在且包含有效的API密钥
    
    # 创建Agent实例，默认使用qwen-flash模型，预算限制为0.1元
    agent = ReActAgent()
    
    # 如果需要自定义预算限制，可以这样设置（例如限制为0.05元）
    # agent = ReActAgent(budget_limit=0.05)
    
    # 示例查询
    query = "我想去东京旅游，帮我规划一个3天的行程，包括景点、美食和交通建议，特别关注新宿区的景点"
    
    # 获取旅游规划
    travel_plan = agent.plan_travel(query)
    
    print("\n=== 旅游规划结果 ===")
    print(travel_plan)

if __name__ == "__main__":
    main()