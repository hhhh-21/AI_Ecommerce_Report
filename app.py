from io import StringIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="电商运营数据 AI 周报助手", layout="wide")

# 设置中文字体，避免商品销售额图表中的中文乱码
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False


# 读取上传的 Excel 文件
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df["日期"] = pd.to_datetime(df["日期"])
    return df


# 补充基础运营指标
def add_metrics(df):
    df = df.copy()
    df["转化率"] = df["订单数"] / df["访客数"]
    df["加购率"] = df["加购数"] / df["访客数"]
    df["客单价"] = df["销售额"] / df["订单数"].replace(0, pd.NA)
    df["客单价"] = df["客单价"].fillna(0)
    return df


# 按最近 7 天和前 7 天拆分数据
def split_weeks(df):
    latest_date = df["日期"].max()
    this_week_start = latest_date - pd.Timedelta(days=6)
    last_week_start = latest_date - pd.Timedelta(days=13)
    last_week_end = latest_date - pd.Timedelta(days=7)

    this_week = df[df["日期"].between(this_week_start, latest_date)]
    last_week = df[df["日期"].between(last_week_start, last_week_end)]
    return this_week, last_week, this_week_start, latest_date, last_week_start, last_week_end


# 汇总一段时间内的核心指标
def summarize(df):
    visitors = df["访客数"].sum()
    orders = df["订单数"].sum()
    sales = df["销售额"].sum()
    conversion_rate = orders / visitors if visitors else 0
    avg_order_value = sales / orders if orders else 0

    return {
        "销售额": sales,
        "访客数": visitors,
        "订单数": orders,
        "转化率": conversion_rate,
        "客单价": avg_order_value,
    }


def growth_rate(current, previous):
    if previous == 0:
        return 0
    return (current - previous) / previous


# 识别需要关注的运营异常
def find_alerts(sales_growth, visitor_growth, conversion_change, this_conversion):
    alerts = []

    if sales_growth < -0.15:
        alerts.append("销售额明显下降")
    if visitor_growth > 0.10 and conversion_change < -0.01:
        alerts.append("流量增长但转化下降")
    if this_conversion < 0.035:
        alerts.append("本周转化率偏低")

    if not alerts:
        alerts.append("暂无明显异常")
    return alerts


# 生成可复制给大模型的周报 Prompt
def build_prompt(this_summary, last_summary, sales_growth, visitor_growth, conversion_change, alerts):
    alert_text = "\n".join("- " + alert for alert in alerts)
    return f"""
请你扮演一名资深电商运营分析师，根据以下经营数据生成一份结构清晰、结论明确、建议可执行的电商运营周报。

【本周核心数据】
- 销售额：{this_summary["销售额"]:.2f} 元
- 订单数：{this_summary["订单数"]} 单
- 访客数：{this_summary["访客数"]} 人
- 转化率：{this_summary["转化率"]:.2%}
- 客单价：{this_summary["客单价"]:.2f} 元

【上周核心数据】
- 销售额：{last_summary["销售额"]:.2f} 元
- 订单数：{last_summary["订单数"]} 单
- 访客数：{last_summary["访客数"]} 人
- 转化率：{last_summary["转化率"]:.2%}
- 客单价：{last_summary["客单价"]:.2f} 元

【环比变化】
- 销售额环比：{sales_growth:.2%}
- 访客数环比：{visitor_growth:.2%}
- 转化率变化：{conversion_change:.2%}

【系统识别的异常】
{alert_text}

请输出：
1. 本周经营概览
2. 关键变化解读
3. 可能原因分析
4. 下周运营动作建议
5. 适合发给老板的 5 句话总结
""".strip()


st.title("电商运营数据 AI 周报助手")
st.caption("面向电商运营场景的周报分析小工具：上传 Excel，自动计算关键指标、识别异常，并生成可复制给大模型的周报 Prompt。")

with st.expander("项目说明", expanded=False):
    st.write(
        "本项目适合作为数据分析 / 运营分析方向的作品集案例，覆盖数据读取、指标计算、周度对比、异常识别、可视化和 Prompt 生成。"
    )
    st.write("测试文件路径：data/sample_ecommerce_data.xlsx")

