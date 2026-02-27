#!/usr/bin/env python3
"""
家庭收支预测系统 - 功能测试脚本
测试所有按钮和功能是否正常工作
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有模块导入"""
    print("📦 测试模块导入...")
    try:
        from src.models import FinanceParams, YearlyData
        from src.calculator import calculate_yearly_projection, calculate_scenarios
        from src.ui.charts import create_asset_chart, create_multi_scenario_chart
        from src.utils.presets import load_presets, save_preset, delete_preset, params_from_dict, get_preset
        from src.utils.file_handler import export_to_excel, import_params_from_excel
        print("✅ 所有模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_models():
    """测试数据模型"""
    print("\n📊 测试数据模型...")
    try:
        from src.models import FinanceParams, YearlyData

        params = FinanceParams(
            start_year=2025,
            start_work_year=2015,
            current_age=34,
            retirement_age=45,
            initial_monthly_salary=10000,
            local_average_salary=12307,
            salary_growth_rate=4.0,
            pension_replacement_ratio=0.4,
            contribution_ratio=0.6,
            living_expense_ratio=0.5,
            deposit_rate=2.0,
            inflation_rate=0.0,
            initial_savings=1000000,
            initial_housing_fund=150000,
            housing_fund_rate=1.5,
            initial_personal_pension=0
        )

        print(f"✅ FinanceParams 创建成功")
        print(f"   - 退休年龄: {params.retirement_age}")
        print(f"   - 当前月薪: {params.initial_monthly_salary}")
        return True
    except Exception as e:
        print(f"❌ 数据模型测试失败: {e}")
        return False

def test_calculator():
    """测试计算模块"""
    print("\n🧮 测试计算模块...")
    try:
        from src.models import FinanceParams
        from src.calculator import calculate_yearly_projection

        params = FinanceParams(
            start_year=2025,
            start_work_year=2015,
            current_age=34,
            retirement_age=45,
            initial_monthly_salary=10000,
            local_average_salary=12307,
            salary_growth_rate=4.0,
            pension_replacement_ratio=0.4,
            contribution_ratio=0.6,
            living_expense_ratio=0.5,
            deposit_rate=2.0,
            inflation_rate=0.0,
            initial_savings=1000000,
            initial_housing_fund=150000,
            housing_fund_rate=1.5,
            initial_personal_pension=0
        )

        result = calculate_yearly_projection(params)

        print(f"✅ 计算成功,生成 {len(result)} 年数据")
        if result:
            first_year = result[0]
            last_year = result[-1]
            print(f"   - 起始: {first_year.year}年, {first_year.age}岁")
            print(f"   - 结束: {last_year.year}年, {last_year.age}岁")
            print(f"   - 退休时总资产: ¥{last_year.total_assets/10000:.2f}万")
        return True
    except Exception as e:
        print(f"❌ 计算模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_charts():
    """测试图表模块"""
    print("\n📈 测试图表模块...")
    try:
        from src.models import FinanceParams
        from src.calculator import calculate_yearly_projection, calculate_scenarios
        from src.ui.charts import create_asset_chart, create_multi_scenario_chart

        params = FinanceParams(
            start_year=2025,
            start_work_year=2015,
            current_age=34,
            retirement_age=45,
            initial_monthly_salary=10000,
            local_average_salary=12307,
            salary_growth_rate=4.0,
            pension_replacement_ratio=0.4,
            contribution_ratio=0.6,
            living_expense_ratio=0.5,
            deposit_rate=2.0,
            inflation_rate=0.0,
            initial_savings=1000000,
            initial_housing_fund=150000,
            housing_fund_rate=1.5,
            initial_personal_pension=0
        )

        result = calculate_yearly_projection(params)

        # 测试单场景图表
        fig1 = create_asset_chart(result)
        print(f"✅ 单场景图表创建成功")

        # 测试多场景图表
        scenarios = {
            "保守": params,
            "中性": params,
            "乐观": params
        }
        scenario_results = calculate_scenarios(scenarios)
        fig2 = create_multi_scenario_chart(scenario_results)
        print(f"✅ 多场景图表创建成功")
        return True
    except Exception as e:
        print(f"❌ 图表模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_presets():
    """测试预设管理"""
    print("\n💾 测试预设管理...")
    try:
        from src.utils.presets import load_presets, get_preset

        # 加载预设
        presets = load_presets()
        print(f"✅ 加载预设成功,共 {len(presets)} 个预设")

        for name in presets.keys():
            print(f"   - {name}")

        # 测试获取单个预设
        if "保守策略" in presets:
            preset = get_preset("保守策略")
            if preset:
                print(f"✅ 获取单个预设成功")

        return True
    except Exception as e:
        print(f"❌ 预设管理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_operations():
    """测试文件操作"""
    print("\n📁 测试文件操作...")
    try:
        from src.utils.file_handler import export_to_excel
        from src.models import FinanceParams
        from src.calculator import calculate_yearly_projection

        params = FinanceParams(
            start_year=2025,
            start_work_year=2015,
            current_age=34,
            retirement_age=45,
            initial_monthly_salary=10000,
            local_average_salary=12307,
            salary_growth_rate=4.0,
            pension_replacement_ratio=0.4,
            contribution_ratio=0.6,
            living_expense_ratio=0.5,
            deposit_rate=2.0,
            inflation_rate=0.0,
            initial_savings=1000000,
            initial_housing_fund=150000,
            housing_fund_rate=1.5,
            initial_personal_pension=0
        )

        result = calculate_yearly_projection(params)

        # 测试导出
        export_to_excel(result, params, "/tmp/test_output.xlsx")
        print(f"✅ Excel 导出成功")

        # 检查文件是否存在
        if os.path.exists("/tmp/test_output.xlsx"):
            file_size = os.path.getsize("/tmp/test_output.xlsx")
            print(f"   - 文件大小: {file_size} bytes")
            return True
        else:
            print(f"❌ 导出文件未创建")
            return False
    except Exception as e:
        print(f"❌ 文件操作测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 家庭收支预测系统 - 功能测试")
    print("=" * 60)

    results = []

    results.append(("模块导入", test_imports()))
    results.append(("数据模型", test_models()))
    results.append(("计算模块", test_calculator()))
    results.append(("图表模块", test_charts()))
    results.append(("预设管理", test_presets()))
    results.append(("文件操作", test_file_operations()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)

    passed = 0
    failed = 0

    for name, result in results:
        if result:
            print(f"✅ {name}: 通过")
            passed += 1
        else:
            print(f"❌ {name}: 失败")
            failed += 1

    print(f"\n总计: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个测试失败,请检查")
        return 1

if __name__ == "__main__":
    sys.exit(main())
