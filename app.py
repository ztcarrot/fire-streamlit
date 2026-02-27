import streamlit as st
from src.models import FinanceParams
from src.calculator import calculate_yearly_projection
from src.ui.charts import create_asset_chart

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

    # 显示图表
    st.subheader("资产趋势图")
    fig = create_asset_chart(yearly_data)
    st.plotly_chart(fig, use_container_width=True)

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
