"""
Unit Tests for NLP Breach Classifier

Tests the BreachClassifier class methods in isolation.
"""

import pytest
import pandas as pd
import numpy as np
from validation.nlp_validation import BreachClassifier


@pytest.mark.unit
class TestBreachClassifierInit:
    """Test classifier initialization."""

    def test_classifier_init(self, classifier):
        """Test that classifier initializes correctly."""
        assert classifier is not None
        assert hasattr(classifier, 'breach_keywords')
        assert hasattr(classifier, 'sensitivity_weights')

    def test_keywords_dict_structure(self, classifier):
        """Test that keywords dictionary has correct structure."""
        assert isinstance(classifier.breach_keywords, dict)
        assert len(classifier.breach_keywords) == 10
        assert all(isinstance(k, str) for k in classifier.breach_keywords.keys())
        assert all(isinstance(v, list) for v in classifier.breach_keywords.values())

    def test_sensitivity_weights_structure(self, classifier):
        """Test that sensitivity weights have correct structure."""
        assert isinstance(classifier.sensitivity_weights, dict)
        assert len(classifier.sensitivity_weights) == 10
        assert all(isinstance(v, int) for v in classifier.sensitivity_weights.values())

    def test_all_breach_types_present(self, classifier):
        """Test that all breach types are properly initialized."""
        expected_types = [
            'pii_breach', 'health_breach', 'financial_breach', 'ip_breach',
            'ransomware', 'nation_state', 'insider_threat', 'ddos_attack',
            'phishing', 'malware'
        ]
        for breach_type in expected_types:
            assert breach_type in classifier.breach_keywords
            assert breach_type in classifier.sensitivity_weights
            assert len(classifier.breach_keywords[breach_type]) > 0


@pytest.mark.unit
class TestClassifyBreachText:
    """Test text classification method."""

    def test_classify_simple_pii_breach(self, classifier):
        """Test classification of simple PII breach text."""
        text = "Hackers stole customer social security numbers"
        result = classifier.classify_breach_text(text)

        assert isinstance(result, dict)
        assert result['pii_breach'] == 1
        assert result['health_breach'] == 0

    def test_classify_health_breach(self, classifier):
        """Test classification of health/medical breach."""
        text = "HIPAA violation: Protected health information exposed"
        result = classifier.classify_breach_text(text)

        assert result['health_breach'] == 1

    def test_classify_financial_breach(self, classifier):
        """Test classification of financial breach."""
        text = "Credit card payment data was stolen in the breach"
        result = classifier.classify_breach_text(text)

        assert result['financial_breach'] == 1

    def test_classify_ransomware(self, classifier):
        """Test classification of ransomware attack."""
        text = "Ransomware encrypted all files. Attackers demand bitcoin ransom."
        result = classifier.classify_breach_text(text)

        assert result['ransomware'] == 1

    def test_classify_nation_state(self, classifier):
        """Test classification of nation-state attack."""
        text = "Advanced persistent threat from state-sponsored actors"
        result = classifier.classify_breach_text(text)

        assert result['nation_state'] == 1

    def test_classify_insider_threat(self, classifier):
        """Test classification of insider threat."""
        text = "Disgruntled employee stole confidential data"
        result = classifier.classify_breach_text(text)

        assert result['insider_threat'] == 1

    def test_classify_ddos_attack(self, classifier):
        """Test classification of DDoS attack."""
        text = "Service disruption caused by distributed denial of service attack"
        result = classifier.classify_breach_text(text)

        assert result['ddos_attack'] == 1

    def test_classify_phishing(self, classifier):
        """Test classification of phishing attack."""
        text = "Spear phishing email compromised executive accounts"
        result = classifier.classify_breach_text(text)

        assert result['phishing'] == 1

    def test_classify_malware(self, classifier):
        """Test classification of malware."""
        text = "Trojan malware infected customer machines"
        result = classifier.classify_breach_text(text)

        assert result['malware'] == 1

    def test_classify_no_breach(self, classifier):
        """Test that non-breach text returns all zeros."""
        text = "This is a normal incident report about weather"
        result = classifier.classify_breach_text(text)

        assert all(v == 0 for v in result.values())

    def test_classify_multiple_breach_types(self, classifier):
        """Test classification with multiple breach types."""
        text = "Ransomware attack stole customer PII and credit cards"
        result = classifier.classify_breach_text(text)

        assert result['ransomware'] == 1
        assert result['pii_breach'] == 1
        assert result['financial_breach'] == 1

    def test_classify_case_insensitive(self, classifier):
        """Test that classification is case-insensitive."""
        text_lower = "ransomware attack"
        text_upper = "RANSOMWARE ATTACK"
        text_mixed = "RaNsOmWaRe AtTaCk"

        result_lower = classifier.classify_breach_text(text_lower)
        result_upper = classifier.classify_breach_text(text_upper)
        result_mixed = classifier.classify_breach_text(text_mixed)

        assert result_lower['ransomware'] == 1
        assert result_upper['ransomware'] == 1
        assert result_mixed['ransomware'] == 1

    def test_classify_null_text(self, classifier):
        """Test classification with None/NaN values."""
        result_none = classifier.classify_breach_text(None)
        result_nan = classifier.classify_breach_text(np.nan)

        assert all(v == 0 for v in result_none.values())
        assert all(v == 0 for v in result_nan.values())

    def test_classify_empty_string(self, classifier):
        """Test classification with empty string."""
        result = classifier.classify_breach_text("")
        assert all(v == 0 for v in result.values())


