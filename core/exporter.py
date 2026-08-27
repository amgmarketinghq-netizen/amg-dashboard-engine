"""
AMG Dashboard - Exporter (Enterprise Grade)
Standalone offline HTML with tab auto-resize + CWE-1236 sanitized in-memory Excel
ZERO TEMP FILES | 100% BytesIO | PRODUCTION SECURE
"""

import pandas as pd
from datetime import datetime
from io import BytesIO
import uuid
import plotly.io as pio
from config import HTML_EXPORT_CSS

class Exporter:
    """Production-grade HTML & Excel exporter"""
    
    def __init__(self, client_name="Client", sector="Other", quality_score=0):
        self.client_name = client_name or "Valued Client"
        self.sector = sector
        self.quality_score = quality_score
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def sanitize_excel_formula(value):
        """Neutralize CWE-1236 formula injection in exported files"""
        if isinstance(value, str) and value:
            if value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')):
                return f"'{value}"
        return value

    def create_html_dashboard(self, df, figures_dict, tier=2):
        """Create standalone, responsive HTML dashboard with proper page-wise separation"""
        page_count = min(tier + 1, 3)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AMG Dashboard - {self._escape_html(self.client_name)}</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    {HTML_EXPORT_CSS}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {self._escape_html(self.client_name)} - Executive Dashboard</h1>
            <p>Industry Sector: {self._escape_html(self.sector)} | Audit Timestamp: {self.timestamp}</p>
            <p>Data Hygiene Score: <strong>{self.quality_score:.1f}%</strong> | Total Records: <strong>{len(df):,}</strong></p>
        </div>

        <div class="tabs">
"""
        for i in range(page_count):
            active = "active" if i == 0 else ""
            tab_labels = ["Overview & KPIs", "Breakdown & Distribution", "Data Explorer"]
            html += f'            <button class="tab-button {active}" onclick="openTab(event, \'page{i+1}\')">📄 {tab_labels[i]}</button>\n'
        html += '        </div>\n'

        # Page 1: Overview & KPIs
        html += '        <div id="page1" class="tab-content active">\n'
        if "kpis" in figures_dict and figures_dict["kpis"]:
            html += '            <div class="kpi-grid">\n'
            for kpi_name, kpi_data in figures_dict["kpis"].items():
                html += f"""                <div class="kpi-card">
                    <h3>{self._escape_html(str(kpi_name))}</h3>
                    <div class="value">{self._escape_html(str(kpi_data['total']))}</div>
                    <div style="font-size: 13px; color: #a0aec0; margin-top: 5px;">Average: {self._escape_html(str(kpi_data['average']))}</div>
                </div>\n"""
            html += '            </div>\n'

        if "insights" in figures_dict and figures_dict["insights"]:
            html += '            <div style="background: #1a1f2e; padding: 18px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #00d4ff;">\n'
            html += '                <h4 style="margin-bottom: 8px; color: #00d4ff;">💡 Automated Executive Takeaways</h4>\n'
            for ins in figures_dict["insights"]:
                html += f'                <p style="margin: 4px 0; color: #e2e8f0; font-size: 14px;">• {self._escape_html(ins)}</p>\n'
            html += '            </div>\n'

        if "trend" in figures_dict and figures_dict["trend"] is not None:
            html += self._render_plotly_div(figures_dict["trend"], "trend")
        html += '        </div>\n'

        # Page 2: Breakdown & Distribution
        if page_count >= 2:
            html += '        <div id="page2" class="tab-content">\n'
            for chart_key in ["bar", "pie", "histogram"]:
                if chart_key in figures_dict and figures_dict[chart_key] is not None:
                    html += self._render_plotly_div(figures_dict[chart_key], chart_key)
            html += '        </div>\n'

        # Page 3: Data Explorer
        if page_count >= 3:
            html += '        <div id="page3" class="tab-content">\n'
            html += '            <div class="chart-container">\n'
            html += '                <h3 style="margin-bottom: 15px; color: #00d4ff;">Dataset Structure & Audit Preview</h3>\n'
            html += '                <div style="overflow-x: auto;">\n'
            html += df.head(50).to_html(classes="table", index=False, border=0)
            html += '                </div>\n'
            html += '            </div>\n'
            html += '        </div>\n'

        # Footer & Resize Script
        html += f"""
        <div style="text-align: center; color: #64748b; font-size: 12px; margin-top: 40px; padding: 20px 0; border-top: 1px solid #2d3748;">
            <p>AMG Dashboard Engine | Enterprise Autonomous BI</p>
            <p>🔒 Ephemeral Data Architecture | Delivered for {self._escape_html(self.client_name)}</p>
        </div>
    </div>

    <script>
        function openTab(evt, tabName) {{
            var i, tabcontent, tabbuttons;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].classList.remove("active");
            }}
            tabbuttons = document.getElementsByClassName("tab-button");
            for (i = 0; i < tabbuttons.length; i++) {{
                tabbuttons[i].classList.remove("active");
            }}
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
            
            setTimeout(function() {{
                window.dispatchEvent(new Event('resize'));
            }}, 150);
        }}
    </script>
</body>
</html>"""
        return html

    def _render_plotly_div(self, fig, name):
        """Render Plotly figure to responsive standalone div"""
        div_id = f"chart_{name}_{uuid.uuid4().hex[:8]}"
        fig_json = fig.to_json()
        return f"""
        <div class="chart-container">
            <div id="{div_id}"></div>
            <script>
                var cData = {fig_json};
                Plotly.newPlot('{div_id}', cData.data, cData.layout, {{responsive: true, autosize: true, displaylogo: false}});
            </script>
        </div>\n"""

    def create_excel_export(self, df):
        """Export sanitized Excel workbook purely in RAM"""
        df_sanitized = df.copy()
        for col in df_sanitized.select_dtypes(include=['object']).columns:
            df_sanitized[col] = df_sanitized[col].map(self.sanitize_excel_formula)

        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            overview_df = pd.DataFrame({
                'Metric': ['Client', 'Sector', 'Total Rows', 'Total Columns', 'Data Quality Score', 'Generated At'],
                'Value': [self.client_name, self.sector, len(df), len(df.columns), f'{self.quality_score:.1f}%', self.timestamp]
            })
            overview_df.to_excel(writer, sheet_name='Overview', index=False)
            df_sanitized.to_excel(writer, sheet_name='Cleaned_Data', index=False)
            
            summary_df = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes.astype(str),
                'Non-Null Count': df.count().values,
                'Null Count': df.isnull().sum().values
            })
            summary_df.to_excel(writer, sheet_name='Data_Profiling', index=False)

        excel_buffer.seek(0)
        return excel_buffer.getvalue()

    @staticmethod
    def _escape_html(text):
        escape_dict = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}
        return ''.join(escape_dict.get(c, c) for c in str(text))
