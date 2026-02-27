# 家庭收支预测系统 - Streamlit 版本设计文档

**日期**: 2025-02-28
**设计者**: Claude
**状态**: 已批准

## 1. 项目概述

### 1.1 项目目标

将现有的 React + TypeScript 家庭收支预测页面重构为独立的 Streamlit Python 应用,并添加增强功能。

### 1.2 核心需求

- 完全独立的 Streamlit 项目
- 保持与原版本相同的计算逻辑
- 添加四种增强功能:
  1. 数据导入导出
  2. 多场景对比
  3. 参数预设管理
  4. 交互式图表标注
- 提交到独立的 GitHub 仓库
- 部署到 Streamlit Cloud

## 2. 技术方案

### 2.1 技术栈

**核心技术:**
- Streamlit 1.31+ (Web 框架)
- Python 3.10+ (编程语言)
- Plotly 5.18+ (交互式图表)

**数据处理:**
- Pandas (数据处理)
- NumPy (数值计算)

**文件处理:**
- openpyxl (Excel 读写)
- xlsxwriter (Excel 导出)

**配置管理:**
- JSON (预设存储)

### 2.2 技术选型理由

选择 **Streamlit + Plotly** 方案的原因:
1. 快速开发 - 纯 Python 技术栈,无需前端构建
2. 满足需求 - Plotly 完全支持所有增强功能
3. 易于维护 - 代码结构清晰,迭代容易
4. 成熟生态 - 数据应用的黄金组合
5. 独立部署 - 易于部署到 Streamlit Cloud

## 3. 项目结构

```
fire-streamlit/
├── app.py                      # Streamlit 主应用入口
├── requirements.txt            # Python 依赖
├── README.md                   # 项目文档
├── .gitignore                  # Git 忽略文件
├── config/
│   └── presets.json            # 参数预设配置文件
├── src/
│   ├── __init__.py
│   ├── calculator.py           # 核心计算逻辑
│   ├── models.py               # 数据模型定义
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_handler.py     # 文件导入导出
│   │   └── presets.py          # 预设管理
│   └── ui/
│       ├── __init__.py
│       ├── input_section.py    # 参数输入界面
│       ├── charts.py           # 图表展示
│       └── results_table.py    # 结果表格
└── tests/                      # 单元测试
    └── test_calculator.py
```

## 4. 数据模型

### 4.1 核心数据结构

```python
@dataclass
class FinanceParams:
    """财务参数"""
    # 基础参数
    start_year: int
    start_work_year: int
    current_age: int
    retirement_age: int

    # 薪资参数
    initial_monthly_salary: float
    local_average_salary: float
    salary_growth_rate: float

    # 养老金参数
    pension_replacement_ratio: float
    contribution_ratio: float

    # 生活开销
    living_expense_ratio: float

    # 利率
    deposit_rate: float
    inflation_rate: float

    # 初始资产
    initial_savings: float
    initial_housing_fund: float
    housing_fund_rate: float
    initial_personal_pension: float

@dataclass
class YearlyData:
    """年度数据"""
    year: int
    age: int
    average_salary: float
    monthly_salary: float
    contribution_base: float
    pension_contribution: float
    personal_pension_account: float
    pension_years: int
    medical_years: int
    can_receive_pension: bool
    annual_pension_received: float
    living_expense: float
    savings: float
    total_assets: float

    # 增强字段
    scenario_name: str = ""
    is_retirement_year: bool = False
    is_pension_start_year: bool = False
```

## 5. 核心功能模块

### 5.1 计算模块 (calculator.py)

- 年度收支预测计算
- 养老金计算(考虑最低缴纳年限)
- 资产累积计算
- 支持多场景并行计算

**核心逻辑:**
1. 工资增长: 退休前按增长率增长,退休后为0
2. 当地平均工资: 每年按增长率增长
3. 养老金缴纳: 退休前或未满最低年限时继续缴纳
4. 个人养老金账户: 基数 × 8% × 12
5. 生活开销: 考虑通胀
6. 60岁后满足年限可领取养老金
7. 存款累计: 含利息
8. 总资产 = 存款 + 公积金 + 个人养老金

### 5.2 输入界面模块 (input_section.py)

- 基础参数输入(年份、年龄、薪资等)
- 高级参数输入(增长率、比例等)
- 预设管理(保存/加载/删除预设)
- 参数验证

### 5.3 图表展示模块 (charts.py)

- 资产趋势图(存款、总资产)
- 多场景对比图
- 关键节点标注(退休点、养老金领取点)
- 交互式缩放和悬停提示

### 5.4 结果表格模块 (results_table.py)

- 年度数据表格
- 支持排序和筛选
- 数据导出功能

### 5.5 文件处理模块 (file_handler.py)

- Excel 导入参数配置
- 导出计算结果为 Excel
- 预设配置的导入导出

### 5.6 预设管理模块 (presets.py)

- 保存当前参数为预设
- 加载已保存的预设
- 管理预设列表

## 6. 用户界面设计

### 6.1 页面布局

