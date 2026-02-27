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

        # 公积金账户: 每年增长1.5% + 月工资的7%
        if age < 60 and i > 0:
            housing_fund = housing_fund * (1 + params.housing_fund_rate / 100) + monthly_salary * 0.07 * 12

        # 60岁退休那年提取公积金到存款
        if age == 60 and housing_fund > 0:
            savings += housing_fund
            housing_fund = 0

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

        # 总资产
        total_assets = savings + housing_fund

        data.append(YearlyData(
            year=year,
            age=age,
            average_salary=round(average_salary, 2),
            monthly_salary=round(monthly_salary if not is_retired else 0, 2),
            contribution_base=round(contribution_base, 2),
            pension_contribution=round(pension_contribution, 2),
            housing_fund_account=round(housing_fund, 2),
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
