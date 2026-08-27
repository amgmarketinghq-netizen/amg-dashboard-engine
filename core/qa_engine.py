"""
AMG Dashboard - QA Engine (Enterprise Grade)
Ultra-Robust Header Alignment, Universal Numeric Coercer, Excel Serial Date Resolver,
and Bulletproof Categorical Ingestion
"""

import pandas as pd
import numpy as np
import chardet
import re
from io import BytesIO
from datetime import datetime
from config import (
    ENCODING_PRIORITY, CURRENCY_SYMBOLS, ALL_MULTIPLIERS,
    ANTI_ID_PATTERNS, MODE_B_METADATA_SHEETS, MODE_B_PRIMARY_SHEET_PATTERNS,
    QA_THRESHOLDS
)

class QAEngine:
    """Production-grade QA and profiling engine with zero hallucinations"""
    
    def __init__(self):
        self.qa_report = {}
        self.warnings = []
        self.errors = []
        self.numeric_cols = []
        self.date_cols = []
        self.category_cols = []
        self.conversion_log = []

    def detect_encoding(self, file_bytes: bytes) -> str:
        """Detect CSV encoding safely"""
        try:
            detected = chardet.detect(file_bytes)
            detected_encoding = detected.get('encoding', 'utf-8')
            if detected_encoding and detected_encoding.lower() in [e.lower() for e in ENCODING_PRIORITY]:
                return detected_encoding
            for encoding in ENCODING_PRIORITY:
                try:
                    file_bytes.decode(encoding)
                    return encoding
                except Exception:
                    pass
            return 'utf-8'
        except Exception as e:
            self.warnings.append(f"⚠️ Encoding detection fallback: {str(e)}")
            return 'utf-8'

    def align_and_sanitize_headers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Auto-detect real header row if top rows contain metadata or blank banners"""
        if df.empty:
            return df
        
        # Check if row 0 is mostly unnamed or empty
        unnamed_cols = [c for c in df.columns if str(c).startswith("Unnamed:") or pd.isna(c)]
        if len(unnamed_cols) > (len(df.columns) * 0.4):
            for i in range(min(5, len(df))):
                row_vals = df.iloc[i].dropna().astype(str).tolist()
                if len(row_vals) >= (len(df.columns) * 0.5):
                    df.columns = [str(x).strip() for x in df.iloc[i].values]
                    df = df.iloc[i+1:].reset_index(drop=True)
                    break

        # Sanitize column names
        cols = [str(c).strip().replace('\n', ' ').replace('\r', ' ') for c in df.columns]
        cols = [re.sub(r'\s+', ' ', c) for c in cols]
        
        seen = {}
        new_cols = []
        for col in cols:
            col_clean = col if col and not col.startswith("Unnamed:") else f"Field_{len(new_cols)+1}"
            if col_clean in seen:
                seen[col_clean] += 1
                new_cols.append(f"{col_clean}_{seen[col_clean]}")
            else:
                seen[col_clean] = 0
                new_cols.append(col_clean)
        
        df.columns = new_cols
        return df

    def load_workbook_safely(self, file_name: str, file_bytes: bytes):
        """Universal router for CSV and Excel workbooks"""
        bio = BytesIO(file_bytes)
        
        if file_name.lower().endswith('.csv'):
            encoding = self.detect_encoding(file_bytes)
            try:
                df = pd.read_csv(bio, encoding=encoding)
                df = self.align_and_sanitize_headers(df)
                return df, "A"
            except Exception as e:
                self.errors.append(f"❌ Failed to parse CSV: {str(e)}")
                return None, "INVALID"
        
        try:
            xl_file = pd.ExcelFile(bio)
            sheet_names = xl_file.sheet_names
            
            valid_sheets = []
            for sheet in sheet_names:
                sheet_lower = sheet.lower().strip()
                if not any(pat in sheet_lower for pat in MODE_B_METADATA_SHEETS['exclude_patterns']):
                    valid_sheets.append(sheet)
            
            if not valid_sheets:
                valid_sheets = sheet_names
            
            mode = "A"
            selected_sheet = valid_sheets[0]
            
            for s in valid_sheets:
                s_lower = s.lower().strip()
                if any(p in s_lower for p in MODE_B_PRIMARY_SHEET_PATTERNS):
                    selected_sheet = s
                    mode = "B"
                    break
            
            if mode == "A":
                sheet_scores = {}
                for s in valid_sheets:
                    bio.seek(0)
                    try:
                        probe = pd.read_excel(bio, sheet_name=s, nrows=5)
                        sheet_scores[s] = probe.shape[1]
                    except Exception:
                        sheet_scores[s] = 0
                selected_sheet = max(sheet_scores, key=sheet_scores.get)
            
            bio.seek(0)
            df = pd.read_excel(bio, sheet_name=selected_sheet)
            df = self.align_and_sanitize_headers(df)
            return df, mode
            
        except Exception as e:
            self.errors.append(f"❌ Failed to load Excel workbook: {str(e)}")
            return None, "INVALID"

    def coerce_numeric_column(self, series: pd.Series, col_name: str):
        """Ultra-flexible numeric parser with currency/unit stripping"""
        log = {"column": col_name, "success": 0, "failed": 0, "nulls": 0}
        
        def parse_val(val):
            if pd.isna(val):
                log["nulls"] += 1
                return np.nan
            if isinstance(val, (int, float, np.number)):
                log["success"] += 1
                return float(val)
            
            s = str(val).strip()
            if s.lower() in {'', 'nan', 'none', 'null', 'n/a', 'na', '-', '—'}:
                log["nulls"] += 1
                return np.nan
            
            # Common currency words & symbols stripping
            s = re.sub(r'(?i)(usd|inr|eur|gbp|aed|cad|aud|rs\.?|rupees?|\/\-)', '', s).strip()
            for sym in CURRENCY_SYMBOLS.keys():
                s = s.replace(sym, '')
            s = s.strip()
            
            is_negative = False
            if s.startswith('(') and s.endswith(')'):
                is_negative = True
                s = s[1:-1].strip()
            elif s.startswith('-'):
                is_negative = True
                s = s[1:].strip()
            
            multiplier = 1.0
            s_upper = s.upper()
            for mult_key, mult_val in ALL_MULTIPLIERS.items():
                if s_upper.endswith(mult_key):
                    multiplier = mult_val
                    s = s[:-len(mult_key)].strip()
                    break
            
            is_pct = '%' in s
            if is_pct:
                s = s.replace('%', '').strip()
            
            # Delimiter resolver
            if ',' in s and '.' in s:
                if s.rfind(',') > s.rfind('.'):
                    s = s.replace('.', '').replace(',', '.')
                else:
                    s = s.replace(',', '')
            elif ',' in s:
                parts = s.split(',')
                if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
                    s = ''.join(parts)
                else:
                    s = s.replace(',', '.')
            
            # Remove any trailing non-numeric artifacts
            s_clean = re.sub(r'[^\d.-]', '', s)
            
            try:
                num = float(s_clean) * multiplier
                if is_pct:
                    num /= 100.0
                if is_negative:
                    num = -abs(num)
                if np.isinf(num):
                    log["failed"] += 1
                    return np.nan
                log["success"] += 1
                return num
            except Exception:
                log["failed"] += 1
                return np.nan

        parsed_series = series.apply(parse_val)
        return parsed_series, log

    def is_id_column(self, col_name: str, series: pd.Series) -> bool:
        """Anti-ID Gate"""
        col_lower = str(col_name).lower()
        if any(pat in col_lower for pat in ANTI_ID_PATTERNS['exact_match']):
            return True
        if any(pat in col_lower for pat in ANTI_ID_PATTERNS['contains_patterns']):
            return True
        return False

    def parse_dates_smart(self, series: pd.Series, col_name: str):
        """Smart date parser with Excel serial date & Day-First resolution"""
        if self.is_id_column(col_name, series):
            return series, False
        
        # Check for Excel numeric serial dates (e.g. 44500)
        if pd.api.types.is_numeric_dtype(series):
            sample_nums = series.dropna()
            if not sample_nums.empty and sample_nums.between(35000, 60000).mean() > 0.8:
                try:
                    parsed = pd.to_datetime(sample_nums, unit='D', origin='1899-12-30', errors='coerce')
                    if parsed.notna().mean() >= 0.7:
                        return pd.to_datetime(series, unit='D', origin='1899-12-30', errors='coerce'), True
                except Exception:
                    pass

        sample = series.dropna().astype(str).head(100)
        if sample.empty:
            return series, False
        
        # Check for date keywords in header
        col_lower = str(col_name).lower()
        has_date_name = any(k in col_lower for k in ['date', 'time', 'dt', 'period', 'day', 'month', 'year'])
        
        dayfirst = False
        for val in sample:
            parts = re.split(r'[-/.]', val.strip())
            if len(parts) >= 2 and parts[0].isdigit() and int(parts[0]) > 12:
                dayfirst = True
                break
        
        try:
            parsed = pd.to_datetime(series, errors='coerce', dayfirst=dayfirst)
            if parsed.notna().mean() >= (0.4 if has_date_name else 0.65):
                return parsed, True
        except Exception:
            pass
        return series, False

    def process_and_qa(self, df: pd.DataFrame, sector: str = "Other"):
        """End-to-end data typing, coercion, and automated fallback"""
        working_df = df.copy()
        numeric_cols = []
        date_cols = []
        category_cols = []
        
        for col in working_df.columns:
            # 1. Native Numeric Check
            if pd.api.types.is_numeric_dtype(working_df[col]):
                if not self.is_id_column(col, working_df[col]):
                    numeric_cols.append(col)
                    continue
            
            # 2. Date Check
            parsed_dates, is_date = self.parse_dates_smart(working_df[col], col)
            if is_date:
                working_df[col] = parsed_dates
                date_cols.append(col)
                continue
            
            # 3. Numeric Coercion Check
            coerced, log = self.coerce_numeric_column(working_df[col], col)
            valid_ratio = coerced.notna().mean()
            
            col_lower = str(col).lower()
            num_keywords = ['sales', 'rev', 'amount', 'price', 'cost', 'qty', 'quantity', 'total', 'profit', 'val', 'rate', 'discount', 'target', 'score', 'spend', 'balance']
            threshold = 0.3 if any(k in col_lower for k in num_keywords) else 0.5
            
            if valid_ratio >= threshold and not self.is_id_column(col, working_df[col]):
                working_df[col] = coerced
                numeric_cols.append(col)
                self.conversion_log.append(log)
                continue
            
            category_cols.append(col)
        
        # BULLETPROOF FALLBACK: If 0 numeric cols found, create synthetic Count metric
        if len(numeric_cols) == 0:
            working_df["Record Count"] = 1.0
            numeric_cols.append("Record Count")
            self.warnings.append("ℹ️ Synthesized 'Record Count' metric to enable complete analytics for categorical data.")
        
        self.numeric_cols = numeric_cols
        self.date_cols = date_cols
        self.category_cols = category_cols
        
        total_cells = working_df.size
        empty_cells = int(working_df.isnull().sum().sum())
        empty_pct = (empty_cells / total_cells * 100) if total_cells > 0 else 0
        dup_count = int(working_df.duplicated().sum())
        dup_pct = (dup_count / len(working_df) * 100) if len(working_df) > 0 else 0
        
        checks_passed = 2
        if empty_pct <= QA_THRESHOLDS["empty_cells_max_pct"]:
            checks_passed += 1
            self.warnings.append(f"✅ Missing Data: {empty_pct:.1f}% (Healthy)")
        else:
            self.warnings.append(f"⚠️ Missing Data: {empty_pct:.1f}% (High Nulls)")
            
        if dup_pct <= QA_THRESHOLDS["duplicates_max_pct"]:
            checks_passed += 1
            self.warnings.append(f"✅ Duplicates: {dup_pct:.1f}% ({dup_count} rows)")
        else:
            self.warnings.append(f"⚠️ Duplicates: {dup_pct:.1f}% ({dup_count} rows)")
            
        self.warnings.append(f"✅ Metrics Identified: {len(numeric_cols)} numeric fields")
        self.warnings.append(f"✅ Dimensions Found: {len(category_cols)} categorical fields")
        
        quality_score = round((checks_passed / 4) * 100, 1)
        
        self.qa_report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rows": len(working_df),
            "columns": len(working_df.columns),
            "quality_score": quality_score,
            "empty_cells_pct": round(empty_pct, 2),
            "duplicates": dup_count,
            "numeric_cols_count": len(numeric_cols),
            "date_cols_count": len(date_cols),
            "category_cols_count": len(category_cols)
        }
        
        return {
            "cleaned_df": working_df,
            "report": self.qa_report,
            "warnings": self.warnings,
            "errors": self.errors,
            "numeric_cols": numeric_cols,
            "date_cols": date_cols,
            "category_cols": category_cols,
            "conversion_log": self.conversion_log
        }
