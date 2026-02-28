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

st.title("家庭收支预测系统")

# 初始化 session state
if 'show_param_guide' not in st.session_state:
    st.session_state.show_param_guide = False
if 'show_help' not in st.session_state:
    st.session_state.show_help = False

# 顶部快捷链接
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.markdown("💡 **实时计算**: 修改左侧参数后,右侧数据和图表会自动刷新")
with col2:
    if st.button("📖 参数说明"):
        st.session_state.show_param_guide = not st.session_state.show_param_guide
        st.rerun()
with col3:
    if st.button("❓ 使用帮助"):
        st.session_state.show_help = not st.session_state.show_help
        st.rerun()

# 参数说明弹窗
if st.session_state.show_param_guide:
    with st.expander("📖 参数说明", expanded=True):
        try:
            with open('PARAMETERS_GUIDE.md', 'r', encoding='utf-8') as f:
                st.markdown(f.read())
        except FileNotFoundError:
            st.info("参数说明文件未找到")
        if st.button("关闭参数说明", key="close_param_guide"):
            st.session_state.show_param_guide = False
            st.rerun()

# 使用帮助弹窗
if st.session_state.show_help:
    with st.expander("❓ 使用帮助", expanded=True):
        try:
            with open('README.md', 'r', encoding='utf-8') as f:
                st.markdown(f.read())
        except FileNotFoundError:
            st.info("README 文件未找到")
        if st.button("关闭帮助", key="close_help"):
            st.session_state.show_help = False
            st.rerun()

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

    # 基础参数
    with st.expander("📅 基础参数", expanded=True):
        # 从 session_state 获取值,如果没有则使用默认值
        def get_param(key, default, param_type=None):
            val = st.session_state.get(f'param_{key}', None)
            if val is None:
                return default
            # 确保类型正确
            if param_type == 'int':
                return int(val)
            elif param_type == 'float':
                return float(val)
            return val

        def text_input_number(label, key, default, param_type='int', help=None):
            """文本输入数字，不捕获滚轮事件"""
            # 获取之前保存的值或使用默认值
            text_val = st.session_state.get(f'text_{key}', str(default))
            # 创建文本输入
            input_val = st.text_input(label, value=text_val, key=f'text_{key}', help=help)
            # 转换为数字并保存到 session_state
            try:
                if param_type == 'int':
                    num_val = int(input_val) if input_val else default
                else:
                    num_val = float(input_val) if input_val else default
                # 保存到 param key 供后续使用
                st.session_state[f'param_{key}'] = num_val
                return num_val
            except ValueError:
                # 如果转换失败，返回默认值
                return default

        col1, col2 = st.columns(2)
        with col1:
            start_year = text_input_number("起始年份（默认今年）", 'start_year', get_param('start_year', CURRENT_YEAR, 'int'), 'int')
            current_age = text_input_number("当前年龄", 'current_age', get_param('current_age', 34, 'int'), 'int')
        with col2:
            start_work_year = text_input_number("开始工作年份", 'start_work_year', get_param('start_work_year', 2014, 'int'), 'int')
            retirement_age = text_input_number("提前退休年龄", 'retirement_age', get_param('retirement_age', 45, 'int'), 'int',
                                        help="计划提前退休的年龄")

        official_retirement_age = text_input_number("正式退休年龄", 'official_retirement_age', get_param('official_retirement_age', 60, 'int'), 'int',
                                          help="正式退休（领取养老金）的年龄，男性60，女性50/55")

    # 薪资参数
    with st.expander("💰 薪资参数", expanded=True):
        initial_monthly_salary = text_input_number("当前月薪(元)", 'initial_monthly_salary', get_param('initial_monthly_salary', 10000, 'int'), 'int',
                                             help="当前月税前收入")
        local_average_salary = text_input_number("当地月平均工资(元)", 'local_average_salary', get_param('local_average_salary', 12434, 'int'), 'int',
                                           help="社保缴费基数参考")

    # 初始资产
    with st.expander("💎 初始资产", expanded=True):
        initial_savings = text_input_number("初始存款(元)", 'initial_savings', get_param('initial_savings', 1000000, 'int'), 'int',
                                     help="当前银行存款总额")
        initial_housing_fund = text_input_number("初始公积金(元)", 'initial_housing_fund', get_param('initial_housing_fund', 150000, 'int'), 'int',
                                      help="当前公积金账户余额")
        housing_fund_rate = text_input_number("公积金年增长率(%)", 'housing_fund_rate', get_param('housing_fund_rate', 1.5, 'float'), 'float',
                                     help="预期公积金年增长率")

    # 高级参数
    with st.expander("🔧 高级参数", expanded=True):
        # 预设管理
        st.markdown("---")
        st.markdown("### 🎯 快速加载预设")
        presets = load_presets()
        preset_names = list(presets.keys())
        selected_preset = st.selectbox("选择预设", ["默认"] + preset_names, key="preset_selector")

        # 如果选择了预设,显示说明和加载按钮
        if selected_preset != "默认":
            preset_data = presets[selected_preset]
            with st.container():
                st.info(f"📝 {preset_data.get('description', '无')}")

                # 显示预设的关键参数
                with st.expander("查看预设详情", expanded=False):
                    params_info = preset_data['params']
                    st.markdown(f"""
                    - 预估工资和物价年增长率: **{params_info['salary_growth_rate']}%**
                    - 预估养老金替代率: **{int(params_info['pension_replacement_ratio']*100)}%**
                    - 消费系数: **{int(params_info['living_expense_ratio']*100)}%**
                    - 预计存款年利率: **{params_info['deposit_rate']}%**
                    """)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ 加载", key="load_preset", use_container_width=True):
                        # 将预设参数保存到 session_state
                        for key, value in preset_data['params'].items():
                            try:
                                # 保存参数值
                                st.session_state[f'param_{key}'] = value
                                # 安全地转换为字符串
                                if isinstance(value, bool):
                                    st.session_state[f'text_{key}'] = 'True' if value else 'False'
                                elif value is None:
                                    st.session_state[f'text_{key}'] = ''
                                else:
                                    st.session_state[f'text_{key}'] = str(value)
                            except Exception as e:
                                st.error(f"加载参数 {key} 失败: {str(e)}")
                        st.success("✓ 预设已加载!")
                        st.rerun()
                with col2:
                    if selected_preset not in ["保守策略", "中性策略", "乐观策略"] and st.button("🗑️ 删除", key="delete_preset", use_container_width=True):
                        delete_preset(selected_preset)
                        st.rerun()

        st.markdown("---")
        st.markdown("### 📊 高级设置")

        col1, col2 = st.columns(2)
        with col1:
            salary_growth_rate = text_input_number("预估工资和物价年增长率(%)", 'salary_growth_rate', get_param('salary_growth_rate', 4.0, 'float'), 'float',
                                          help="影响未来收入增长、物价和养老金基数")
        with col2:
            deposit_rate = text_input_number("预计存款年利率(%)", 'deposit_rate', get_param('deposit_rate', 2.0, 'float'), 'float',
                                help="银行存款/理财年化收益率")

        col1, col2 = st.columns(2)
        with col1:
            pension_replacement_ratio = text_input_number("预估养老金替代率", 'pension_replacement_ratio', get_param('pension_replacement_ratio', 0.4, 'float'), 'float',
                                                help="""退休后养老金占平均工资的比例（如：0.4 表示 40%）

💡 **上海市养老金计算公式**：
• 基础养老金 = (当地平均工资 + 指数化月平均缴费工资) ÷ 2 × 缴费年限 × 1%
• 个人账户养老金 = 个人账户储存额 ÷ 139（60岁退休）
• 总养老金 = 基础养老金 + 个人账户养老金

预估替代率 = 月养老金 ÷ 当地月平均工资""")
            # 显示计算后的等效当前月养老金
            monthly_pension = pension_replacement_ratio * local_average_salary
            st.caption(f"💵 等效当前月养老金: ¥{monthly_pension:,.0f} 元")
        with col2:
            living_expense_ratio = text_input_number("消费系数", 'living_expense_ratio', get_param('living_expense_ratio', 0.5, 'float'), 'float',
                                     help="月生活开销占当地平均工资的比例")
            # 显示计算后的当前平均年消费金额
            annual_expense = living_expense_ratio * local_average_salary * 12
            st.caption(f"💰 当前平均年消费: ¥{annual_expense:,.0f} 元")

        contribution_ratio = text_input_number("灵活就业缴纳比例", 'contribution_ratio', get_param('contribution_ratio', 0.6, 'float'), 'float',
                                       help="社保缴费基数比例(0.6-3.0)")

        inflation_rate = 0.0  # 固定为0


    st.divider()
    st.subheader("💾 保存预设")
    with st.expander("保存当前参数为预设"):
        new_preset_name = st.text_input("预设名称", key="new_preset_name")
        new_preset_desc = st.text_input("预设说明", key="new_preset_desc")
        if st.button("💾 保存预设", key="save_preset_btn"):
            if new_preset_name:
                # 获取当前参数值
                current_params = FinanceParams(
                    start_year=int(start_year),
                    start_work_year=int(start_work_year),
                    current_age=int(current_age),
                    retirement_age=int(retirement_age),
                    official_retirement_age=int(official_retirement_age),
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
                    initial_personal_pension=0.0  # 已废弃，保留默认值
                )
                save_preset(new_preset_name, current_params, new_preset_desc)
                st.success(f"✓ 预设 '{new_preset_name}' 已保存!")
            else:
                st.error("请输入预设名称")

    st.divider()
    st.subheader("📊 场景对比")

    # 动态获取所有可用的预设（包括用户自定义的）
    all_presets = load_presets()
    all_preset_names = list(all_presets.keys())

    # 如果有自定义预设，添加提示
    if len(all_preset_names) > 3:
        st.caption(f"💡 共有 {len(all_preset_names)} 个预设可选，包括您保存的自定义预设")

    # 选择要对比的场景
    compare_scenarios = st.multiselect(
        "选择对比场景",
        options=all_preset_names,
        default=[]
    )

    # 参数导入导出（折叠）
    st.divider()
    with st.expander("📁 参数管理"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**导出**")
            if st.button("📤 导出参数", key="export_params_sidebar"):
                try:
                    from src.utils.file_handler import export_user_params_and_presets
                    import tempfile

                    # 获取当前参数
                    current_params = FinanceParams(
                        start_year=int(start_year),
                        start_work_year=int(start_work_year),
                        current_age=int(current_age),
                        retirement_age=int(retirement_age),
                        official_retirement_age=int(official_retirement_age),
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
                        initial_personal_pension=0.0
                    )

                    # 创建临时文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                        export_user_params_and_presets(current_params, tmp_file.name)

                        # 提供下载
                        with open(tmp_file.name, 'rb') as f:
                            st.download_button(
                                label="⬇️ 下载",
                                data=f,
                                file_name="家庭收支预测-参数配置.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key="download_params"
                            )
                    st.success("✓ 导出成功!")
                except Exception as e:
                    st.error(f"导出失败: {str(e)}")

        with col2:
            st.markdown("**导入**")
            uploaded_file = st.file_uploader("选择文件", type=['xlsx', 'xls'], key="file_uploader_sidebar")
            if uploaded_file is not None:
                try:
                    from src.utils.file_handler import import_params_from_excel
                    imported_data = import_params_from_excel(uploaded_file)
                    st.success("✓ 读取成功!")

                    if st.button("✅ 应用并刷新", key="apply_imported_sidebar"):
                        # 应用用户参数
                        if 'user_params' in imported_data:
                            param_mapping = {
                                '起始年份': 'start_year',
                                '开始工作年份': 'start_work_year',
                                '当前年龄': 'current_age',
                                '提前退休年龄': 'retirement_age',
                                '正式退休年龄': 'official_retirement_age',
                                '当前月薪(元)': 'initial_monthly_salary',
                                '当地月平均工资(元)': 'local_average_salary',
                                '预估工资和物价年增长率(%)': 'salary_growth_rate',
                                '预估养老金替代率': 'pension_replacement_ratio',
                                '灵活就业缴纳比例': 'contribution_ratio',
                                '消费系数': 'living_expense_ratio',
                                '预计存款年利率(%)': 'deposit_rate',
                                '物价增长率(%)': 'inflation_rate',
                                '初始存款(元)': 'initial_savings',
                                '初始公积金(元)': 'initial_housing_fund',
                                '公积金年增长率(%)': 'housing_fund_rate'
                            }

                            for chinese_name, english_key in param_mapping.items():
                                if chinese_name in imported_data['user_params']:
                                    value = imported_data['user_params'][chinese_name]
                                    st.session_state[f'param_{english_key}'] = value
                                    # 安全地转换为字符串
                                    if isinstance(value, bool):
                                        st.session_state[f'text_{english_key}'] = 'True' if value else 'False'
                                    elif value is None:
                                        st.session_state[f'text_{english_key}'] = ''
                                    else:
                                        st.session_state[f'text_{english_key}'] = str(value)

                        # 应用自定义预设
                        if 'user_presets' in imported_data:
                            for preset_name, preset_data in imported_data['user_presets'].items():
                                st.session_state.user_presets[preset_name] = preset_data

                        st.success("✓ 参数已应用! 页面即将刷新...")
                        st.rerun()
                except Exception as e:
                    st.error(f"导入失败: {str(e)}")

# 创建参数对象
params = FinanceParams(
    start_year=int(start_year),
    start_work_year=int(start_work_year),
    current_age=int(current_age),
    retirement_age=int(retirement_age),
    official_retirement_age=int(official_retirement_age),
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
    initial_personal_pension=0.0  # 已废弃，保留默认值
)

# 自动计算(实时) - 不使用缓存以避免哈希问题
yearly_data = calculate_yearly_projection(params)

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
import pandas as pd

df_data = [{
    "年龄": d.age,
    "年份": d.year,
    "月平均工资": f"¥{d.average_salary/10000:.2f}万",
    "月薪": f"¥{d.monthly_salary/10000:.2f}万",
    "年养老金缴纳": f"¥{d.pension_contribution/10000:.2f}万",
    "公积金账户": f"¥{d.housing_fund_account/10000:.2f}万",
    "养老金年数": d.pension_years,
    "医保年数": d.medical_years,
    "可领养老金": "✓" if d.can_receive_pension else "",
    "年领取养老金": f"¥{d.annual_pension_received/10000:.2f}万" if d.annual_pension_received > 0 else "-",
    "年生活开销": f"¥{d.living_expense/10000:.2f}万",
    "存款": f"¥{d.savings/10000:.2f}万",
    "总资产": d.total_assets / 10000  # 保存数值用于样式
} for d in yearly_data]

df = pd.DataFrame(df_data)
# 将年龄设为索引，这样会成为第一列并可以固定
df = df.set_index('年龄')

# 定义样式函数：总资产为负数时显示红色
def color_negative_red(val):
    """总资产为负数时显示红色"""
    if isinstance(val, (int, float)) and val < 0:
        return 'color: red; font-weight: bold;'
    return ''

# 应用样式
styled_df = df.style.applymap(color_negative_red, subset=['总资产'])
# 格式化总资产列
styled_df = styled_df.format({'总资产': '¥{:.2f}万'})
# 固定索引列（年龄）在左侧
styled_df = styled_df.set_sticky(axis="index")

st.dataframe(styled_df, use_container_width=True, height=400)

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

    # 显示说明
    st.info("💡 **对比说明**: 场景对比使用您当前输入的基础参数、薪资参数和初始资产，只从预设中应用高级参数（工资增长率、养老金替代率等）")

    # 合并用户参数和预设高级参数的函数
    def merge_user_params_with_preset(user_params: FinanceParams, preset_params: dict) -> FinanceParams:
        """合并用户当前输入的参数和预设的高级参数"""
        return FinanceParams(
            # 使用用户的当前输入
            start_year=user_params.start_year,
            start_work_year=user_params.start_work_year,
            current_age=user_params.current_age,
            retirement_age=user_params.retirement_age,
            official_retirement_age=user_params.official_retirement_age,
            initial_monthly_salary=user_params.initial_monthly_salary,
            local_average_salary=user_params.local_average_salary,
            initial_savings=user_params.initial_savings,
            initial_housing_fund=user_params.initial_housing_fund,
            housing_fund_rate=user_params.housing_fund_rate,
            initial_personal_pension=user_params.initial_personal_pension,
            # 从预设中获取高级参数
            salary_growth_rate=preset_params.get('salary_growth_rate', user_params.salary_growth_rate),
            pension_replacement_ratio=preset_params.get('pension_replacement_ratio', user_params.pension_replacement_ratio),
            contribution_ratio=preset_params.get('contribution_ratio', user_params.contribution_ratio),
            living_expense_ratio=preset_params.get('living_expense_ratio', user_params.living_expense_ratio),
            deposit_rate=preset_params.get('deposit_rate', user_params.deposit_rate),
            inflation_rate=preset_params.get('inflation_rate', user_params.inflation_rate)
        )

    # 创建场景参数：使用用户当前输入 + 预设的高级参数
    scenario_params = {}
    for scenario_name in compare_scenarios:
        preset_data = get_preset(scenario_name)
        if preset_data:
            scenario_params[scenario_name] = merge_user_params_with_preset(params, preset_data['params'])

    if scenario_params:
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
            pension_data = next((d for d in results if d.age == scenario_params[name].official_retirement_age), None)
            final_data = results[-1] if results else None
            scenario_params_obj = scenario_params[name]

            if retirement_data:
                comparison_data.append({
                    "场景": name,
                    "提前退休年龄": f"{scenario_params_obj.retirement_age}岁",
                    "提前退休年份": retirement_data.year,
                    "正式退休年龄": f"{scenario_params_obj.official_retirement_age}岁",
                    "预估工资和物价年增长率": f"{scenario_params_obj.salary_growth_rate}%",
                    "预估养老金替代率": f"{scenario_params_obj.pension_replacement_ratio:.0%}",
                    "消费系数": f"{scenario_params_obj.living_expense_ratio:.0%}",
                    "预计存款年利率": f"{scenario_params_obj.deposit_rate}%",
                    "退休时存款": f"¥{retirement_data.savings/10000:.2f}万",
                    "退休时公积金": f"¥{retirement_data.housing_fund_account/10000:.2f}万",
                    "退休时总资产": f"¥{retirement_data.total_assets/10000:.2f}万",
                    "年生活开销": f"¥{retirement_data.living_expense/10000:.2f}万",
                    f"{scenario_params_obj.official_retirement_age}岁存款": f"¥{pension_data.savings/10000:.2f}万" if pension_data else "-",
                    f"{scenario_params_obj.official_retirement_age}岁总资产": f"¥{pension_data.total_assets/10000:.2f}万" if pension_data else "-",
                    f"{scenario_params_obj.official_retirement_age}岁养老金": f"¥{pension_data.annual_pension_received/10000:.2f}万" if pension_data and pension_data.annual_pension_received > 0 else "-",
                    "100岁时总资产": f"¥{final_data.total_assets/10000:.2f}万" if final_data else "-"
                })

        st.dataframe(comparison_data, use_container_width=True)
    else:
        st.warning("无法加载选定的场景，请检查预设配置")
