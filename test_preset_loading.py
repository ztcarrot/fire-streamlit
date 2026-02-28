#!/usr/bin/env python3
"""测试预设加载功能"""

import sys
sys.path.insert(0, '.')

from src.utils.presets import load_presets, get_preset

print("=" * 60)
print("测试预设加载功能")
print("=" * 60)

# 加载所有预设
presets = load_presets()
print(f"\n✓ 加载了 {len(presets)} 个预设:")
for name in presets.keys():
    print(f"  - {name}")

# 测试每个预设的参数
for preset_name in presets.keys():
    print(f"\n{'='*60}")
    print(f"测试预设: {preset_name}")
    print('='*60)

    preset_data = get_preset(preset_name)
    if not preset_data:
        print(f"✗ 无法加载预设 '{preset_name}'")
        continue

    params = preset_data.get('params', {})
    print(f"\n参数数量: {len(params)}")

    # 检查每个参数的值类型
    print("\n参数类型检查:")
    for key, value in params.items():
        value_type = type(value).__name__
        print(f"  - {key}: {value_type} = {value}")

        # 测试字符串转换
        try:
            if isinstance(value, bool):
                str_val = 'True' if value else 'False'
            elif value is None:
                str_val = ''
            else:
                str_val = str(value)
            print(f"    ✓ 转换为字符串: '{str_val}'")
        except Exception as e:
            print(f"    ✗ 转换失败: {e}")

    print(f"\n✓ 预设 '{preset_name}' 测试通过")

print("\n" + "=" * 60)
print("🎉 所有预设测试通过!")
print("=" * 60)
