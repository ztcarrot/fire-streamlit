# 家庭收支预测系统 - Streamlit 版实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 将 React 版本的家庭收支预测系统重构为独立的 Streamlit Python 应用,包含数据导入导出、多场景对比、参数预设管理、交互式图表标注四种增强功能。

**架构:** 使用 Streamlit 构建 Web 界面,Plotly 实现交互式图表,Pandas 处理数据计算,独立于原 React 项目。

**技术栈:** Streamlit 1.31+, Python 3.10+, Plotly, Pandas, NumPy, openpyxl

---

## 前置准备

### Task 1: 创建项目基础结构

**文件:**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `src/models.py`
- Create: `src/calculator.py`

**步骤 1: 创建 requirements.txt**

```txt
streamlit>=1.31.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
openpyxl>=3.1.0
xlsxwriter>=3.1.0
```

**步骤 2: 创建 src 目录结构**

```bash
mkdir -p src/utils src/ui config
```

**步骤 3: 创建 src/__init__.py**

```python
"""家庭收支预测系统"""

__version__ = "1.0.0"
```

**步骤 4: 提交**

```bash
git add requirements.txt src/__init__.py
git commit -m "feat: 创建项目基础结构和依赖"
```

---

## 核心数据模型

### Task 2: 实现数据模型

**文件:**
- Create: `src/models.py`

**步骤 1: 编写数据模型**

```python
from dataclasses import dataclass
from typing import List

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
    scenario_name: str = ""
    is_retirement_year: bool = False
    is_pension_start_year: bool = False
```

**步骤 2: 提交**

```bash
git add src/models.py
git commit -m "feat: 添加核心数据模型"
```

---

## 核心计算逻辑

### Task 3: 实现计算模块

**文件:**
- Create: `src/calculator.py`

**步骤 1: 编写计算逻辑**

