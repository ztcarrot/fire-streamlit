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
│   ├── ui/                 # UI 组件
│   │   └── charts.py       # 图表
│   └── utils/              # 工具函数
│       ├── presets.py      # 预设管理
│       └── file_handler.py # 文件处理
├── config/                 # 配置文件
│   └── presets.json        # 预设配置
└── docs/                   # 文档
    └── plans/              # 设计文档
```

## 使用说明

### 1. 输入参数
在左侧边栏输入您的财务参数,包括:
- 基础信息(年龄、退休年龄等)
- 薪资信息(当前月薪、当地平均工资等)
- 高级参数(增长率、比例等)

### 2. 使用预设
从下拉菜单选择预设场景:
- 保守策略: 低增长、高开销
- 中性策略: 中等参数
- 乐观策略: 高增长、低开销

### 3. 多场景对比
选择多个场景进行对比分析

### 4. 导出结果
点击"导出结果到 Excel"下载完整报告

## 技术栈

- **Streamlit**: Web 框架
- **Plotly**: 交互式图表
- **Pandas**: 数据处理
- **NumPy**: 数值计算

## 部署

### 本地部署

1. Clone 本仓库
2. 安装依赖: `pip install -r requirements.txt`
3. 运行: `streamlit run app.py`

### Streamlit Cloud 部署

1. Fork 本仓库到您的 GitHub
2. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
3. 点击 "New app"
4. 选择您的仓库
5. 点击 "Deploy"

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request!