uploaded_file = st.file_uploader("上传电商运营 Excel 文件", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("请先上传 Excel 文件。可以先运行 generate_data.py 生成 data/sample_ecommerce_data.xlsx 作为测试数据。")
    st.stop()

try:
    raw_df = load_data(uploaded_file)
except Exception as error:
    st.error(f"文件读取失败：{error}")
    st.stop()

required_columns = ["日期", "商品名称", "访客数", "浏览量", "加购数", "订单数", "销售额"]
missing_columns = [col for col in required_columns if col not in raw_df.columns]
if missing_columns:
    st.error("文件缺少必要字段：" + "、".join(missing_columns))
    st.stop()

df = add_metrics(raw_df)
this_week, last_week, this_start, this_end, last_start, last_end = split_weeks(df)
this_summary = summarize(this_week)
last_summary = summarize(last_week)

sales_growth = growth_rate(this_summary["销售额"], last_summary["销售额"])
visitor_growth = growth_rate(this_summary["访客数"], last_summary["访客数"])
conversion_change = this_summary["转化率"] - last_summary["转化率"]
alerts = find_alerts(sales_growth, visitor_growth, conversion_change, this_summary["转化率"])

st.subheader("原始数据预览")
st.dataframe(df.head(30), use_container_width=True)

st.subheader("本周核心指标")
col1, col2, col3, col4 = st.columns(4)
col1.metric("本周销售额", f"¥{this_summary['销售额']:,.2f}", f"{sales_growth:.2%}")
col2.metric("本周订单数", f"{this_summary['订单数']:,}")
col3.metric("本周访客数", f"{this_summary['访客数']:,}", f"{visitor_growth:.2%}")
col4.metric("整体转化率", f"{this_summary['转化率']:.2%}", f"{conversion_change:.2%}")

st.subheader("周度对比")
compare_df = pd.DataFrame(
    [
        {"指标": "销售额", "本周": this_summary["销售额"], "上周": last_summary["销售额"], "变化": sales_growth},
        {"指标": "访客数", "本周": this_summary["访客数"], "上周": last_summary["访客数"], "变化": visitor_growth},
        {"指标": "转化率", "本周": this_summary["转化率"], "上周": last_summary["转化率"], "变化": conversion_change},
        {"指标": "客单价", "本周": this_summary["客单价"], "上周": last_summary["客单价"], "变化": growth_rate(this_summary["客单价"], last_summary["客单价"])},
    ]
)
st.dataframe(compare_df, use_container_width=True)

st.write(f"本周范围：{this_start.date()} 至 {this_end.date()}")
st.write(f"上周范围：{last_start.date()} 至 {last_end.date()}")

st.subheader("异常识别")
for alert in alerts:
    if alert == "暂无明显异常":
        st.success(alert)
    else:
        st.warning(alert)

st.subheader("商品销售额对比")
st.caption("图表说明：按商品汇总最近 7 天与前 7 天销售额，单位为元；柱体上方展示对应销售额，便于快速比较商品表现。")

product_compare = (
    pd.concat(
        [
            this_week.groupby("商品名称")["销售额"].sum().rename("本周销售额"),
            last_week.groupby("商品名称")["销售额"].sum().rename("上周销售额"),
        ],
        axis=1,
    )
    .fillna(0)
    .sort_values("本周销售额", ascending=False)
)

fig, ax = plt.subplots(figsize=(11, 5.5))
product_compare.plot(kind="bar", ax=ax, color=["#2f80ed", "#f2994a"], width=0.72)
ax.set_title("商品销售额周度对比", fontsize=15, pad=16)
ax.set_xlabel("商品名称", fontsize=11)
ax.set_ylabel("销售额（元）", fontsize=11)
ax.legend(title="统计周期", loc="upper right")
ax.grid(axis="y", linestyle="--", alpha=0.35)

# 为每根柱子补充销售额数值标签
for container in ax.containers:
    ax.bar_label(container, fmt="%.0f", padding=3, fontsize=8)

plt.xticks(rotation=30, ha="right")
plt.tight_layout()
st.pyplot(fig)

st.subheader("可复制运营周报 Prompt")
prompt = build_prompt(this_summary, last_summary, sales_growth, visitor_growth, conversion_change, alerts)
st.text_area("复制下面内容到 ChatGPT / DeepSeek / 通义千问", prompt, height=440)

st.subheader("下载分析结果")
result_df = df.copy()
result_df["日期"] = result_df["日期"].dt.strftime("%Y-%m-%d")
csv_buffer = StringIO()
result_df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
st.download_button(
    label="下载分析结果 CSV",
    data=csv_buffer.getvalue(),
    file_name="ecommerce_weekly_analysis.csv",
    mime="text/csv",
)