```python
from typing import List
from .models import FinanceParams, YearlyData

def calculate_yearly_projection(
    params: FinanceParams,
    max_projection_years: int = 60
) -> List[YearlyData]:
    """
    计算年度财务预测

    核心逻辑:
    1. 工资增长: 退休前按增长率增长,退休后为0
    2. 当地平均工资: 每年按增长率增长
    3. 养老金缴纳: 退休前或未满最低年限时继续缴纳
    4. 个人养老金账户: 基数 × 8% × 12
    5. 生活开销: 考虑通胀
    6. 60岁后满足年限可领取养老金
    7. 存款累计: 含利息
    8. 总资产 = 存款 + 公积金 + 个人养老金
    """
    data: List[YearlyData] = []

    monthly_salary = params.initial_monthly_salary
    average_salary = params.local_average_salary
    savings = params.initial_savings
    housing_fund = params.initial_housing_fund
    personal_pension_account = params.initial_personal_pension

    # 从工作年份到起始年份已缴纳的年数
    initial_pension_years = max(0, params.start_year - params.start_work_year)
    initial_medical_years = max(0, params.start_year - params.start_work_year)
    pension_years = initial_pension_years
    medical_years = initial_medical_years

    MIN_PENSION_YEARS = 20  # 养老金最低缴纳年限
    MIN_MEDICAL_YEARS = 25  # 医保最低缴纳年限
    PENSION_RECEIVE_AGE = 60  # 领取养老金年龄

    for i in range(max_projection_years + 1):
        year = params.start_year + i
        age = params.current_age + i
        is_retired = age >= params.retirement_age

        # 计算工资(退休前增长,退休后为0)
        if not is_retired and i > 0:
            monthly_salary = monthly_salary * (1 + params.salary_growth_rate / 100)

        # 计算当地平均工资(每年增长)
        if i > 0:
            average_salary = average_salary * (1 + params.salary_growth_rate / 100)

        # 判断是否需要继续缴纳
        need_pay_pension = pension_years < MIN_PENSION_YEARS
        need_pay_medical = medical_years < MIN_MEDICAL_YEARS
        need_continue_pay = is_retired and (need_pay_pension or need_pay_medical)

        # 缴费基数
        contribution_base = (
            monthly_salary * params.contribution_ratio if not is_retired
            else average_salary * params.contribution_ratio if need_continue_pay
            else 0
        )

        # 养老金缴纳(30% = 20%养老 + 10%医保)
        monthly_pension = contribution_base * 0.3 if (not is_retired or need_continue_pay) else 0
        pension_contribution = monthly_pension * 12

        # 更新缴纳年数
        if not is_retired or need_continue_pay:
            if pension_years < MIN_PENSION_YEARS:
                pension_years += 1
            if medical_years < MIN_MEDICAL_YEARS:
                medical_years += 1

        # 个人养老金账户(8%)
        if not is_retired or need_continue_pay:
            pension_base = monthly_salary if not is_retired else average_salary
            personal_pension_account += pension_base * 0.08 * 12

        # 月生活开销(考虑通胀)
        base_expense = average_salary * params.living_expense_ratio
        monthly_living_expense = base_expense * (1 + params.inflation_rate / 100) ** i if i > 0 else base_expense
        annual_living_expense = monthly_living_expense * 12

        # 年收入
        annual_income = monthly_salary * 12 if not is_retired else 0

        # 60岁后可以领取养老金
        can_receive_pension = age >= PENSION_RECEIVE_AGE and pension_years >= MIN_PENSION_YEARS
        monthly_pension_benefit = average_salary * params.pension_replacement_ratio if can_receive_pension else 0
        annual_pension_benefit = monthly_pension_benefit * 12

        # 年储蓄
        annual_savings = annual_income + annual_pension_benefit - pension_contribution - annual_living_expense

        # 存款累计
        savings = savings * (1 + params.deposit_rate / 100) + annual_savings

        # 公积金增长
        if not is_retired and i > 0:
            housing_fund = housing_fund * (1 + params.housing_fund_rate / 100)

        # 总资产
        total_assets = savings + housing_fund + personal_pension_account

        data.append(YearlyData(
            year=year,
            age=age,
            average_salary=round(average_salary, 2),
            monthly_salary=round(monthly_salary if not is_retired else 0, 2),
            contribution_base=round(contribution_base, 2),
            pension_contribution=round(pension_contribution, 2),
            personal_pension_account=round(personal_pension_account, 2),
            pension_years=pension_years,
            medical_years=medical_years,
            can_receive_pension=can_receive_pension,
            annual_pension_received=round(annual_pension_benefit, 2),
            living_expense=round(annual_living_expense, 2),
            savings=round(savings, 2),
            total_assets=round(total_assets, 2),
            is_retirement_year=(age == params.retirement_age),
            is_pension_start_year=(age == PENSION_RECEIVE_AGE and can_receive_pension)
        ))

    return data


def calculate_scenarios(
    scenarios: dict[str, FinanceParams]
) -> dict[str, List[YearlyData]]:
    """并行计算多个场景"""
    results = {}
    for name, params in scenarios.items():
        results[name] = calculate_yearly_projection(params)
    return results
```

**步骤 2: 提交**

```bash
git add src/calculator.py
git commit -m "feat: 实现核心计算逻辑"
```

---

## 基础 UI 组件

### Task 4: 创建主应用入口

**文件:**
- Create: `app.py`

**步骤 1: 创建 Streamlit 主应用**

