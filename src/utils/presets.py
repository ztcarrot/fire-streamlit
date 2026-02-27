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
            "retirement_age": 45,
            "initial_monthly_salary": 10000,
            "local_average_salary": 12307,
            "salary_growth_rate": 2.0,
            "pension_replacement_ratio": 0.4,
            "contribution_ratio": 0.6,
            "living_expense_ratio": 0.6,
            "deposit_rate": 1.5,
            "inflation_rate": 0.0,
            "initial_savings": 1000000,
            "initial_housing_fund": 150000,
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
            "retirement_age": 45,
            "initial_monthly_salary": 10000,
            "local_average_salary": 12307,
            "salary_growth_rate": 4.0,
            "pension_replacement_ratio": 0.4,
            "contribution_ratio": 0.6,
            "living_expense_ratio": 0.5,
            "deposit_rate": 2.0,
            "inflation_rate": 0.0,
            "initial_savings": 1000000,
            "initial_housing_fund": 150000,
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
            "retirement_age": 45,
            "initial_monthly_salary": 10000,
            "local_average_salary": 12307,
            "salary_growth_rate": 6.0,
            "pension_replacement_ratio": 0.4,
            "contribution_ratio": 0.6,
            "living_expense_ratio": 0.4,
            "deposit_rate": 3.0,
            "inflation_rate": 0.0,
            "initial_savings": 1000000,
            "initial_housing_fund": 150000,
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