@pytest.mark.unit
class TestCalculateRecordsSeverity:
    """Test records severity calculation."""

    def test_no_records_affected(self, classifier):
        """Test severity with zero records."""
        severity = classifier._calculate_records_severity(0)
        assert severity == 0

    def test_small_breach_under_1000(self, classifier):
        """Test severity for breach under 1000 records."""
        severity = classifier._calculate_records_severity(500)
        assert severity == 1

    def test_medium_breach_1000_to_10000(self, classifier):
        """Test severity for breach 1000-10000 records."""
        severity = classifier._calculate_records_severity(5000)
        assert severity == 2

    def test_large_breach_10000_to_100000(self, classifier):
        """Test severity for breach 10000-100000 records."""
        severity = classifier._calculate_records_severity(50000)
        assert severity == 3

    def test_very_large_breach_100000_to_1000000(self, classifier):
        """Test severity for breach 100000-1000000 records."""
        severity = classifier._calculate_records_severity(500000)
        assert severity == 4

    def test_massive_breach_over_1000000(self, classifier):
        """Test severity for breach over 1 million records."""
        severity = classifier._calculate_records_severity(2000000)
        assert severity == 5

    def test_null_records(self, classifier):
        """Test severity with null/NaN records."""
        severity_nan = classifier._calculate_records_severity(np.nan)
        severity_none = classifier._calculate_records_severity(None)

        assert severity_nan == 0
        assert severity_none == 0

    def test_string_numeric_conversion(self, classifier):
        """Test severity with string numeric input."""
        severity = classifier._calculate_records_severity("50000")
        assert severity == 3

    def test_float_values(self, classifier):
        """Test severity with float values."""
        severity = classifier._calculate_records_severity(50000.5)
        assert severity == 3


@pytest.mark.unit
class TestClassifyBreach:
    """Test single breach classification."""

    def test_classify_full_breach_row(self, sample_breach_row, classifier):
        """Test full classification of a breach row."""
        result = classifier.classify_breach(sample_breach_row)

        assert isinstance(result, dict)
        assert 'pii_breach' in result
        assert 'ransomware' in result
        assert 'severity_score' in result
        assert 'combined_severity_score' in result
        assert 'high_severity_breach' in result

    def test_classify_health_breach_row(self, sample_health_breach_row, classifier):
        """Test classification of health breach row."""
        result = classifier.classify_breach(sample_health_breach_row)

        assert result['health_breach'] == 1
        assert 'severity_score' in result

    def test_classify_financial_breach_row(self, sample_financial_breach_row, classifier):
        """Test classification of financial breach row."""
        result = classifier.classify_breach(sample_financial_breach_row)

        assert result['financial_breach'] == 1
        assert result['pii_breach'] == 1  # SSN mentioned

    def test_severity_score_calculation(self, sample_breach_row, classifier):
        """Test that severity scores are calculated."""
        result = classifier.classify_breach(sample_breach_row)

        assert 'severity_score' in result
        assert isinstance(result['severity_score'], (int, float))
        assert result['severity_score'] >= 0

    def test_combined_severity_score(self, sample_breach_row, classifier):
        """Test combined severity score calculation."""
        result = classifier.classify_breach(sample_breach_row)

        assert 'combined_severity_score' in result
        assert result['combined_severity_score'] >= 0

    def test_high_severity_flag(self, sample_breach_row, classifier):
        """Test high severity flag calculation."""
        result = classifier.classify_breach(sample_breach_row)

        assert 'high_severity_breach' in result
        assert result['high_severity_breach'] in [0, 1]

    def test_complex_breach_flag(self, sample_breach_row, classifier):
        """Test complex breach flag for multiple breach types."""
        result = classifier.classify_breach(sample_breach_row)

        assert 'complex_breach' in result
        assert result['complex_breach'] in [0, 1]

    def test_num_breach_types_count(self, sample_breach_row, classifier):
        """Test counting of breach types."""
        result = classifier.classify_breach(sample_breach_row)

        assert 'num_breach_types' in result
        assert result['num_breach_types'] >= 0

    def test_breach_with_missing_columns(self, classifier):
        """Test classification with missing optional columns."""
        minimal_row = pd.Series({
            'incident_details': 'Ransomware attack'
        })
        result = classifier.classify_breach(minimal_row)

        assert result['ransomware'] == 1
        assert 'severity_score' in result