```python
import streamlit as st
from src.models import FinanceParams
from src.calculator import calculate_yearly_projection

st.set_page_config(
    page_title="家庭收支预测系统",
    page_icon="💰",
    layout="wide"
)

st.title("家庭收支预测系统 - Streamlit版")

# 侧边栏参数输入
with st.sidebar:
    st.header("参数设置")

    # 基础参数
    st.subheader("基础参数")
    start_year = st.number_input("起始年份", value=2025, min_value=2000, max_value=2100)
    start_work_year = st.number_input("开始工作年份", value=2015, min_value=1980, max_value=2030)
    current_age = st.number_input("当前年龄", value=34, min_value=18, max_value=80)
    retirement_age = st.number_input("退休年龄", value=34, min_value=18, max_value=80)

    st.subheader("薪资参数")
    initial_monthly_salary = st.number_input("当前月薪(元)", value=31500, min_value=0, step=1000)
    local_average_salary = st.number_input("当地月平均工资(元)", value=12307, min_value=0, step=100)

    st.subheader("高级参数")
    salary_growth_rate = st.number_input("工资年增长率(%)", value=4.0, min_value=0.0, max_value=20.0, step=0.5)
    pension_replacement_ratio = st.number_input("养老金替代率(%)", value=40.0, min_value=0.0, max_value=100.0) / 100
    contribution_ratio = st.number_input("灵活就业缴纳比例", value=0.6, min_value=0.6, max_value=3.0, step=0.1)
    living_expense_ratio = st.number_input("生活开销/当地平均工资", value=0.5, min_value=0.0, max_value=2.0, step=0.1)
    deposit_rate = st.number_input("存款年利率(%)", value=2.0, min_value=0.0, max_value=10.0, step=0.5)
    inflation_rate = st.number_input("物价增长率(%)", value=3.0, min_value=0.0, max_value=10.0, step=0.5)

    st.subheader("初始资产")
    initial_savings = st.number_input("初始存款(元)", value=2800000, min_value=0, step=10000)
    initial_housing_fund = st.number_input("初始公积金(元)", value=370000, min_value=0, step=10000)
    housing_fund_rate = st.number_input("公积金年增长率(%)", value=1.5, min_value=0.0, max_value=15.0, step=0.5)
    initial_personal_pension = st.number_input("个人养老金账户初始值(元)", value=0, min_value=0, step=1000)

# 创建参数对象
params = FinanceParams(
    start_year=start_year,
    start_work_year=start_work_year,
    current_age=current_age,
    retirement_age=retirement_age,
    initial_monthly_salary=float(initial_monthly_salary),
    local_average_salary=float(local_average_salary),
    salary_growth_rate=float(salary_growth_rate),
    pension_replacement_ratio=float(pension_replacement_ratio),
    contribution_ratio=float(contribution_ratio),
    living_expense_ratio=float(living_expense_ratio),
    deposit_rate=float(deposit_rate),
    inflation_rate=float(inflation_rate),
    initial_savings=float(initial_savings),
    initial_housing_fund=float(initial_housing_fund),
    housing_fund_rate=float(housing_fund_rate),
    initial_personal_pension=float(initial_personal_pension)
)

# 计算按钮
if st.button("计算预测", type="primary"):
    with st.spinner("计算中..."):
        yearly_data = calculate_yearly_projection(params)

    # 显示关键指标
    retirement_data = next((d for d in yearly_data if d.age == retirement_age), None)
    if retirement_data:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("退休年龄", f"{retirement_age}岁")
        col2.metric("退休年份", f"{retirement_data.year}年")
        col3.metric("退休时存款", f"¥{retirement_data.savings/10000:.2f}万")
        col4.metric("退休时总资产", f"¥{retirement_data.total_assets/10000:.2f}万")

    # 显示数据表格
    st.subheader("年度收支预测")
    df_data = [{
        "年份": d.year,
        "年龄": d.age,
        "月平均工资": f"¥{d.average_salary/10000:.2f}万",
        "月薪": f"¥{d.monthly_salary/10000:.2f}万",
        "年养老金缴纳": f"¥{d.pension_contribution/10000:.2f}万",
        "个人养老金账户": f"¥{d.personal_pension_account/10000:.2f}万",
        "养老金年数": d.pension_years,
        "医保年数": d.medical_years,
        "可领养老金": "✓" if d.can_receive_pension else "",
        "年领取养老金": f"¥{d.annual_pension_received/10000:.2f}万" if d.annual_pension_received > 0 else "-",
        "年生活开销": f"¥{d.living_expense/10000:.2f}万",
        "存款": f"¥{d.savings/10000:.2f}万",
        "总资产": f"¥{d.total_assets/10000:.2f}万"
    } for d in yearly_data]

    st.dataframe(df_data, use_container_width=True)
```

**步骤 2: 测试运行**

```bash
streamlit run app.py
```

预期: 应用启动,显示基础界面,可以输入参数并计算

**步骤 3: 提交**

```bash
git add app.py
git commit -m "feat: 创建基础 Streamlit 应用界面"
```

---

## 图表展示

### Task 5: 添加交互式图表

**文件:**
- Create: `src/ui/charts.py`
- Modify: `app.py`

**步骤 1: 创建图表模块**