```
┌─────────────────────────────────────────────────┐
│          家庭收支预测系统 - Streamlit版          │
├─────────────────────────────────────────────────┤
│  [基础参数]  [高级参数]  [场景管理]  [导入/导出]  │
├─────────────────────────────────────────────────┤
│  参数输入区 (可折叠/展开)                        │
│  [计算预测]  [重置]  [保存为预设]                │
├─────────────────────────────────────────────────┤
│  关键指标卡片                                    │
│  (退休年份、退休存款、退休总资产、养老金月领)    │
├─────────────────────────────────────────────────┤
│  交互式图表 (Plotly)                            │
│  - 资产趋势曲线                                  │
│  - 关键节点标注                                  │
│  - 多场景对比                                    │
├─────────────────────────────────────────────────┤
│  年度数据表格                                    │
│  - 可排序/筛选                                  │
│  - 固定首列                                      │
│  - 导出按钮                                      │
└─────────────────────────────────────────────────┘
```

### 6.2 交互设计

**参数输入区:**
- 使用 st.expander 组织参数
- 分组显示:基础参数 / 高级参数
- 提供参数说明(tooltip)
- 实时验证参数合法性

**预设管理:**
- st.selectbox 选择预设
- 预设自动保存到 config/presets.json
- 支持预设 CRUD 操作
- 默认预设:保守/中性/乐观三种场景

**多场景对比:**
- st.multiselect 选择要对比的场景
- 图表中使用不同颜色/线型区分
- 图例显示场景名称
- 支持一键切换单场景/多场景视图

**交互式图表标注:**
- 退休点:红色虚线 + "退休"
- 领取养老金点:绿色虚线 + "开始领养老金"
- 资产拐点:自动标注资产最大值/最小值

## 7. 增强功能设计

### 7.1 数据导入导出

**Excel 导入:**
- 导入参数配置
- Excel 格式:参数名称 | 参数值 | 说明

**Excel 导出:**
- 导出计算结果
- 包含工作表:参数配置、年度数据、图表数据、关键指标

### 7.2 多场景对比

**默认场景:**
- 保守:低增长率(2%)、高开销(60%)、低利率(1.5%)
- 中性:中等增长率(4%)、中等开销(50%)、中等利率(2%)
- 乐观:高增长率(6%)、低开销(40%)、高利率(3%)

**对比功能:**
- 同一图表显示多条曲线
- 交互式图例:点击隐藏/显示特定场景
- 悬停显示各场景数值对比

### 7.3 参数预设管理

**预设存储结构:**
```json
{
    "presets": {
        "保守策略": {
            "params": {...},
            "created_at": "2025-01-01",
            "description": "低风险场景配置"
        }
    }
}
```

**管理功能:**
- 保存当前参数为新预设
- 覆盖已有预设
- 删除预设
- 导入/导出预设文件

### 7.4 交互式图表标注

**自动标注:**
- 退休年份
- 开始领取养老金年份
- 资产峰值年份

**Plotly 实现:**
```python
fig.add_vline(
    x=retirement_year,
    line_dash="dash",
    line_color="red",
    annotation_text="退休"
)
```

## 8. 部署方案

### 8.1 GitHub 仓库

- 独立仓库名: `fire-streamlit`
- 包含完整源码、文档、测试

### 8.2 Streamlit Cloud 部署

**部署步骤:**
1. 连接 GitHub 仓库到 Streamlit Cloud
2. 配置依赖文件 requirements.txt
3. 自动部署
4. 访问 URL: `https://fire-streamlit.streamlit.app`

**优势:**
- 免费托管
- 一键部署
- 自动更新

## 9. 开发计划

### 阶段 1: 基础功能 (1-2天)
- 项目搭建
- 核心计算逻辑迁移
- 基础 UI 实现
- 简单图表展示

### 阶段 2: 增强功能 (2-3天)
- 多场景对比
- 预设管理
- 数据导入导出
- 交互式标注

### 阶段 3: 优化部署 (1天)
- 测试和 Bug 修复
- 文档编写
- 部署到 Streamlit Cloud
- 提交到 GitHub

**总计: 约 4-6 天**

## 10. 成功标准

- [x] 计算结果与原 React 版本完全一致
- [x] 支持所有增强功能
- [x] 界面友好,响应迅速
- [x] 成功部署到 Streamlit Cloud
- [x] 代码提交到独立的 GitHub 仓库
- [x] 包含完整的使用文档

## 11. 风险与挑战

### 11.1 技术风险

**风险:** Python 浮点数精度可能导致计算结果微小差异
**缓解:** 使用 Decimal 类型处理关键金融计算

### 11.2 性能风险

**风险:** 多场景计算可能导致页面响应变慢
**缓解:** 使用 @st.cache_data 缓存计算结果

### 11.3 用户体验风险

**风险:** Streamlit 默认样式可能不够美观
**缓解:** 自定义 CSS 样式,使用 Streamlit 主题配置

## 12. 总结

本设计文档详细描述了将家庭收支预测系统从 React 迁移到 Streamlit 的完整方案。使用 Streamlit + Plotly 技术栈,在保持原有功能的基础上,添加了四种增强功能,最终将部署到 Streamlit Cloud 并提交到独立的 GitHub 仓库。
