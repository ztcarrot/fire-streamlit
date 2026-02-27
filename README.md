# 家庭收支预测系统 - Streamlit 版

基于 Streamlit 的家庭财务预测工具,帮助您规划未来财务状况。

## 功能特性

- ✅ 完整的收支预测计算
- ✅ 交互式图表展示
- ✅ 多场景对比分析
- ✅ 参数预设管理
- ✅ 数据导入导出
- ✅ 关键节点标注

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
streamlit run app.py
```

应用将在浏览器中打开,默认地址为 `http://localhost:8501`

## 项目结构

```
fire-streamlit/
├── app.py                  # 应用入口
├── src/                    # 源代码
│   ├── calculator.py       # 计算逻辑
│   ├── models.py           # 数据模型
│   └── ui/                 # UI 组件
├── config/                 # 配置文件
└── docs/                   # 文档
```

## 使用说明

详见 [docs/plans/2025-02-28-family-finance-streamlit-design.md](docs/plans/2025-02-28-family-finance-streamlit-design.md)

## 部署

本项目部署在 Streamlit Cloud: [https://fire-streamlit.streamlit.app](https://fire-streamlit.streamlit.app)

## 许可证

MIT License