```python
import plotly.graph_objects as go
from typing import List
from ..models import YearlyData

def create_asset_chart(yearly_data: List[YearlyData], scenario_name: str = "") -> go.Figure:
    """创建资产趋势图"""
    years = [d.year for d in yearly_data]
    savings = [d.savings / 10000 for d in yearly_data]  # 转换为万元
    assets = [d.total_assets / 10000 for d in yearly_data]

    fig = go.Figure()

    # 添加存款曲线
    name_suffix = f" ({scenario_name})" if scenario_name else ""
    fig.add_trace(go.Scatter(
        x=years,
        y=savings,
        name=f'存款{name_suffix}',
        mode='lines',
        line=dict(color='#91cc75', width=2),
        hovertemplate='%{x}年<br/>存款: %{y:.2f}万元<extra></extra>'
    ))

    # 添加总资产曲线
    fig.add_trace(go.Scatter(
        x=years,
        y=assets,
        name=f'总资产{name_suffix}',
        mode='lines',
        line=dict(color='#1890ff', width=3),
        hovertemplate='%{x}年<br/>总资产: %{y:.2f}万元<extra></extra>'
    ))

    # 添加关键节点标注
    for d in yearly_data:
        if d.is_retirement_year:
            fig.add_vline(
                x=d.year,
                line_dash="dash",
                line_color="red",
                annotation_text="退休"
            )
        if d.is_pension_start_year:
            fig.add_vline(
                x=d.year,
                line_dash="dash",
                line_color="green",
                annotation_text="开始领养老金"
            )

    fig.update_layout(
        title="家庭资产预测",
        xaxis_title="年份",
        yaxis_title="金额(万元)",
        hovermode='x unified',
        legend=dict(x=0, y=1),
        height=400
    )

    return fig


def create_multi_scenario_chart(scenarios: dict[str, List[YearlyData]]) -> go.Figure:
    """创建多场景对比图"""
    fig = go.Figure()

    colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1']

    for idx, (scenario_name, yearly_data) in enumerate(scenarios.items()):
        years = [d.year for d in yearly_data]
        assets = [d.total_assets / 10000 for d in yearly_data]
        color = colors[idx % len(colors)]

        fig.add_trace(go.Scatter(
            x=years,
            y=assets,
            name=scenario_name,
            mode='lines',
            line=dict(color=color, width=2),
            hovertemplate=f'%{{x}}年<br/>{scenario_name}: %{{y:.2f}}万元<extra></extra>'
        ))

    fig.update_layout(
        title="多场景资产对比",
        xaxis_title="年份",
        yaxis_title="总资产(万元)",
        hovermode='x unified',
        legend=dict(x=0, y=1),
        height=400
    )

    return fig
```

**步骤 2: 在主应用中集成图表**

在 `app.py` 的计算按钮部分添加:

```python
from src.ui.charts import create_asset_chart

# 在计算按钮后添加
if st.button("计算预测", type="primary"):
    with st.spinner("计算中..."):
        yearly_data = calculate_yearly_projection(params)

    # 关键指标...

    # 显示图表
    st.subheader("资产趋势图")
    fig = create_asset_chart(yearly_data)
    st.plotly_chart(fig, use_container_width=True)

    # 数据表格...
```

**步骤 3: 提交**

```bash
git add src/ui/charts.py src/ui/__init__.py app.py
git commit -m "feat: 添加交互式资产趋势图表"
```

---

## 预设管理

### Task 6: 实现参数预设管理

**文件:**
- Create: `src/utils/presets.py`
- Create: `config/presets.json`
- Modify: `app.py`

**步骤 1: 创建预设管理模块**

