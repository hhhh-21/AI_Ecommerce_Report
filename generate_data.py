from pathlib import Path

import pandas as pd
import random


# 生成 28 天、5 个商品的模拟电商运营数据
def generate_sample_data():
    random.seed(42)

    products = ["无线蓝牙耳机", "便携榨汁杯", "智能台灯", "运动瑜伽垫", "家用收纳箱"]
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=28)

    rows = []
    for date in dates:
        for product in products:
            visitors = random.randint(450, 1600)
            page_views = visitors * random.randint(2, 5) + random.randint(0, 300)
            add_to_cart = int(visitors * random.uniform(0.05, 0.18))
            orders = int(visitors * random.uniform(0.018, 0.075))
            avg_price = random.uniform(59, 399)
            sales = round(orders * avg_price, 2)

            rows.append(
                {
                    "日期": date.date(),
                    "商品名称": product,
                    "访客数": visitors,
                    "浏览量": page_views,
                    "加购数": add_to_cart,
                    "订单数": orders,
                    "销售额": sales,
                }
            )

    return pd.DataFrame(rows)


if __name__ == "__main__":
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    df = generate_sample_data()
    output_file = output_dir / "sample_ecommerce_data.xlsx"
    df.to_excel(output_file, index=False)

    print(f"测试数据已生成：{output_file}")
