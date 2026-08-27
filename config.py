"""
AMG Dashboard Engine - Global Configuration
Enterprise-grade theme, currency, sector, and multiplier definitions
"""

THEMES = {
    "Professional Dark": {
        "bg_primary": "#0f1419",
        "bg_secondary": "#1a1f2e",
        "accent": "#00d4ff",
        "accent_alt": "#ff6b6b",
        "text_primary": "#ffffff",
        "text_secondary": "#a0aec0",
        "chart_colors": [
            "#00d4ff", "#ff6b6b", "#51cf66", "#ffd93d",
            "#a78bfa", "#06b6d4", "#ec4899", "#f97316"
        ]
    },
    "Clean Light": {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f7f9fc",
        "accent": "#2563eb",
        "accent_alt": "#dc2626",
        "text_primary": "#1a202c",
        "text_secondary": "#64748b",
        "chart_colors": [
            "#2563eb", "#dc2626", "#16a34a", "#ca8a04",
            "#9333ea", "#0891b2", "#be185d", "#ea580c"
        ]
    }
}

CURRENCY_SYMBOLS = {
    "$": {"name": "US Dollar", "region": "US/Global", "code": "USD"},
    "€": {"name": "Euro", "region": "EU", "code": "EUR"},
    "£": {"name": "British Pound", "region": "UK", "code": "GBP"},
    "¥": {"name": "Yen/Yuan", "region": "Asia", "code": "JPY/CNY"},
    "₹": {"name": "Indian Rupee", "region": "India", "code": "INR"},
    "AED": {"name": "UAE Dirham", "region": "Middle East", "code": "AED"},
    "CAD": {"name": "Canadian Dollar", "region": "Canada", "code": "CAD"},
    "AUD": {"name": "Australian Dollar", "region": "Australia", "code": "AUD"},
}

GLOBAL_MULTIPLIERS = {
    "T": 1e12,
    "B": 1e9,
    "M": 1e6,
    "K": 1e3,
}

INDIAN_MULTIPLIERS = {
    "CRORE": 1e7,
    "CR": 1e7,
    "LAKH": 1e5,
    "L": 1e5,
}

ALL_MULTIPLIERS = {**GLOBAL_MULTIPLIERS, **INDIAN_MULTIPLIERS}

SECTOR_DEFINITIONS = {
    "Sales/B2B": {
        "name": "Sales & B2B",
        "key_metrics": ["Revenue", "Orders", "Customers", "AOV", "Units Sold"],
        "chart_priority": ["Trend", "Category", "Distribution"],
        "regions": ["US", "EU", "UK", "Middle East", "India/Asia"]
    },
    "Finance": {
        "name": "Finance & Banking",
        "key_metrics": ["Total Amount", "Transaction Count", "Avg Transaction", "Growth Rate"],
        "chart_priority": ["Trend", "Category", "Distribution"],
        "regions": ["Global"]
    },
    "Operations": {
        "name": "Operations & Logistics",
        "key_metrics": ["Processing Time", "Shipments", "Efficiency Rate", "On-Time Delivery"],
        "chart_priority": ["Trend", "Category", "Distribution"],
        "regions": ["Global"]
    },
    "Customer/CRM": {
        "name": "Customer & CRM",
        "key_metrics": ["Total Customers", "Lifetime Value", "Retention Rate", "Churn"],
        "chart_priority": ["Category", "Trend", "Distribution"],
        "regions": ["Global"]
    },
    "E-commerce": {
        "name": "E-commerce",
        "key_metrics": ["Total Sales", "Orders", "AOV", "Conversion Rate"],
        "chart_priority": ["Trend", "Category", "Distribution"],
        "regions": ["Global"]
    },
    "Healthcare": {
        "name": "Healthcare",
        "key_metrics": ["Patient Count", "Treatment Cost", "Success Rate", "Avg Stay"],
        "chart_priority": ["Category", "Trend", "Distribution"],
        "regions": ["US", "EU", "UK"]
    },
    "Logistics": {
        "name": "Logistics",
        "key_metrics": ["Deliveries", "Distance", "Cost", "Time Efficiency"],
        "chart_priority": ["Trend", "Category", "Distribution"],
        "regions": ["Global"]
    },
    "Real Estate": {
        "name": "Real Estate",
        "key_metrics": ["Property Count", "Total Value", "Avg Price", "Sales Rate"],
        "chart_priority": ["Category", "Trend", "Distribution"],
        "regions": ["US", "EU", "India/Asia"]
    },
    "Marketing": {
        "name": "Marketing",
        "key_metrics": ["Campaign Spend", "Reach", "Conversions", "ROI"],
        "chart_priority": ["Trend", "Category", "Distribution"],
        "regions": ["Global"]
    },
}

