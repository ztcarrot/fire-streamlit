import plotly.graph_objects as go
from typing import List
from ..models import YearlyData

def create_asset_chart(yearly_data: List[YearlyData], scenario_name: str = "") -> go.Figure:
    """创建资产趋势图"""
    years = [d.year for d in yearly_data]
    savings = [d.savings / 10000 for d in yearly_data]  # 转换为万元
    assets = [d.total_assets / 10000 for d in yearly_data]

    fig = go.Figure()

    # 添加存款曲线
    name_suffix = f" ({scenario_name})" if scenario_name else ""
    fig.add_trace(go.Scatter(
        x=years,
        y=savings,
        name=f'存款{name_suffix}',
        mode='lines',
        line=dict(color='#91cc75', width=2),
        hovertemplate='%{x}年<br/>存款: %{y:.2f}万元<extra></extra>'
    ))

    # 添加总资产曲线
    fig.add_trace(go.Scatter(
        x=years,
        y=assets,
        name=f'总资产{name_suffix}',
        mode='lines',
        line=dict(color='#1890ff', width=3),
        hovertemplate='%{x}年<br/>总资产: %{y:.2f}万元<extra></extra>'
    ))

    # 添加关键节点标注
    for d in yearly_data:
        if d.is_retirement_year:
            fig.add_vline(
                x=d.year,
                line_dash="dash",
                line_color="red",
                annotation_text="退休"
            )
        if d.is_pension_start_year:
            fig.add_vline(
                x=d.year,
                line_dash="dash",
                line_color="green",
                annotation_text="开始领养老金"
            )

    fig.update_layout(
        title="家庭资产预测",
        xaxis_title="年份",
        yaxis_title="金额(万元)",
        hovermode='x unified',
        legend=dict(x=0, y=0),
        height=400
    )

    return fig


def create_multi_scenario_chart(scenarios: dict[str, List[YearlyData]]) -> go.Figure:
    """创建多场景对比图"""
    fig = go.Figure()

    colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1']

    for idx, (scenario_name, yearly_data) in enumerate(scenarios.items()):
        years = [d.year for d in yearly_data]
        assets = [d.total_assets / 10000 for d in yearly_data]
        color = colors[idx % len(colors)]

        fig.add_trace(go.Scatter(
            x=years,
            y=assets,
            name=scenario_name,
            mode='lines',
            line=dict(color=color, width=2),
            hovertemplate=f'%{{x}}年<br/>{scenario_name}: %{{y:.2f}}万元<extra></extra>'
        ))

    fig.update_layout(
        title="多场景资产对比",
        xaxis_title="年份",
        yaxis_title="总资产(万元)",
        hovermode='x unified',
        legend=dict(x=0, y=0),
        height=400
    )

    return fig