@pytest.mark.unit
class TestClassifyDataFrame:
    """Test batch dataframe classification."""

    def test_classify_dataframe(self, sample_dataframe, classifier):
        """Test classification of full dataframe."""
        result_df = classifier.classify_dataframe(sample_dataframe)

        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == len(sample_dataframe)
        assert 'breach_id' in result_df.columns
        assert 'pii_breach' in result_df.columns
        assert 'ransomware' in result_df.columns

    def test_classify_empty_dataframe(self, empty_dataframe, classifier):
        """Test classification of empty dataframe."""
        result_df = classifier.classify_dataframe(empty_dataframe)

        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 0

    def test_classify_dataframe_with_nulls(self, null_values_dataframe, classifier):
        """Test classification of dataframe with null values."""
        result_df = classifier.classify_dataframe(null_values_dataframe)

        assert len(result_df) == len(null_values_dataframe)
        assert all(col in result_df.columns for col in ['pii_breach', 'ransomware'])

    def test_classify_dataframe_preserves_length(self, sample_dataframe, classifier):
        """Test that classification preserves dataframe length."""
        result_df = classifier.classify_dataframe(sample_dataframe)

        assert len(result_df) == len(sample_dataframe)

    def test_breach_id_assignment(self, sample_dataframe, classifier):
        """Test that breach IDs are assigned correctly."""
        result_df = classifier.classify_dataframe(sample_dataframe)

        assert 'breach_id' in result_df.columns
        assert list(result_df['breach_id']) == list(range(len(sample_dataframe)))

    def test_all_breach_types_in_result(self, sample_dataframe, classifier):
        """Test that all breach types are present in result."""
        result_df = classifier.classify_dataframe(sample_dataframe)

        expected_cols = [
            'pii_breach', 'health_breach', 'financial_breach', 'ip_breach',
            'ransomware', 'nation_state', 'insider_threat', 'ddos_attack',
            'phishing', 'malware'
        ]
        for col in expected_cols:
            assert col in result_df.columns

    def test_batch_vs_individual_consistency(self, sample_dataframe, classifier):
        """Test that batch classification matches individual classifications."""
        result_df = classifier.classify_dataframe(sample_dataframe)

        for idx, row in sample_dataframe.iterrows():
            individual_result = classifier.classify_breach(row)
            batch_result = result_df.iloc[idx]

            assert batch_result['pii_breach'] == individual_result['pii_breach']
            assert batch_result['ransomware'] == individual_result['ransomware']


@pytest.mark.unit
class TestValidateKeywords:
    """Test keyword validation method."""

    def test_validate_valid_keywords(self, classifier):
        """Test validation of valid keywords dict."""
        valid_dict = {
            'breach_type': ['keyword1', 'keyword2'],
            'another_type': ['keyword3']
        }
        assert BreachClassifier.validate_keywords(valid_dict) is True

    def test_validate_empty_dict(self):
        """Test validation of empty dict."""
        assert BreachClassifier.validate_keywords({}) is True

    def test_validate_invalid_non_dict(self):
        """Test validation fails for non-dict input."""
        assert BreachClassifier.validate_keywords([]) is False
        assert BreachClassifier.validate_keywords("not a dict") is False

    def test_validate_invalid_non_string_key(self):
        """Test validation fails with non-string keys."""
        invalid_dict = {1: ['keyword1'], 'valid': ['keyword2']}
        assert BreachClassifier.validate_keywords(invalid_dict) is False

    def test_validate_invalid_non_list_value(self):
        """Test validation fails with non-list values."""
        invalid_dict = {'key': 'not a list'}
        assert BreachClassifier.validate_keywords(invalid_dict) is False

    def test_validate_invalid_non_string_keywords(self):
        """Test validation fails with non-string keywords."""
        invalid_dict = {'key': ['keyword1', 123, 'keyword2']}
        assert BreachClassifier.validate_keywords(invalid_dict) is False


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_very_long_text(self, classifier):
        """Test classification with very long text."""
        long_text = "ransomware " * 1000
        result = classifier.classify_breach_text(long_text)

        assert result['ransomware'] == 1

    def test_special_characters(self, classifier):
        """Test classification with special characters."""
        text = "Ransomware!!! @#$% attack (encrypted) [data]"
        result = classifier.classify_breach_text(text)

        assert result['ransomware'] == 1

    def test_unicode_characters(self, classifier):
        """Test classification with unicode characters."""
        text = "Ransomware attack with café data (encrypted files)"
        result = classifier.classify_breach_text(text)

        assert result['ransomware'] == 1
        assert result['financial_breach'] == 0

    def test_negative_records_count(self, classifier):
        """Test severity calculation with negative records (invalid)."""
        severity = classifier._calculate_records_severity(-100)
        assert severity == 0

    def test_very_large_records_count(self, classifier):
        """Test severity with extremely large record count."""
        severity = classifier._calculate_records_severity(1e10)
        assert severity == 5