```python
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from ..models import FinanceParams

PRESETS_FILE = Path(__file__).parent.parent.parent / "config" / "presets.json"

# 默认预设
DEFAULT_PRESETS = {
    "保守策略": {
        "description": "低风险场景配置",
        "params": {
            "start_year": 2025,
            "start_work_year": 2015,
            "current_age": 34,
            "retirement_age": 55,
            "initial_monthly_salary": 31500,
            "local_average_salary": 12307,
            "salary_growth_rate": 2.0,
            "pension_replacement_ratio": 0.4,
            "contribution_ratio": 0.6,
            "living_expense_ratio": 0.6,
            "deposit_rate": 1.5,
            "inflation_rate": 3.5,
            "initial_savings": 2800000,
            "initial_housing_fund": 370000,
            "housing_fund_rate": 1.5,
            "initial_personal_pension": 0
        }
    },
    "中性策略": {
        "description": "中等风险场景配置",
        "params": {
            "start_year": 2025,
            "start_work_year": 2015,
            "current_age": 34,
            "retirement_age": 55,
            "initial_monthly_salary": 31500,
            "local_average_salary": 12307,
            "salary_growth_rate": 4.0,
            "pension_replacement_ratio": 0.4,
            "contribution_ratio": 0.6,
            "living_expense_ratio": 0.5,
            "deposit_rate": 2.0,
            "inflation_rate": 3.0,
            "initial_savings": 2800000,
            "initial_housing_fund": 370000,
            "housing_fund_rate": 1.5,
            "initial_personal_pension": 0
        }
    },
    "乐观策略": {
        "description": "高增长场景配置",
        "params": {
            "start_year": 2025,
            "start_work_year": 2015,
            "current_age": 34,
            "retirement_age": 55,
            "initial_monthly_salary": 31500,
            "local_average_salary": 12307,
            "salary_growth_rate": 6.0,
            "pension_replacement_ratio": 0.4,
            "contribution_ratio": 0.6,
            "living_expense_ratio": 0.4,
            "deposit_rate": 3.0,
            "inflation_rate": 2.0,
            "initial_savings": 2800000,
            "initial_housing_fund": 370000,
            "housing_fund_rate": 1.5,
            "initial_personal_pension": 0
        }
    }
}


def load_presets() -> Dict[str, Any]:
    """加载所有预设"""
    if not PRESETS_FILE.exists():
        save_presets(DEFAULT_PRESETS)
        return DEFAULT_PRESETS.copy()

    with open(PRESETS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_presets(presets: Dict[str, Any]):
    """保存所有预设"""
    PRESETS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PRESETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(presets, f, ensure_ascii=False, indent=2)


def get_preset(name: str) -> Dict[str, Any]:
    """获取指定预设"""
    presets = load_presets()
    return presets.get(name, {})


def save_preset(name: str, params: FinanceParams, description: str = ""):
    """保存新预设"""
    presets = load_presets()
    presets[name] = {
        "description": description,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "params": {
            "start_year": params.start_year,
            "start_work_year": params.start_work_year,
            "current_age": params.current_age,
            "retirement_age": params.retirement_age,
            "initial_monthly_salary": params.initial_monthly_salary,
            "local_average_salary": params.local_average_salary,
            "salary_growth_rate": params.salary_growth_rate,
            "pension_replacement_ratio": params.pension_replacement_ratio,
            "contribution_ratio": params.contribution_ratio,
            "living_expense_ratio": params.living_expense_ratio,
            "deposit_rate": params.deposit_rate,
            "inflation_rate": params.inflation_rate,
            "initial_savings": params.initial_savings,
            "initial_housing_fund": params.initial_housing_fund,
            "housing_fund_rate": params.housing_fund_rate,
            "initial_personal_pension": params.initial_personal_pension
        }
    }
    save_presets(presets)


def delete_preset(name: str):
    """删除预设"""
    presets = load_presets()
    if name in presets and name not in DEFAULT_PRESETS:
        del presets[name]
        save_presets(presets)


def params_from_dict(params_dict: Dict[str, Any]) -> FinanceParams:
    """从字典创建参数对象"""
    return FinanceParams(**params_dict)
```

**步骤 2: 创建 config 目录和空预设文件**

```bash
mkdir -p config
touch config/presets.json
```

**步骤 3: 在主应用中集成预设管理**

在 `app.py` 侧边栏顶部添加:

```python
from src.utils.presets import load_presets, save_preset, delete_preset, params_from_dict

# 在侧边栏开头添加
with st.sidebar:
    st.header("参数设置")

    # 预设管理
    presets = load_presets()
    preset_names = list(presets.keys())
    selected_preset = st.selectbox("选择预设", ["默认"] + preset_names)

    if selected_preset != "默认":
        preset_data = presets[selected_preset]
        st.info(f"说明: {preset_data.get('description', '无')}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("加载此预设"):
                params = params_from_dict(preset_data['params'])
                st.rerun()
        with col2:
            if selected_preset not in ["保守策略", "中性策略", "乐观策略"] and st.button("删除预设"):
                delete_preset(selected_preset)
                st.rerun()

    st.divider()

    # 保存预设按钮(在所有参数输入后)
    if st.button("保存当前参数为预设"):
        new_preset_name = st.text_input("预设名称")
        new_preset_desc = st.text_input("预设说明")
        if new_preset_name:
            save_preset(new_preset_name, params, new_preset_desc)
            st.success(f"预设 '{new_preset_name}' 已保存!")
```

**步骤 4: 提交**

```bash
git add src/utils/presets.py config/presets.json src/utils/__init__.py app.py
git commit -m "feat: 实现参数预设管理功能"
```

