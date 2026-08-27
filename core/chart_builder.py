"""
AMG Dashboard - Chart Builder (Enterprise Grade)
Plotly visualizations with UUID div IDs, high-cardinality handling, outlier protection, executive insights
UNIVERSAL CURRENCY SUPPORT | DETERMINISTIC MATH ONLY
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import uuid
from config import THEMES, QA_THRESHOLDS

class ChartBuilder:
    """Production-grade Plotly chart generator with universal currency handling"""
    
    def __init__(self, theme="Professional Dark", currency_symbol="$"):
        self.theme = THEMES.get(theme, THEMES["Professional Dark"])
        self.chart_colors = self.theme["chart_colors"]
        self.currency_symbol = currency_symbol
        self.generated_charts = {}

    @staticmethod
    def safe_divide(numerator, denominator):
        """Safe division: mask zero denominators and inf/-inf"""
        if denominator == 0 or pd.isna(denominator):
            return np.nan
        result = numerator / denominator
        if np.isinf(result):
            return np.nan
        return result

    def format_currency(self, val):
        """Format number with detected currency symbol safely"""
        if pd.isna(val):
            return "N/A"
        sym = self.currency_symbol
        abs_v = abs(val)
        if abs_v >= 1e9:
            return f"{sym}{val/1e9:.2f}B"
        if abs_v >= 1e6:
            return f"{sym}{val/1e6:.2f}M"
        if abs_v >= 1e3:
            return f"{sym}{val/1e3:.1f}K"
        return f"{sym}{val:,.2f}"

    def create_kpi_cards(self, df, numeric_cols, max_cards=3):
        """Create KPI metric cards with safe math and dynamic currency"""
        kpis = {}
        for col in numeric_cols[:max_cards]:
            try:
                clean_s = df[col].dropna()
                total = clean_s.sum() if len(clean_s) > 0 else np.nan
                count = int(clean_s.count())
                avg = self.safe_divide(total, count)
                
                kpis[col] = {
                    "total": self.format_currency(total),
                    "average": self.format_currency(avg),
                    "count": f"{count:,}",
                    "raw_total": total,
                    "raw_avg": avg
                }
            except Exception:
                kpis[col] = {
                    "total": "N/A", "average": "N/A", "count": "0",
                    "raw_total": np.nan, "raw_avg": np.nan
                }
        return kpis

    def generate_executive_insights(self, df, numeric_cols, category_cols):
        """Generate 3 pure-math insights (Pareto, Growth/Spread, Completeness)"""
        insights = []
        try:
            if len(category_cols) > 0 and len(numeric_cols) > 0:
                cat_col = category_cols[0]
                metric_col = numeric_cols[0]
                breakdown = df.groupby(cat_col)[metric_col].sum().sort_values(ascending=False)
                total_volume = breakdown.sum()
                
                if total_volume > 0:
                    top_20_count = max(1, int(len(breakdown) * 0.2))
                    top_20_volume = breakdown.head(top_20_count).sum()
                    pareto_share = self.safe_divide(top_20_volume, total_volume) * 100
                    if not pd.isna(pareto_share):
                        insights.append(f"📊 Pareto Concentration: Top 20% categories drive {pareto_share:.1f}% of total {metric_col}")
        except Exception:
            pass

        try:
            if len(numeric_cols) > 0:
                data = df[numeric_cols[0]].dropna()
                if len(data) > 1:
                    mean_val = data.mean()
                    spread = data.max() - data.min()
                    volatility = self.safe_divide(spread, mean_val) * 100
                    if not pd.isna(volatility):
                        insights.append(f"📈 Volatility Index: {volatility:.1f}% spread between peak and baseline values")
        except Exception:
            pass

        try:
            if len(numeric_cols) > 0:
                total_cells = len(df) * len(numeric_cols)
                non_null = sum(df[col].count() for col in numeric_cols)
                completeness = self.safe_divide(non_null, total_cells) * 100
                if not pd.isna(completeness):
                    insights.append(f"✅ Data Completeness: {completeness:.1f}% valid data points across all metric fields")
        except Exception:
            pass

        return insights if insights else ["Dataset ready for executive review."]

    def create_trend_chart(self, df, date_col, numeric_cols):
        """Create line chart for time-series trends"""
        try:
            if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
                df = df.copy()
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            df_clean = df.dropna(subset=[date_col]).sort_values(date_col)
            if len(df_clean) == 0:
                return self._error_chart("No valid dates found"), f"err_{uuid.uuid4().hex[:8]}"

            fig = go.Figure()
            for i, col in enumerate(numeric_cols[:2]):
                valid_data = df_clean[[date_col, col]].dropna()
                if len(valid_data) > 0:
                    fig.add_trace(go.Scatter(
                        x=valid_data[date_col],
                        y=valid_data[col],
                        mode='lines+markers',
                        name=col,
                        line=dict(color=self.chart_colors[i % len(self.chart_colors)], width=3),
                        marker=dict(size=6),
                        hovertemplate=f'<b>{col}</b><br>%{{x|%Y-%m-%d}}<br>Value: %{{y:,.2f}}<extra></extra>'
                    ))

            fig.update_layout(
                title=f"Trend Analysis: {', '.join(numeric_cols[:2])}",
                xaxis_title=date_col,
                yaxis_title="Metric Value",
                hovermode="x unified",
                height=420,
                margin=dict(l=40, r=40, t=50, b=40),
                plot_bgcolor=self.theme["bg_secondary"],
                paper_bgcolor=self.theme["bg_primary"],
                font=dict(color=self.theme["text_primary"]),
                showlegend=True
            )
            chart_id = f"chart_trend_{uuid.uuid4().hex[:8]}"
            self.generated_charts[chart_id] = fig
            return fig, chart_id
        except Exception as e:
            return self._error_chart(f"Trend Error: {str(e)}"), f"err_{uuid.uuid4().hex[:8]}"

    def create_bar_chart(self, df, category_col, metric_col):
        """Create bar chart with automatic high-cardinality aggregation (Top 10 + Others)"""
        try:
            df_clean = df[[category_col, metric_col]].dropna()
            breakdown = df_clean.groupby(category_col)[metric_col].sum().sort_values(ascending=False)
            
            threshold = QA_THRESHOLDS.get("high_cardinality_threshold", 10)
            if len(breakdown) > threshold:
                top_n = breakdown.head(threshold).copy()
                top_n["Others"] = breakdown.iloc[threshold:].sum()
                breakdown = top_n

            colors = [self.chart_colors[i % len(self.chart_colors)] for i in range(len(breakdown))]
            fig = go.Figure(data=[
                go.Bar(
                    x=breakdown.index.astype(str),
                    y=breakdown.values,
                    marker=dict(color=colors),
                    text=[f"{v:,.0f}" for v in breakdown.values],
                    textposition="outside",
                    hovertemplate=f'<b>%{{x}}</b><br>{metric_col}: %{{y:,.2f}}<extra></extra>'
                )
            ])
            fig.update_layout(
                title=f"Category Breakdown: {metric_col} by {category_col}",
                xaxis_title=category_col,
                yaxis_title=metric_col,
                height=420,
                margin=dict(l=40, r=40, t=50, b=60),
                xaxis_tickangle=-30,
                plot_bgcolor=self.theme["bg_secondary"],
                paper_bgcolor=self.theme["bg_primary"],
                font=dict(color=self.theme["text_primary"]),
                showlegend=False
            )
            chart_id = f"chart_bar_{uuid.uuid4().hex[:8]}"
            self.generated_charts[chart_id] = fig
            return fig, chart_id
        except Exception as e:
            return self._error_chart(f"Bar Chart Error: {str(e)}"), f"err_{uuid.uuid4().hex[:8]}"

    def create_pie_chart(self, df, category_col, metric_col):
        """Create pie chart for distribution"""
        try:
            df_clean = df[[category_col, metric_col]].dropna()
            distribution = df_clean.groupby(category_col)[metric_col].sum().sort_values(ascending=False)
            
            if len(distribution) > 8:
                top_8 = distribution.head(8).copy()
                top_8["Others"] = distribution.iloc[8:].sum()
                distribution = top_8

            fig = go.Figure(data=[
                go.Pie(
                    labels=distribution.index.astype(str),
                    values=distribution.values,
                    marker=dict(colors=self.chart_colors),
                    textinfo="percent+label",
                    hovertemplate='<b>%{label}</b><br>Value: %{value:,.2f} (%{percent})<extra></extra>'
                )
            ])
            fig.update_layout(
                title=f"{category_col} Distribution",
                height=420,
                margin=dict(l=30, r=30, t=50, b=30),
                paper_bgcolor=self.theme["bg_primary"],
                font=dict(color=self.theme["text_primary"]),
                showlegend=True
            )
            chart_id = f"chart_pie_{uuid.uuid4().hex[:8]}"
            self.generated_charts[chart_id] = fig
            return fig, chart_id
        except Exception as e:
            return self._error_chart(f"Pie Chart Error: {str(e)}"), f"err_{uuid.uuid4().hex[:8]}"

    def create_histogram(self, df, metric_col):
        """Create distribution histogram with IQR outlier containment"""
        try:
            data = df[metric_col].dropna()
            if len(data) == 0:
                return self._error_chart("No data available"), f"err_{uuid.uuid4().hex[:8]}"

            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            bounded = data[(data >= q1 - 1.5 * iqr) & (data <= q3 + 1.5 * iqr)]

            fig = go.Figure(data=[
                go.Histogram(
                    x=bounded if len(bounded) > 0 else data,
                    nbinsx=25,
                    marker=dict(color=self.chart_colors[2 % len(self.chart_colors)]),
                    hovertemplate=f'<b>{metric_col}</b><br>Range: %{{x}}<br>Count: %{{y}}<extra></extra>'
                )
            ])
            fig.update_layout(
                title=f"Distribution Profile: {metric_col}",
                xaxis_title=metric_col,
                yaxis_title="Frequency",
                height=420,
                margin=dict(l=40, r=40, t=50, b=40),
                plot_bgcolor=self.theme["bg_secondary"],
                paper_bgcolor=self.theme["bg_primary"],
                font=dict(color=self.theme["text_primary"]),
                showlegend=False
            )
            chart_id = f"chart_hist_{uuid.uuid4().hex[:8]}"
            self.generated_charts[chart_id] = fig
            return fig, chart_id
        except Exception as e:
            return self._error_chart(f"Histogram Error: {str(e)}"), f"err_{uuid.uuid4().hex[:8]}"

    def _error_chart(self, message):
        fig = go.Figure()
        fig.add_annotation(
            text=message, xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color="#ff6b6b")
        )
        fig.update_layout(
            title="Chart Generation Alert", height=400,
            plot_bgcolor=self.theme["bg_secondary"], paper_bgcolor=self.theme["bg_primary"]
        )
        return fig
