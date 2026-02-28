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
            "参数名称": "起始年份（默认今年）",
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
            "参数名称": "预估工资和物价年增长率",
            "参数值": f"{params.salary_growth_rate}%",
            "说明": "影响未来收入增长、物价和养老金基数"
        }, {
            "参数名称": "预估养老金替代率",
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
            "参数名称": "预计存款年利率",
            "参数值": f"{params.deposit_rate}%",
            "说明": "银行存款/理财年化收益率"
        }, {
            "参数名称": "物价增长率",
            "参数值": f"{params.inflation_rate}%",
            "说明": "预期物价年增长率"
        }, {
            "参数名称": "初始存款",
            "参数值": params.initial_savings,
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
            "参数值": params.initial_personal_pension,
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
            "公积金账户": d.housing_fund_account,
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


def import_params_from_excel(file_path) -> Dict[str, Any]:
    """从 Excel 导入参数配置和自定义预设

    返回格式:
    {
        'user_params': {...},  # 用户当前输入的所有参数
        'user_presets': {...}  # 用户自定义的预设
    }
    """
    result = {}

    # 读取用户参数
    try:
        df_params = pd.read_excel(file_path, sheet_name='用户当前参数')
        user_params = {}
        for _, row in df_params.iterrows():
            param_name = row['参数名称']
            param_value = row['参数值']

            # 转换数值
            if isinstance(param_value, str):
                if param_value == '-' or param_value == '':
                    continue
                if '%' in param_value:
                    param_value = float(param_value.replace('%', '')) / 100
                elif '万' in param_value:
                    param_value = float(param_value.replace('万', '')) * 10000
                elif '岁' in param_value:
                    param_value = int(param_value.replace('岁', ''))
                else:
                    param_value = float(param_value) if '.' in str(param_value) or param_value.isdigit() else param_value

            user_params[param_name] = param_value
        result['user_params'] = user_params
    except Exception as e:
        pass  # 如果没有该工作表，继续

    # 读取自定义预设
    try:
        df_presets = pd.read_excel(file_path, sheet_name='自定义预设')
        user_presets = {}
        for _, row in df_presets.iterrows():
            preset_name = row['预设名称']
            preset_data = {
                'description': row['说明'],
                'params': {}
            }

            # 解析参数JSON
            import json
            params_json = row['参数配置']
            if isinstance(params_json, str):
                preset_data['params'] = json.loads(params_json)
            else:
                preset_data['params'] = params_json

            user_presets[preset_name] = preset_data
        result['user_presets'] = user_presets
    except Exception as e:
        pass  # 如果没有该工作表，继续

    # 如果没有自定义预设，初始化为空字典
    if 'user_presets' not in result:
        result['user_presets'] = {}

    return result


def export_user_params_and_presets(params: FinanceParams, output_path: str):
    """导出用户当前参数和自定义预设到 Excel"""
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        # 用户当前参数工作表
        user_params_data = [{
            "参数名称": "起始年份（默认今年）",
            "参数值": params.start_year,
            "说明": "预测开始的年份"
        }, {
            "参数名称": "开始工作年份",
            "参数值": params.start_work_year,
            "说明": "开始工作的年份"
        }, {
            "参数名称": "当前年龄",
            "参数值": params.current_age,
            "说明": "您当前的年龄"
        }, {
            "参数名称": "提前退休年龄",
            "参数值": params.retirement_age,
            "说明": "计划提前退休的年龄"
        }, {
            "参数名称": "正式退休年龄",
            "参数值": params.official_retirement_age,
            "说明": "正式退休（领取养老金）的年龄"
        }, {
            "参数名称": "当前月薪(元)",
            "参数值": params.initial_monthly_salary,
            "说明": "当前月税前收入"
        }, {
            "参数名称": "当地月平均工资(元)",
            "参数值": params.local_average_salary,
            "说明": "社保缴费基数参考"
        }, {
            "参数名称": "预估工资和物价年增长率(%)",
            "参数值": f"{params.salary_growth_rate}%",
            "说明": "影响未来收入增长、物价和养老金基数"
        }, {
            "参数名称": "预估养老金替代率",
            "参数值": f"{params.pension_replacement_ratio:.4f}",
            "说明": "退休后养老金占平均工资比例（如0.4表示40%）"
        }, {
            "参数名称": "灵活就业缴纳比例",
            "参数值": params.contribution_ratio,
            "说明": "社保缴费基数比例(0.6-3.0)"
        }, {
            "参数名称": "消费系数",
            "参数值": params.living_expense_ratio,
            "说明": "月生活开销占当地平均工资的比例"
        }, {
            "参数名称": "预计存款年利率(%)",
            "参数值": f"{params.deposit_rate}%",
            "说明": "银行存款/理财年化收益率"
        }, {
            "参数名称": "初始存款(元)",
            "参数值": params.initial_savings,
            "说明": "当前银行存款总额"
        }, {
            "参数名称": "初始公积金(元)",
            "参数值": params.initial_housing_fund,
            "说明": "当前公积金账户余额"
        }, {
            "参数名称": "公积金年增长率(%)",
            "参数值": f"{params.housing_fund_rate}%",
            "说明": "预期公积金年增长率"
        }, {
            "参数名称": "个人养老金账户初始值(元)",
            "参数值": params.initial_personal_pension,
            "说明": "个人养老金账户初始金额（已废弃）"
        }]
        user_params_df = pd.DataFrame(user_params_data)
        user_params_df.to_excel(writer, sheet_name='用户当前参数', index=False)

        # 自定义预设工作表
        import streamlit as st
        if 'user_presets' in st.session_state and st.session_state.user_presets:
            presets_data = []
            for preset_name, preset_data in st.session_state.user_presets.items():
                import json
                presets_data.append({
                    "预设名称": preset_name,
                    "说明": preset_data.get('description', ''),
                    "参数配置": json.dumps(preset_data['params'], ensure_ascii=False)
                })
            if presets_data:
                presets_df = pd.DataFrame(presets_data)
                presets_df.to_excel(writer, sheet_name='自定义预设', index=False)
        else:
            # 创建空的工作表
            pd.DataFrame({'提示': ['暂无自定义预设']}).to_excel(writer, sheet_name='自定义预设', index=False)
