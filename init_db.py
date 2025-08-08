import polars as pl
import os

def init_database():
    """
    初始化数据库，创建景点数据表
    """
    # 定义数据模式
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
        "categories": pl.Utf8,  # 以逗号分隔的字符串存储
        "transportation": pl.Utf8,  # JSON字符串存储
        "nearby_attractions": pl.Utf8,  # 以逗号分隔的字符串存储
        "website": pl.Utf8,
        "phone": pl.Utf8,
        "last_updated": pl.Utf8
    }
    
    # 创建空的DataFrame
    df = pl.DataFrame(schema=schema)
    
    # 保存为Parquet格式
    df.write_parquet("tokyo_attractions.parquet")
    
    print("数据库初始化完成，已创建 tokyo_attractions.parquet 文件")

def load_initial_data():
    """
    加载初始数据到数据库
    """
    # 初始数据
    data = [
        {
            "name": "浅草寺",
            "city": "东京",
            "ward": "台东区",
            "description": "东京最古老的寺庙，雷门是其标志性入口",
            "address": "东京都台东区浅草2-3-1",
            "latitude": 35.714702,
            "longitude": 139.796708,
            "ticket_price": "免费",
            "opening_hours": "全天开放",
            "recommended_duration": "1-2小时",
            "categories": "寺庙,文化,历史",
            "transportation": '{"地铁": "银座线浅草站步行5分钟", "JR": "山手線上野站步行10分钟"}',
            "nearby_attractions": "浅草文化观光中心,雷门",
            "website": "https://www.senso-ji.jp/",
            "phone": "+81-3-3842-0181",
            "last_updated": "2025-08-09"
        },
        {
            "name": "东京塔",
            "city": "东京",
            "ward": "港区",
            "description": "东京的标志性建筑之一，高333米",
            "address": "东京都港区芝公园4-2-8",
            "latitude": 35.658581,
            "longitude": 139.745433,
            "ticket_price": "大人1200日元",
            "opening_hours": "9:00-23:00",
            "recommended_duration": "2-3小时",
            "categories": "观景台,地标,现代建筑",
            "transportation": '{"地铁": "大江户线赤羽桥站步行5分钟", "JR": "山手线浜松町站步行15分钟"}',
            "nearby_attractions": "芝公园,增上寺",
            "website": "https://www.tokyotower.co.jp/",
            "phone": "+81-3-3433-5111",
            "last_updated": "2025-08-09"
        },
        {
            "name": "明治神宫",
            "city": "东京",
            "ward": "涩谷区",
            "description": "供奉明治天皇的神社，位于繁华市中心的一片绿地",
            "address": "东京都涩谷区代代木神园町1-1",
            "latitude": 35.676391,
            "longitude": 139.699309,
            "ticket_price": "免费",
            "opening_hours": "全年开放",
            "recommended_duration": "1-2小时",
            "categories": "神社,自然,文化",
            "transportation": '{"地铁": "千代田线明治神宫前站步行5分钟", "JR": "山手线原宿站步行10分钟"}',
            "nearby_attractions": "代代木公园,原宿竹下通",
            "website": "https://www.meijijingu.or.jp/",
            "phone": "+81-3-3371-1407",
            "last_updated": "2025-08-09"
        },
        {
            "name": "涩谷十字路口",
            "city": "东京",
            "ward": "涩谷区",
            "description": "世界最繁忙的十字路口之一",
            "address": "东京都涩谷区涩谷1-3-20",
            "latitude": 35.659934,
            "longitude": 139.700532,
            "ticket_price": "免费",
            "opening_hours": "全天开放",
            "recommended_duration": "1小时",
            "categories": "地标,现代,购物",
            "transportation": '{"地铁": "银座线、半藏门线、副都心线涩谷站", "JR": "山手线涩谷站"}',
            "nearby_attractions": "涩谷天空,109百货",
            "website": "https://www.shibuya.city.tokyo.jp/",
            "phone": "",
            "last_updated": "2025-08-09"
        },
        {
            "name": "新宿御苑",
            "city": "东京",
            "ward": "新宿区",
            "description": "融合日式、英式、法式风格的庭园",
            "address": "东京都新宿区内藤町5-1",
            "latitude": 35.681093,
            "longitude": 139.728639,
            "ticket_price": "大人500日元",
            "opening_hours": "9:00-16:30",
            "recommended_duration": "2-3小时",
            "categories": "庭园,自然,休闲",
            "transportation": '{"地铁": "丸之内线新宿御苑前站", "JR": "JR线新宿站南口步行5分钟"}',
            "nearby_attractions": "新宿中央公园,明治神宫外苑",
            "website": "https://www.env.go.jp/garden/shinjukugyoen/",
            "phone": "+81-3-3343-5555",
            "last_updated": "2025-08-09"
        }
    ]
    
    # 创建DataFrame并保存
    df = pl.DataFrame(data)
    df.write_parquet("tokyo_attractions.parquet")
    
    print("初始数据已加载到数据库")

if __name__ == "__main__":
    if not os.path.exists("tokyo_attractions.parquet"):
        load_initial_data()
    else:
        print("数据库文件已存在")