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
