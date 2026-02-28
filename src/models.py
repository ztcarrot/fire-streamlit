from dataclasses import dataclass
from typing import List

@dataclass
class FinanceParams:
    """财务参数"""
    # 基础参数
    start_year: int
    start_work_year: int
    current_age: int
    retirement_age: int  # 提前退休年龄
    official_retirement_age: int  # 正式退休年龄（领取养老金年龄）

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
    housing_fund_account: float
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
