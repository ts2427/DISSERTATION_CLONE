"""
NLP Breach Severity Classifier
==============================

This module encapsulates the breach severity classification logic.
Can be used by script 45, validation scripts, and unit tests.

Author: Timothy Spivey
Date: January 2026
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class BreachClassifier:
    """Classify data breaches by severity and type using keyword matching."""

    # Keywords for each breach category
    BREACH_KEYWORDS = {
        'pii_breach': [
            'social security', 'ssn', 'credit card', 'personal information',
            'personally identifiable', 'pii', 'driver license', 'passport',
            'national id', 'identity', 'names and addresses', 'date of birth',
            'financial information', 'bank account', 'customer data', 'personal data'
        ],
        'health_breach': [
            'hipaa', 'medical record', 'health information', 'phi',
            'protected health', 'patient data', 'medical history',
            'diagnosis', 'prescription', 'healthcare', 'health data',
            'medical data', 'patient information'
        ],
        'financial_breach': [
            'payment card', 'credit card', 'debit card', 'bank account',
            'financial data', 'transaction', 'payment information',
            'account number', 'routing number', 'wire transfer', 'banking'
        ],
        'ip_breach': [
            'intellectual property', 'trade secret', 'source code',
            'proprietary', 'patent', 'confidential business', 'corporate data',
            'r&d', 'research data', 'business intelligence'
        ],
        'ransomware': [
            'ransomware', 'encryption', 'ransom', 'locked', 'decrypt',
            'encrypted files', 'ransom payment', 'crypto', 'extortion'
        ],
        'nation_state': [
            'nation-state', 'apt', 'advanced persistent', 'state-sponsored',
            'chinese hackers', 'russian hackers', 'north korea', 'iran',
            'government-backed', 'espionage', 'state actor'
        ],
        'insider_threat': [
            'insider', 'employee', 'contractor', 'unauthorized access',
            'internal', 'staff member', 'privileged access', 'former employee'
        ],
        'ddos_attack': [
            'ddos', 'denial of service', 'distributed denial',
            'service disruption', 'network flood', 'dos attack'
        ],
        'phishing': [
            'phishing', 'spear phishing', 'email compromise',
            'business email compromise', 'bec', 'social engineering'
        ],
        'malware': [
            'malware', 'virus', 'trojan', 'worm', 'backdoor',
            'keylogger', 'spyware', 'botnet'
        ]
    }

    # Sensitivity weights for severity scoring
    SENSITIVITY_WEIGHTS = {
        'pii_breach': 3,
        'health_breach': 4,  # HIPAA violations are most severe
        'financial_breach': 3,
        'ip_breach': 2,
        'ransomware': 3,
        'nation_state': 3,
        'insider_threat': 2,
        'ddos_attack': 1,
        'phishing': 2,
        'malware': 2
    }

    def __init__(self):
        """Initialize classifier with keywords and weights."""
        self.breach_keywords = self.BREACH_KEYWORDS.copy()
        self.sensitivity_weights = self.SENSITIVITY_WEIGHTS.copy()

    def classify_breach_text(self, text: any) -> Dict[str, int]:
        """
        Classify breach based on text description.

        Args:
            text: Text description (can be None/NaN)

        Returns:
            Dict with key for each breach type (0=not present, 1=present)
        """
        # Handle null values
        if pd.isna(text):
            return {key: 0 for key in self.breach_keywords.keys()}

        text_lower = str(text).lower()
        classifications = {}

        # Check if any keyword appears in text
        for breach_type, keywords in self.breach_keywords.items():
            found = any(keyword in text_lower for keyword in keywords)
            classifications[breach_type] = 1 if found else 0

        return classifications

    def _calculate_records_severity(self, records_affected: float) -> int:
        """
        Calculate severity score based on number of records affected.

        Args:
            records_affected: Number of records (converts to float, handles NaN)

        Returns:
            Severity score 0-5 based on scale
        """
        # Convert to numeric
        try:
            records_affected = pd.to_numeric(records_affected, errors='coerce')
            if pd.isna(records_affected):
                records_affected = 0
            else:
                records_affected = float(records_affected)
        except:
            records_affected = 0

        # Log scale severity based on records
        if records_affected <= 0:
            return 0
        elif records_affected < 1000:
            return 1
        elif records_affected < 10000:
            return 2
        elif records_affected < 100000:
            return 3
        elif records_affected < 1000000:
            return 4
        else:
            return 5

    def classify_breach(self, row: pd.Series,
                       text_columns: List[str] = None) -> Dict:
        """
        Classify single breach row.

        Args:
            row: Pandas Series with breach data
            text_columns: List of text column names to use (auto-detected if None)

        Returns:
            Dict with all classification and severity scores
        """
        # Auto-detect text columns if not provided
        if text_columns is None:
            possible_text_cols = ['breach_details', 'Description', 'incident_details',
                                'information_affected', 'Details']
            text_columns = [col for col in possible_text_cols if col in row.index]

        # Combine text from all available columns
        text_parts = []

        for col in text_columns:
            if col in row.index and pd.notna(row.get(col)):
                text_parts.append(str(row[col]))

        # Add other potentially useful fields
        if pd.notna(row.get('org_name')):
            text_parts.append(str(row['org_name']))
        if pd.notna(row.get('organization_type')):
            text_parts.append(str(row['organization_type']))
        if pd.notna(row.get('TYPE')):
            text_parts.append(str(row['TYPE']))

        # Combine all text
        text = ' '.join(text_parts)

        # Classify text
        classifications = self.classify_breach_text(text)

        # Calculate severity score from keywords
        severity_score = sum(
            classifications[breach_type] * self.sensitivity_weights[breach_type]
            for breach_type in self.breach_keywords.keys()
        )

        # Calculate severity based on records affected
        records_affected = row.get('total_affected', 0)
        records_severity = self._calculate_records_severity(records_affected)

        # Combined severity
        combined_severity = severity_score + records_severity

        # High severity flag (top quartile, score >= 7)
        high_severity = 1 if combined_severity >= 7 else 0

        # Multiple breach types indicates complexity
        num_breach_types = sum(classifications.values())
        complex_breach = 1 if num_breach_types >= 2 else 0

        # Return full result
        result = {
            **classifications,  # All breach type flags
            'severity_score': severity_score,
            'records_severity': records_severity,
            'records_affected_numeric': float(records_affected) if records_affected else 0.0,
            'combined_severity_score': combined_severity,
            'high_severity_breach': high_severity,
            'num_breach_types': num_breach_types,
            'complex_breach': complex_breach
        }

        return result

    def classify_dataframe(self, df: pd.DataFrame,
                          text_columns: List[str] = None) -> pd.DataFrame:
        """
        Classify all breaches in DataFrame.

        Args:
            df: DataFrame with breach data
            text_columns: List of text column names to use (auto-detected if None)

        Returns:
            DataFrame with classifications for each breach
        """
        results = []

        for idx, row in df.iterrows():
            result = self.classify_breach(row, text_columns)
            result['breach_id'] = idx
            results.append(result)

        return pd.DataFrame(results)

    @staticmethod
    def validate_keywords(keywords_dict: Dict[str, List[str]]) -> bool:
        """
        Validate keyword dictionary structure.

        Args:
            keywords_dict: Dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(keywords_dict, dict):
            return False

        for key, values in keywords_dict.items():
            if not isinstance(key, str):
                return False
            if not isinstance(values, list):
                return False
            if not all(isinstance(v, str) for v in values):
                return False

        return True


# Export for convenience
__all__ = ['BreachClassifier']
