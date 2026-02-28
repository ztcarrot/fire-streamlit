#!/usr/bin/env python3
"""测试参数导入导出功能"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.models import FinanceParams
from src.utils.file_handler import export_user_params_and_presets, import_params_from_excel
import tempfile
import streamlit as st

# 初始化 session_state
if not hasattr(st, 'session_state'):
    class MockSessionState:
        def __init__(self):
            self.data = {}
        def __contains__(self, key):
            return key in self.data
        def __setitem__(self, key, value):
            self.data[key] = value
        def __getitem__(self, key):
            return self.data.get(key)
    st.session_state = MockSessionState()

# 初始化 user_presets
st.session_state.user_presets = {
    "我的自定义预设": {
        "description": "测试用预设",
        "created_at": "2026-02-28",
        "params": {
            "salary_growth_rate": 5.0,
            "deposit_rate": 2.5
        }
    }
}

print("=" * 60)
print("测试参数导入导出功能")
print("=" * 60)

# 创建测试参数
test_params = FinanceParams(
    start_year=2026,
    start_work_year=2016,
    current_age=35,  # 修改后的值
    retirement_age=45,
    official_retirement_age=60,
    initial_monthly_salary=15000,  # 修改后的值
    local_average_salary=12307,
    salary_growth_rate=5.0,  # 修改后的值
    pension_replacement_ratio=0.45,
    contribution_ratio=0.8,
    living_expense_ratio=0.55,
    deposit_rate=2.5,  # 修改后的值
    inflation_rate=0.0,
    initial_savings=1200000,  # 修改后的值
    initial_housing_fund=200000,  # 修改后的值
    housing_fund_rate=2.0,
    initial_personal_pension=0
)

print("\n📤 测试1: 导出功能")
print("-" * 60)
print("原始参数:")
print(f"  - 当前年龄: {test_params.current_age}")
print(f"  - 当前月薪: {test_params.initial_monthly_salary}")
print(f"  - 工资增长率: {test_params.salary_growth_rate}%")
print(f"  - 存款利率: {test_params.deposit_rate}%")
print(f"  - 初始存款: {test_params.initial_savings}")
print(f"  - 初始公积金: {test_params.initial_housing_fund}")
print(f"  - 自定义预设数量: {len(st.session_state.user_presets)}")

# 导出
with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
    export_path = tmp_file.name
    export_user_params_and_presets(test_params, export_path)
    print(f"\n✓ 参数已导出到: {export_path}")

    # 检查文件大小
    file_size = os.path.getsize(export_path)
    print(f"✓ 文件大小: {file_size} bytes")

print("\n📥 测试2: 导入功能")
print("-" * 60)

# 导入
imported_data = import_params_from_excel(export_path)
print("✓ 文件读取成功")

# 检查导入的数据
if 'user_params' in imported_data:
    print(f"\n✓ 用户参数已导入，共 {len(imported_data['user_params'])} 个参数")
    user_params = imported_data['user_params']

    # 验证关键字段
    print("\n验证关键参数:")
    key_fields = {
        '当前年龄': 35,
        '当前月薪(元)': 15000,
        '工资年增长率(%)': 0.05,  # 5.0% 转换为小数
        '存款年利率(%)': 0.025,  # 2.5% 转换为小数
        '初始存款(元)': 1200000,
        '初始公积金(元)': 200000
    }

    all_match = True
    for field, expected in key_fields.items():
        if field in user_params:
            actual = user_params[field]
            # 对于百分比字段，使用近似比较
            if field.endswith('(%)'):
                match = abs(actual - expected) < 0.0001
            else:
                match = actual == expected
            status = "✓" if match else "✗"
            print(f"  {status} {field}: {actual} (期望: {expected})")
            if not match:
                all_match = False
        else:
            print(f"  ✗ {field}: 缺失")
            all_match = False

    if all_match:
        print("\n✅ 所有关键参数验证通过!")
    else:
        print("\n❌ 部分参数验证失败!")
        sys.exit(1)

if 'user_presets' in imported_data:
    print(f"\n✓ 自定义预设已导入，共 {len(imported_data['user_presets'])} 个")
    for name, data in imported_data['user_presets'].items():
        print(f"  - {name}: {data.get('description', '')}")

# 清理临时文件
os.unlink(export_path)

print("\n" + "=" * 60)
print("🎉 所有测试通过!")
print("=" * 60)
