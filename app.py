import streamlit as st
from datetime import datetime
from src.models import FinanceParams
from src.calculator import calculate_yearly_projection, calculate_scenarios
from src.ui.charts import create_asset_chart, create_multi_scenario_chart
from src.utils.presets import load_presets, save_preset, delete_preset, params_from_dict, get_preset
from src.utils.file_handler import export_to_excel, import_params_from_excel

# 获取当前年份
CURRENT_YEAR = datetime.now().year

st.set_page_config(
    page_title="家庭收支预测系统",
    page_icon="💰",
    layout="wide"
)

st.title("家庭收支预测系统 - Streamlit版")

# 顶部快捷链接
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.markdown("💡 **实时计算**: 修改左侧参数后,右侧数据和图表会自动刷新")
with col2:
    if st.button("📖 参数说明"):
        st.switch_page("PARAMETERS_GUIDE.md")
with col3:
    if st.button("❓ 使用帮助"):
        st.switch_page("README.md")

# 使用说明
with st.expander("💡 使用说明", expanded=False):
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
    - **实时计算**: 修改任意参数,结果立即更新
    - **参数预设**: 保存常用的参数配置,快速切换场景
    - **多场景对比**: 同时查看多个场景的预测结果
    - **数据导出**: 将计算结果导出为 Excel 文件
    """)

# 侧边栏参数输入
with st.sidebar:
    st.header("📊 参数设置")

    # 预设管理
    presets = load_presets()
    preset_names = list(presets.keys())
    selected_preset = st.selectbox("🎯 快速加载预设", ["默认"] + preset_names)

    # 如果选择了预设,显示说明和加载按钮
    if selected_preset != "默认":
        preset_data = presets[selected_preset]
        with st.container():
            st.info(f"📝 {preset_data.get('description', '无')}")

            # 显示预设的关键参数
            with st.expander("查看预设详情", expanded=False):
                params_info = preset_data['params']
                st.markdown(f"""
                - 工资增长率: **{params_info['salary_growth_rate']}%**
                - 生活开销: **{int(params_info['living_expense_ratio']*100)}%**
                - 存款利率: **{params_info['deposit_rate']}%**
                - 通胀率: **{params_info['inflation_rate']}%**
                """)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 加载", key="load_preset", use_container_width=True):
                    # 将预设参数保存到 session_state
                    for key, value in preset_data['params'].items():
                        st.session_state[f'param_{key}'] = value
                    st.success("✓ 预设已加载!")
                    st.rerun()
            with col2:
                if selected_preset not in ["保守策略", "中性策略", "乐观策略"] and st.button("🗑️ 删除", key="delete_preset", use_container_width=True):
                    delete_preset(selected_preset)
                    st.rerun()

    st.divider()

    # 基础参数
    st.subheader("📅 基础参数")
    # 从 session_state 获取值,如果没有则使用默认值
    def get_param(key, default):
        return st.session_state.get(f'param_{key}', default)

    start_year = st.number_input("起始年份", value=get_param('start_year', CURRENT_YEAR), min_value=2000, max_value=2100, key='param_start_year')
    start_work_year = st.number_input("开始工作年份", value=get_param('start_work_year', CURRENT_YEAR-10), min_value=1980, max_value=2030, key='param_start_work_year')
    current_age = st.number_input("当前年龄", value=get_param('current_age', 34), min_value=18, max_value=80, key='param_current_age')
    retirement_age = st.number_input("退休年龄", value=get_param('retirement_age', 45), min_value=18, max_value=80, key='param_retirement_age')

    st.subheader("💰 薪资参数")
    initial_monthly_salary = st.number_input("当前月薪(元)", value=get_param('initial_monthly_salary', 10000), min_value=0, step=1000, key='param_initial_monthly_salary')
    local_average_salary = st.number_input("当地月平均工资(元)", value=get_param('local_average_salary', 12307), min_value=0, step=100, key='param_local_average_salary')

    with st.expander("🔧 高级参数", expanded=False):
        salary_growth_rate = st.number_input("工资年增长率(%)", value=get_param('salary_growth_rate', 4.0), min_value=0.0, max_value=20.0, step=0.5, key='param_salary_growth_rate',
                                          help="影响未来收入增长和养老金基数")
        pension_replacement_ratio = st.number_input("养老金替代率(%)", value=get_param('pension_replacement_ratio', 40.0), min_value=0.0, max_value=100.0, step=1.0, key='param_pension_replacement_ratio',
                                                help="退休后养老金占平均工资的比例") / 100
        contribution_ratio = st.number_input("灵活就业缴纳比例", value=get_param('contribution_ratio', 0.6), min_value=0.6, max_value=3.0, step=0.1, key='param_contribution_ratio',
                                       help="社保缴费基数比例(0.6-3.0)")
        living_expense_ratio = st.number_input("生活开销/当地平均工资", value=get_param('living_expense_ratio', 0.5), min_value=0.0, max_value=2.0, step=0.1, key='param_living_expense_ratio',
                                     help="月生活开销占当地平均工资的比例")
        deposit_rate = st.number_input("存款年利率(%)", value=get_param('deposit_rate', 2.0), min_value=0.0, max_value=10.0, step=0.5, key='param_deposit_rate',
                                help="银行存款/理财年化收益率")

        # 物价增长率固定为0，不可编辑
        st.info("📊 **物价增长率**: 已固定为 0%")
        st.caption("💡 物价增长率已经由工资增长率近似")
        inflation_rate = 0.0  # 固定为0

    st.subheader("💎 初始资产")
    initial_savings = st.number_input("初始存款(元)", value=get_param('initial_savings', 1000000), min_value=0, step=10000, key='param_initial_savings', format="%d",
                                 help="当前银行存款总额")
    initial_housing_fund = st.number_input("初始公积金(元)", value=get_param('initial_housing_fund', 150000), min_value=0, step=10000, key='param_initial_housing_fund', format="%d",
                                      help="当前公积金账户余额")
    housing_fund_rate = st.number_input("公积金年增长率(%)", value=get_param('housing_fund_rate', 1.5), min_value=0.0, max_value=15.0, step=0.5, key='param_housing_fund_rate',
                                 help="预期公积金年增长率")
    initial_personal_pension = st.number_input("个人养老金账户初始值(元)", value=get_param('initial_personal_pension', 0), min_value=0, step=1000, key='param_initial_personal_pension', format="%d",
                                           help="个人养老金账户初始金额")

    st.divider()
    st.subheader("💾 保存预设")
    with st.expander("保存当前参数为预设"):
        new_preset_name = st.text_input("预设名称", key="new_preset_name")
        new_preset_desc = st.text_input("预设说明", key="new_preset_desc")
        if st.button("💾 保存预设", key="save_preset_btn"):
            if new_preset_name:
                save_preset(new_preset_name, params, new_preset_desc)
                st.success(f"✓ 预设 '{new_preset_name}' 已保存!")
            else:
                st.error("请输入预设名称")

    st.divider()
    st.subheader("📊 场景对比")

    # 选择要对比的场景
    compare_scenarios = st.multiselect(
        "选择对比场景",
        options=["保守策略", "中性策略", "乐观策略"],
        default=[]
    )

    st.divider()
    st.subheader("📁 数据管理")

    # 导入参数
    uploaded_file = st.file_uploader("导入参数配置", type=['xlsx', 'xls'], key="file_uploader")
    if uploaded_file is not None:
        try:
            imported_params = import_params_from_excel(uploaded_file)
            st.success("✓ 参数导入成功!")
            with st.expander("查看导入的参数", expanded=False):
                st.json(imported_params)

            if st.button("应用导入的参数", key="apply_imported"):
                for key, value in imported_params.items():
                    st.session_state[f'param_{key}'] = value
                st.rerun()
        except Exception as e:
            st.error(f"导入失败: {str(e)}")

# 创建参数对象
params = FinanceParams(
    start_year=int(start_year),
    start_work_year=int(start_work_year),
    current_age=int(current_age),
    retirement_age=int(retirement_age),
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

# 自动计算(实时)
@st.cache_data(ttl=60)
def cached_calculation(p):
    return calculate_yearly_projection(p)

yearly_data = cached_calculation(params)

# 显示关键指标
retirement_data = next((d for d in yearly_data if d.age == retirement_age), None)
if retirement_data:
    st.markdown("---")
    st.subheader("🎯 关键指标预测")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📅 退休年龄", f"{retirement_age}岁")
    col2.metric("📆 退休年份", f"{retirement_data.year}年")
    col3.metric("💵 退休时存款", f"¥{retirement_data.savings/10000:.2f}万")
    col4.metric("💰 退休时总资产", f"¥{retirement_data.total_assets/10000:.2f}万")

# 显示图表
st.subheader("📈 资产趋势图")
fig = create_asset_chart(yearly_data)
st.plotly_chart(fig, use_container_width=True)

# 显示数据表格
st.subheader("📋 年度收支预测表")
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

st.dataframe(df_data, use_container_width=True, height=400)

# 导出按钮
st.divider()
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("📥 导出结果到 Excel", type="primary"):
        output_file = "家庭收支预测结果.xlsx"
        export_to_excel(yearly_data, params, output_file)
        with open(output_file, 'rb') as f:
            st.download_button(
                label="⬇️ 下载 Excel 文件",
                data=f,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# 多场景对比
if compare_scenarios:
    st.markdown("---")
    st.subheader("🔍 多场景对比分析")

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
    st.subheader("📊 关键指标对比")
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
