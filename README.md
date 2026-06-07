# 电商运营数据 AI 周报助手

一个适合放入简历和 GitHub 作品集的 Streamlit 数据分析项目。项目模拟电商运营周报场景，支持上传 Excel 数据，自动完成核心指标计算、周度对比、异常识别、商品销售额可视化，并生成可复制给 ChatGPT / DeepSeek / 通义千问的运营周报 Prompt。

## 项目亮点

- 数据处理：使用 pandas 读取 Excel，并自动计算转化率、加购率、客单价等指标。
- 周度分析：按最近 7 天作为本周、前 7 天作为上周，自动计算销售额、访客数、转化率环比变化。
- 异常识别：内置销售额下降、流量增长但转化下降、转化率偏低等业务规则。
- 可视化：使用 matplotlib 展示商品销售额周度对比柱状图，包含图例、单位、标题和数值标签。
- AI 辅助：不接入真实大模型 API，仅生成可复制的运营周报 Prompt，便于后续扩展。
- 结果导出：支持下载分析后的 CSV 文件。

## 项目结构

```text
电商运营数据AI周报助手/
├── app.py                         # Streamlit 网页应用
├── generate_data.py               # 模拟数据生成脚本
├── requirements.txt               # 项目依赖
├── README.md                      # 项目说明
└── data/
    └── sample_ecommerce_data.xlsx # 示例电商数据
```

## 快速开始

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 生成测试数据

```bash
python generate_data.py
```

3. 启动应用

```bash
streamlit run app.py
```

打开终端显示的本地地址，通常是：

```text
http://localhost:8501
```

## Excel 字段要求

上传文件需包含以下字段：

```text
日期、商品名称、访客数、浏览量、加购数、订单数、销售额
```

## 适合写进简历的描述

基于 Streamlit + pandas + matplotlib 搭建电商运营数据 AI 周报助手，实现 Excel 数据上传、核心运营指标计算、周度环比分析、异常规则识别、商品销售额可视化和大模型周报 Prompt 自动生成，帮助运营人员快速完成周报分析与决策建议整理。

## 后续可扩展方向

- 接入真实大模型 API，自动生成完整周报正文。
- 增加 SKU、渠道、店铺维度筛选。
- 增加复购率、退款率、ROI、投放消耗等更多运营指标。
- 支持导出 Word / PDF 格式周报。
