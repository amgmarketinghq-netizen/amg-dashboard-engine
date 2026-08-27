"""
AMG Dashboard - Chart Builder (Enterprise Grade)
Universal Visualizations for Financial, Sales, and Pure CRM/Lead Datasets
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import uuid
from config import THEMES, QA_THRESHOLDS

class ChartBuilder:
    """Production-grade Plotly chart generator with CRM and Financial support"""
    
    def __init__(self, theme="Professional Dark", currency_symbol="$"):
        self.theme = THEMES.get(theme, THEMES["Professional Dark"])
        self.chart_colors = self.theme["chart_colors"]
        self.currency_symbol = currency_symbol
        self.generated_charts = {}

    @staticmethod
    def safe_divide(numerator, denominator):
        if denominator == 0 or pd.isna(denominator):
            return np.nan
        result = numerator / denominator
        return np.nan if np.isinf(result) else result

    def format_currency(self, val, is_crm=False):
        if pd.isna(val):
            return "N/A"
        if is_crm:
            return f"{int(val):,}" if abs(val) >= 1 else f"{val:.2f}"
        sym = self.currency_symbol
        abs_v = abs(val)
        if abs_v >= 1e9:
            return f"{sym}{val/1e9:.2f}B"
        if abs_v >= 1e6:
            return f"{sym}{val/1e6:.2f}M"
        if abs_v >= 1e3:
            return f"{sym}{val/1e3:.1f}K"
        return f"{sym}{val:,.2f}"

    def create_kpi_cards(self, df, numeric_cols, category_cols):
        """Create dynamic KPI metric cards for both Numeric and CRM datasets"""
        kpis = {}
        
        # Financial/Numeric KPIs
        real_numeric = [c for c in numeric_cols if c != "Record Count"]
        if real_numeric:
            for col in real_numeric[:3]:
                clean_s = df[col].dropna()
                total = clean_s.sum() if len(clean_s) > 0 else np.nan
                count = int(clean_s.count())
                avg = self.safe_divide(total, count)
                kpis[col] = {
                    "total": self.format_currency(total),
                    "average": self.format_currency(avg),
                    "count": f"{count:,}"
                }
        else:
            # CRM / Lead List Fallback KPIs
            total_records = len(df)
            kpis["Total Database Records"] = {
                "total": f"{total_records:,}",
                "average": "100% Ingested",
                "count": f"{total_records:,}"
            }
            if len(category_cols) > 0:
                top_cat = category_cols[0]
                unique_entities = df[top_cat].nunique()
                kpis[f"Unique {top_cat}"] = {
                    "total": f"{unique_entities:,}",
                    "average": f"Categories",
                    "count": f"{unique_entities:,}"
                }
            if len(category_cols) > 1:
                sub_cat = category_cols[1]
                unique_sub = df[sub_cat].nunique()
                kpis[f"Unique {sub_cat}"] = {
                    "total": f"{unique_sub:,}",
                    "average": f"Segments",
                    "count": f"{unique_sub:,}"
                }

        return kpis

    def generate_executive_insights(self, df, numeric_cols, category_cols):
        """Generate insights for Financial or CRM Lead datasets"""
        insights = []
        real_numeric = [c for c in numeric_cols if c != "Record Count"]

        if real_numeric and category_cols:
            cat_col = category_cols[0]
            metric_col = real_numeric[0]
            breakdown = df.groupby(cat_col)[metric_col].sum().sort_values(ascending=False)
            total_vol = breakdown.sum()
            if total_vol > 0:
                top_20_count = max(1, int(len(breakdown) * 0.2))
                top_20_vol = breakdown.head(top_20_count).sum()
                pareto_share = self.safe_divide(top_20_vol, total_vol) * 100
                insights.append(f"📊 Pareto Volume: Top 20% of {cat_col} controls {pareto_share:.1f}% of {metric_col}")
        elif category_cols:
            # CRM Insight: Top Concentration
            cat_col = category_cols[0]
            top_val = df[cat_col].value_counts()
            if not top_val.empty:
                top_pct = (top_val.iloc[0] / len(df)) * 100
                insights.append(f"🎯 Market Dominance: Leading {cat_col} ('{top_val.index[0]}') represents {top_pct:.1f}% of total records")
            if len(category_cols) > 1:
                sub_col = category_cols[1]
                insights.append(f"📌 Segment Diversity: Identified {df[sub_col].nunique():,} distinct categories across '{sub_col}'")

        fill_rate = (df.notnull().sum().sum() / df.size) * 100
        insights.append(f"✅ Data Hygiene: Overall record completeness is at {fill_rate:.1f}% across all fields")

        return insights

    def create_trend_chart(self, df, date_col, numeric_cols):
        try:
            df_clean = df.dropna(subset=[date_col]).sort_values(date_col)
            fig = go.Figure()
            target_cols = [c for c in numeric_cols if c != "Record Count"][:2] or numeric_cols[:1]
            for i, col in enumerate(target_cols):
                valid_data = df_clean[[date_col, col]].dropna()
                if len(valid_data) > 0:
                    fig.add_trace(go.Scatter(
                        x=valid_data[date_col], y=valid_data[col],
                        mode='lines+markers', name=col,
                        line=dict(color=self.chart_colors[i % len(self.chart_colors)], width=3),
                        marker=dict(size=6)
                    ))
            fig.update_layout(
                title=f"Temporal Trend Analysis", xaxis_title=date_col, yaxis_title="Volume",
                hovermode="x unified", height=420, margin=dict(l=40, r=40, t=50, b=40),
                plot_bgcolor=self.theme["bg_secondary"], paper_bgcolor=self.theme["bg_primary"],
                font=dict(color=self.theme["text_primary"])
            )
            return fig, f"chart_trend_{uuid.uuid4().hex[:8]}"
        except Exception as e:
            return self._error_chart(f"Trend: {str(e)}"), f"err_{uuid.uuid4().hex[:8]}"

    def create_bar_chart(self, df, category_col, metric_col="Record Count"):
        try:
            if metric_col == "Record Count" or metric_col not in df.columns:
                breakdown = df[category_col].value_counts()
                title_metric = "Record Volume"
            else:
                breakdown = df.groupby(category_col)[metric_col].sum().sort_values(ascending=False)
                title_metric = metric_col

            threshold = QA_THRESHOLDS.get("high_cardinality_threshold", 10)
            if len(breakdown) > threshold:
                top_n = breakdown.head(threshold).copy()
                top_n["Others"] = breakdown.iloc[threshold:].sum()
                breakdown = top_n

            colors = [self.chart_colors[i % len(self.chart_colors)] for i in range(len(breakdown))]
            fig = go.Figure(data=[
                go.Bar(
                    x=breakdown.index.astype(str), y=breakdown.values,
                    marker=dict(color=colors),
                    text=[f"{v:,.0f}" for v in breakdown.values], textposition="outside"
                )
            ])
            fig.update_layout(
                title=f"Top {len(breakdown)} {category_col} by {title_metric}",
                xaxis_title=category_col, yaxis_title=title_metric, height=420,
                margin=dict(l=40, r=40, t=50, b=60), xaxis_tickangle=-30,
                plot_bgcolor=self.theme["bg_secondary"], paper_bgcolor=self.theme["bg_primary"],
                font=dict(color=self.theme["text_primary"])
            )
            return fig, f"chart_bar_{uuid.uuid4().hex[:8]}"
        except Exception as e:
            return self._error_chart(f"Bar: {str(e)}"), f"err_{uuid.uuid4().hex[:8]}"

    def create_pie_chart(self, df, category_col, metric_col="Record Count"):
        try:
            if metric_col == "Record Count" or metric_col not in df.columns:
                distribution = df[category_col].value_counts()
            else:
                distribution = df.groupby(category_col)[metric_col].sum().sort_values(ascending=False)

            if len(distribution) > 8:
                top_8 = distribution.head(8).copy()
                top_8["Others"] = distribution.iloc[8:].sum()
                distribution = top_8

            fig = go.Figure(data=[
                go.Pie(
                    labels=distribution.index.astype(str), values=distribution.values,
                    marker=dict(colors=self.chart_colors), textinfo="percent+label"
                )
            ])
            fig.update_layout(
                title=f"{category_col} Market Share Distribution", height=420,
                margin=dict(l=30, r=30, t=50, b=30), paper_bgcolor=self.theme["bg_primary"],
                font=dict(color=self.theme["text_primary"])
            )
            return fig, f"chart_pie_{uuid.uuid4().hex[:8]}"
        except Exception as e:
            return self._error_chart(f"Pie: {str(e)}"), f"err_{uuid.uuid4().hex[:8]}"

    def create_histogram(self, df, metric_col):
        try:
            data = df[metric_col].dropna()
            fig = go.Figure(data=[go.Histogram(x=data, nbinsx=25, marker=dict(color=self.chart_colors[2]))])
            fig.update_layout(
                title=f"Frequency Profile: {metric_col}", xaxis_title=metric_col, yaxis_title="Count",
                height=420, margin=dict(l=40, r=40, t=50, b=40),
                plot_bgcolor=self.theme["bg_secondary"], paper_bgcolor=self.theme["bg_primary"],
                font=dict(color=self.theme["text_primary"])
            )
            return fig, f"chart_hist_{uuid.uuid4().hex[:8]}"
        except Exception as e:
            return self._error_chart(f"Hist: {str(e)}"), f"err_{uuid.uuid4().hex[:8]}"

    def _error_chart(self, message):
        fig = go.Figure()
        fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(color="#ff6b6b"))
        fig.update_layout(height=400, plot_bgcolor=self.theme["bg_secondary"], paper_bgcolor=self.theme["bg_primary"])
        return fig