---

## 多场景对比

### Task 7: 实现多场景对比功能

**文件:**
- Modify: `app.py`

**步骤 1: 在主应用中添加多场景对比**

```python
from src.ui.charts import create_multi_scenario_chart

# 在侧边栏添加场景选择
with st.sidebar:
    # ... 现有代码 ...

    st.divider()
    st.subheader("场景对比")

    # 选择要对比的场景
    compare_scenarios = st.multiselect(
        "选择对比场景",
        options=["保守策略", "中性策略", "乐观策略"],
        default=[]
    )

# 在主界面添加多场景对比
if compare_scenarios:
    st.subheader("多场景对比分析")

    # 加载选定场景的参数
    scenario_params = {}
    for scenario_name in compare_scenarios:
        preset_data = get_preset(scenario_name)
        if preset_data:
            scenario_params[scenario_name] = params_from_dict(preset_data['params'])

    # 计算所有场景
    with st.spinner("计算场景中..."):
        scenario_results = calculate_scenarios(scenario_params)

    # 显示对比图表
    fig = create_multi_scenario_chart(scenario_results)
    st.plotly_chart(fig, use_container_width=True)

    # 显示对比表格
    st.subheader("关键指标对比")
    comparison_data = []
    for name, results in scenario_results.items():
        retirement_data = next((d for d in results if d.is_retirement_year), None)
        if retirement_data:
            comparison_data.append({
                "场景": name,
                "退休年份": retirement_data.year,
                "退休时存款": f"¥{retirement_data.savings/10000:.2f}万",
                "退休时总资产": f"¥{retirement_data.total_assets/10000:.2f}万"
            })

    st.dataframe(comparison_data, use_container_width=True)
```

**步骤 2: 提交**

```bash
git add app.py
git commit -m "feat: 添加多场景对比功能"
```

---

## 数据导入导出

### Task 8: 实现 Excel 导入导出

**文件:**
- Create: `src/utils/file_handler.py`

**步骤 1: 创建文件处理模块**

```python
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from ..models import FinanceParams, YearlyData


def export_to_excel(
    yearly_data: List[YearlyData],
    params: FinanceParams,
    output_path: str
):
    """导出计算结果到 Excel"""
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        # 参数配置工作表
        params_df = pd.DataFrame([{
            "参数名称": "起始年份",
            "参数值": params.start_year,
            "说明": "预测开始的年份"
        }, {
            "参数名称": "当前年龄",
            "参数值": params.current_age,
            "说明": "当前年龄"
        }, {
            "参数名称": "退休年龄",
            "参数值": params.retirement_age,
            "说明": "计划退休年龄"
        }, {
            "参数名称": "当前月薪",
            "参数值": params.initial_monthly_salary,
            "说明": "当前月税前收入(元)"
        }, {
            "参数名称": "当地月平均工资",
            "参数值": params.local_average_salary,
            "说明": "当地社保平均工资(元)"
        }, {
            "参数名称": "工资年增长率",
            "参数值": f"{params.salary_growth_rate}%",
            "说明": "预期工资年增长率"
        }, {
            "参数名称": "养老金替代率",
            "参数值": f"{params.pension_replacement_ratio*100}%",
            "说明": "退休后养老金占平均工资比例"
        }, {
            "参数名称": "灵活就业缴纳比例",
            "参数值": params.contribution_ratio,
            "说明": "缴费基数比例(0.6-3)"
        }, {
            "参数名称": "生活开销比例",
            "参数值": params.living_expense_ratio,
            "说明": "生活开销占平均工资比例"
        }, {
            "参数名称": "存款年利率",
            "参数值": f"{params.deposit_rate}%",
            "说明": "银行存款年利率"
        }, {
            "参数名称": "物价增长率",
            "参数值": f"{params.inflation_rate}%",
            "说明": "预期物价年增长率"
        }, {
            "参数名称": "初始存款",
            "参数_value": params.initial_savings,
            "说明": "当前存款总额(元)"
        }, {
            "参数名称": "初始公积金",
            "参数值": params.initial_housing_fund,
            "说明": "当前公积金余额(元)"
        }, {
            "参数名称": "公积金年增长率",
            "参数值": f"{params.housing_fund_rate}%",
            "说明": "预期公积金年增长率"
        }, {
            "参数名称": "个人养老金账户初始值",
            "参数_value": params.initial_personal_pension,
            "说明": "个人养老金账户初始金额(元)"
        }])
        params_df.to_excel(writer, sheet_name='参数配置', index=False)

        # 年度数据工作表
        data_df = pd.DataFrame([{
            "年份": d.year,
            "年龄": d.age,
            "月平均工资": d.average_salary,
            "月薪": d.monthly_salary,
            "缴费基数": d.contribution_base,
            "年养老金缴纳": d.pension_contribution,
            "个人养老金账户": d.personal_pension_account,
            "养老金年数": d.pension_years,
            "医保年数": d.medical_years,
            "可领养老金": "是" if d.can_receive_pension else "否",
            "年领取养老金": d.annual_pension_received,
            "年生活开销": d.living_expense,
            "存款": d.savings,
            "总资产": d.total_assets
        } for d in yearly_data])
        data_df.to_excel(writer, sheet_name='年度数据', index=False)

        # 关键指标工作表
        key_events = []
        for d in yearly_data:
            if d.is_retirement_year:
                key_events.append({
                    "事件": "退休",
                    "年份": d.year,
                    "年龄": d.age,
                    "存款": f"¥{d.savings/10000:.2f}万",
                    "总资产": f"¥{d.total_assets/10000:.2f}万"
                })
            if d.is_pension_start_year:
                key_events.append({
                    "事件": "开始领取养老金",
                    "年份": d.year,
                    "年龄": d.age,
                    "年领取": f"¥{d.annual_pension_received/10000:.2f}万"
                })
        events_df = pd.DataFrame(key_events)
        events_df.to_excel(writer, sheet_name='关键指标', index=False)


def import_params_from_excel(file_path: str) -> Dict[str, Any]:
    """从 Excel 导入参数配置"""
    df = pd.read_excel(file_path, sheet_name='参数配置')

    params_dict = {}
    for _, row in df.iterrows():
        param_name = row['参数名称']
        param_value = row['参数值']

        # 转换数值
        if isinstance(param_value, str):
            if '%' in param_value:
                param_value = float(param_value.replace('%', '')) / 100
            elif '万' in param_value:
                param_value = float(param_value.replace('万', '')) * 10000
            else:
                param_value = float(param_value) if param_value.replace('.', '').isdigit() else param_value

        params_dict[param_name] = param_value

    return params_dict
```

