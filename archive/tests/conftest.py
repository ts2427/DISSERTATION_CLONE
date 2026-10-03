"""
Pytest Configuration and Shared Fixtures

Provides common fixtures for unit and integration tests.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from validation.nlp_validation import BreachClassifier


@pytest.fixture(scope="session")
def classifier():
    """Provide a BreachClassifier instance for all tests."""
    return BreachClassifier()


@pytest.fixture
def sample_breach_row():
    """Provide a sample breach row for testing."""
    return pd.Series({
        'org_name': 'TechCorp Inc',
        'breach_date': '2023-01-15',
        'incident_details': 'Ransomware attack encrypted customer databases. Attackers demanded 5 million in bitcoin.',
        'information_affected': 'Customer PII including SSN and credit card numbers',
        'total_affected': 50000.0,
        'breach_type': 'ransomware',
        'disclosed_date': '2023-01-20'
    })


@pytest.fixture
def sample_health_breach_row():
    """Provide a sample health breach row for testing."""
    return pd.Series({
        'org_name': 'MediCare Hospital',
        'breach_date': '2022-06-10',
        'incident_details': 'HIPAA violation: Protected health information exposed due to unsecured database.',
        'information_affected': 'Patient medical records and diagnosis information',
        'total_affected': 25000.0,
        'breach_type': 'health',
        'organization_type': 'Healthcare'
    })


@pytest.fixture
def sample_financial_breach_row():
    """Provide a sample financial breach row for testing."""
    return pd.Series({
        'org_name': 'FinanceBank Corp',
        'breach_date': '2023-03-01',
        'incident_details': 'Credit card fraud scheme. Payment card information stolen.',
        'information_affected': 'Debit and credit card numbers with CVV',
        'total_affected': 100000.0,
        'breach_type': 'financial'
    })


@pytest.fixture
def sample_dataframe():
    """Provide a sample breach dataframe for testing."""
    return pd.DataFrame({
        'org_name': ['TechCorp', 'MediCare', 'FinanceBank', 'RetailCo', 'DataCorp'],
        'breach_date': ['2023-01-15', '2022-06-10', '2023-03-01', '2023-05-20', '2023-02-14'],
        'incident_details': [
            'Ransomware attack with encryption and ransom demand',
            'HIPAA violation with patient medical records exposed',
            'Credit card fraud and payment card theft',
            'Phishing attack compromised executive email accounts',
            'Nation-state advanced persistent threat targeting R&D'
        ],
        'information_affected': [
            'Customer PII and SSN',
            'Patient health information',
            'Bank account and routing numbers',
            'Business email and internal communications',
            'Proprietary source code and trade secrets'
        ],
        'total_affected': [50000.0, 25000.0, 100000.0, 5000.0, 150000.0],
        'breach_type': ['ransomware', 'health', 'financial', 'phishing', 'nation_state']
    })


@pytest.fixture
def empty_dataframe():
    """Provide an empty dataframe for edge case testing."""
    return pd.DataFrame({
        'org_name': [],
        'incident_details': [],
        'information_affected': [],
        'total_affected': [],
        'breach_type': []
    })


@pytest.fixture
def null_values_dataframe():
    """Provide a dataframe with null/NaN values for testing."""
    return pd.DataFrame({
        'org_name': ['TechCorp', None, 'FinanceBank'],
        'incident_details': ['Some incident', np.nan, 'Another incident'],
        'information_affected': [None, 'Some data', None],
        'total_affected': [50000.0, np.nan, 100000.0],
        'breach_type': ['ransomware', 'unknown', 'financial']
    })


@pytest.fixture
def classifier_with_custom_keywords():
    """Provide a classifier with custom keywords for testing."""
    classifier = BreachClassifier()
    # Modify keywords for testing
    classifier.breach_keywords['pii_breach'] = ['test_keyword', 'pii']
    return classifier


@pytest.fixture
def sample_metrics_dict():
    """Provide a sample metrics dictionary like validation script outputs."""
    return {
        'overall': {
            'weighted_precision': 0.875,
            'weighted_recall': 0.82,
            'weighted_f1': 0.847,
            'accuracy': 0.85,
            'n_total_samples': 150,
            'validation_date': '2026-01-22T10:30:00'
        },
        'per_category': {
            'pii_breach': {
                'precision': 0.90,
                'recall': 0.85,
                'f1_score': 0.875,
                'n_samples': 150,
                'n_positive_true': 45,
                'n_positive_pred': 47
            },
            'health_breach': {
                'precision': 0.95,
                'recall': 0.92,
                'f1_score': 0.935,
                'n_samples': 150,
                'n_positive_true': 38,
                'n_positive_pred': 40
            }
        }
    }


@pytest.fixture
def output_dir(tmp_path):
    """Provide a temporary directory for test outputs."""
    return tmp_path / "test_outputs"


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: Mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: Mark test as slow"
    )
    config.addinivalue_line(
        "markers", "validation: Mark test as validation test"
    )