TIER_DEFINITIONS = {
    1: {"name": "Tier 1 - Simple", "pages": 2, "price_usd": 80, "price_inr": 4000},
    2: {"name": "Tier 2 - Professional", "pages": 3, "price_usd": 250, "price_inr": 10000},
    3: {"name": "Tier 3 - Advanced", "pages": 5, "price_usd": 600, "price_inr": 25000},
}

QA_THRESHOLDS = {
    "empty_cells_max_pct": 15,
    "duplicates_max_pct": 10,
    "min_numeric_columns": 1,
    "quality_score_good": 80,
    "quality_score_warning": 60,
    "high_cardinality_threshold": 10,
}

ANTI_ID_PATTERNS = {
    "exact_match": [
        "id", "code", "pincode", "zip", "postal", "invoice",
        "sku", "vat", "iban", "phone", "ssn", "customer_id",
        "order_id", "transaction_id", "reference", "account_no"
    ],
    "contains_patterns": [
        "id_", "_id", "code_", "_code", "num_", "_num", "postal"
    ]
}

ENCODING_PRIORITY = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]

MODE_B_METADATA_SHEETS = {
    "exclude_patterns": [
        "audit", "log", "profiling", "profile", "data dictionary",
        "readme", "summary", "notes", "instructions", "metadata",
        "config", "settings", "schema"
    ]
}

MODE_B_PRIMARY_SHEET_PATTERNS = [
    "cleaned data", "clean data", "master data", "fact",
    "main", "data", "records", "customers", "transactions",
    "orders", "sales", "results"
]

HTML_EXPORT_CSS = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f1419; color: #ffffff; line-height: 1.6; }
    .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
    .header { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%); padding: 30px; border-radius: 12px; border-left: 5px solid #00d4ff; margin-bottom: 30px; }
    .header h1 { font-size: 28px; margin-bottom: 10px; color: #00d4ff; }
    .tabs { display: flex; gap: 10px; margin-bottom: 30px; border-bottom: 2px solid #1a1f2e; padding-bottom: 15px; flex-wrap: wrap; }
    .tab-button { padding: 10px 20px; background: #1a1f2e; border: 1px solid #2d3748; color: #a0aec0; cursor: pointer; border-radius: 6px; transition: all 0.3s; }
    .tab-button.active { background: #00d4ff; color: #0f1419; font-weight: bold; }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    .chart-container { background: #1a1f2e; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #2d3748; }
    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .kpi-card { background: #1a1f2e; padding: 20px; border-radius: 10px; border-left: 4px solid #00d4ff; }
    .kpi-card h3 { font-size: 13px; color: #a0aec0; margin-bottom: 10px; text-transform: uppercase; }
    .kpi-card .value { font-size: 24px; font-weight: bold; color: #00d4ff; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; color: #e2e8f0; font-size: 13px; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #2d3748; }
    th { background: #0f1419; color: #00d4ff; }
    @media print {
        body { background: white; color: black; }
        .header { background: #f5f5f5; }
        .tab-button { display: none; }
        .tab-content { display: block !important; }
        .chart-container { page-break-inside: avoid; }
    }
</style>
"""

CUSTOM_CSS = """
<style>
    .main { background-color: #0e1117; }
</style>
"""

SESSION_STATE_DEFAULTS = {
    "file_uploaded": False,
    "ingestion_mode": "A",
    "dataframe": None,
    "cleaned_df": None,
    "qa_report": None,
    "numeric_cols": [],
    "date_cols": [],
    "category_cols": [],
    "dashboard_generated": False,
    "figures": {},
    "client_name": "",
    "sector": "Sales/B2B",
    "tier": 2,
    "theme": "Professional Dark"
}