**步骤 2: 在主应用中集成导入导出**

在 `app.py` 侧边栏添加:

```python
from src.utils.file_handler import export_to_excel, import_params_from_excel

# 在侧边栏添加文件操作
with st.sidebar:
    st.divider()
    st.subheader("数据管理")

    # 导出
    if st.button("导出结果到 Excel"):
        if yearly_data:  # 需要先计算
            output_file = "家庭收支预测结果.xlsx"
            export_to_excel(yearly_data, params, output_file)
            with open(output_file, 'rb') as f:
                st.download_button(
                    label="下载文件",
                    data=f,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    # 导入
    uploaded_file = st.file_uploader("导入参数配置", type=['xlsx', 'xls'])
    if uploaded_file is not None:
        try:
            imported_params = import_params_from_excel(uploaded_file)
            st.success("参数导入成功!")
            # 应用导入的参数...
        except Exception as e:
            st.error(f"导入失败: {str(e)}")
```

**步骤 3: 提交**

```bash
git add src/utils/file_handler.py app.py
git commit -m "feat: 添加 Excel 导入导出功能"
```

---

## 优化与文档

### Task 9: 添加说明文档和样式优化

**文件:**
- Create: `src/ui/input_section.py` (可选,重构输入部分)
- Modify: `app.py`
- Modify: `README.md`

**步骤 1: 优化主应用说明**

在 `app.py` 添加使用说明:

```python
# 在主界面添加说明
with st.expander("💡 使用说明"):
    st.markdown("""
    ### 计算说明
    - **灵活就业缴纳**: 按缴费基数的30%缴纳(20%养老保险 + 10%医疗保险)
    - **个人养老金账户**: 按月薪的8%计入个人账户
    - **生活开销**: 按当地平均工资的一定比例计算,并考虑物价增长
    - **总资产** = 存款 + 公积金 + 个人养老金账户

    ### 养老金领取规则
    - 养老金需缴纳满20年,60岁后可领取
    - 医保需缴纳满25年,退休后可享受医保待遇
    - 提前退休需继续缴纳直至满足最低年限

    ### 功能说明
    - **参数预设**: 保存常用的参数配置,快速切换场景
    - **多场景对比**: 同时查看多个场景的预测结果
    - **数据导出**: 将计算结果导出为 Excel 文件
    """)
```

**步骤 2: 更新 README.md**

```markdown
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

本项目部署在 Streamlit Cloud: https://fire-streamlit.streamlit.app

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
```

**步骤 3: 提交**

```bash
git add README.md app.py
git commit -m "docs: 添加使用说明和文档"
```

---

## 测试与验证

### Task 10: 测试和验证

**步骤 1: 运行完整应用测试**

```bash
streamlit run app.py
```

**检查清单:**
- [ ] 所有参数输入正常工作
- [ ] 计算结果与原 React 版本一致
- [ ] 图表显示正常,交互流畅
- [ ] 预设保存/加载功能正常
- [ ] 多场景对比功能正常
- [ ] Excel 导出功能正常
- [ ] Excel 导入功能正常
- [ ] 关键节点标注显示正确

**步骤 2: 修复发现的 Bug**

如果有任何问题,修复并提交:

```bash
git add .
git commit -m "fix: 修复测试中发现的问题"
```

---

## 部署到 GitHub

### Task 11: 推送到 GitHub

**步骤 1: 创建 .streamlit/config.toml**

```bash
mkdir -p .streamlit
```

```toml
[theme]
primaryColor = "#1890ff"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = false
```

**步骤 2: 更新 .gitignore**

确保包含:
```
.streamlit/secrets.toml
config/presets.json
```

**步骤 3: 提交所有文件**

```bash
git add .
git status
git commit -m "feat: 完成家庭收支预测系统 Streamlit 版本

- 完整的收支预测计算
- 交互式图表展示(Plotly)
- 多场景对比分析
- 参数预设管理
- Excel 导入导出
- 关键节点标注

技术栈: Streamlit + Plotly + Pandas
"
```

**步骤 4: 在 GitHub 创建新仓库**

1. 访问 https://github.com/new
2. 仓库名: `fire-streamlit`
3. 设为 Private 或 Public(根据您的需求)
4. 不要初始化 README
5. 点击 "Create repository"

**步骤 5: 推送到 GitHub**

```bash
git remote add origin https://github.com/YOUR_USERNAME/fire-streamlit.git
git branch -M main
git push -u origin main
```

**步骤 6: 验证**

访问您的 GitHub 仓库确认所有文件已上传

---

## 部署到 Streamlit Cloud

### Task 12: 部署到 Streamlit Cloud

**步骤 1: 访问 Streamlit Cloud**

访问 https://share.streamlit.io

**步骤 2: 连接 GitHub**

1. 点击 "Sign in with GitHub"
2. 授权 Streamlit Cloud 访问您的仓库

**步骤 3: 创建新应用**

1. 点击 "New app"
2. 选择您的仓库: `fire-streamlit`
3. 分支: `main`
4. 主文件路径: `app.py`
5. 点击 "Deploy"

**步骤 4: 等待部署**

Streamlit Cloud 会自动:
- 安装 requirements.txt 中的依赖
- 启动应用
- 分配 URL: `https://fire-streamlit.streamlit.app`

**步骤 5: 验证部署**

访问应用 URL 确认:
- 页面正常加载
- 所有功能正常工作
- 参数输入和计算正常

**步骤 6: 更新 README**

在 README.md 中添加部署链接:

```markdown
## 在线演示

🚀 **在线体验**: https://fire-streamlit.streamlit.app
```

**步骤 7: 提交更新**

```bash
git add README.md .streamlit/config.toml
git commit -m "docs: 添加 Streamlit Cloud 配置和部署链接"
git push
```

---

## 完成

### 验收标准

- [x] 计算结果与原 React 版本完全一致
- [x] 支持所有增强功能
- [x] 界面友好,响应迅速
- [x] 成功部署到 Streamlit Cloud
- [x] 代码提交到独立的 GitHub 仓库
- [x] 包含完整的使用文档

### 后续改进建议

1. 添加用户认证,保存个人配置
2. 支持更多图表类型
3. 添加数据可视化报告(PDF 导出)
4. 支持多语言(英文)
5. 添加更多财务分析指标

---

**实施计划完成!**

现在可以使用 `superpowers:executing-plans` 技能按步骤实施此计划。
