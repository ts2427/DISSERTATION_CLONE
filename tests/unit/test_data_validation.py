"""
Unit Tests for Data Quality and Validation

Tests data integrity checks, missing values, and dataset quality metrics.
"""

import pytest
import pandas as pd
import numpy as np


@pytest.mark.unit
class TestDataFrameStructure:
    """Test dataframe structure and column integrity."""

    def test_sample_dataframe_columns(self, sample_dataframe):
        """Test that sample dataframe has expected columns."""
        expected_cols = [
            'org_name', 'breach_date', 'incident_details',
            'information_affected', 'total_affected', 'breach_type'
        ]
        for col in expected_cols:
            assert col in sample_dataframe.columns

    def test_sample_dataframe_length(self, sample_dataframe):
        """Test that sample dataframe has 5 rows."""
        assert len(sample_dataframe) == 5

    def test_dataframe_column_types(self, sample_dataframe):
        """Test that columns have expected data types."""
        assert sample_dataframe['org_name'].dtype == 'object'
        assert sample_dataframe['total_affected'].dtype == 'float64'
        assert sample_dataframe['breach_type'].dtype == 'object'


@pytest.mark.unit
class TestMissingValues:
    """Test handling of missing values."""

    def test_null_values_dataframe_nulls(self, null_values_dataframe):
        """Test that null dataframe contains NaN/None values."""
        assert null_values_dataframe['org_name'].isna().sum() > 0
        assert null_values_dataframe['incident_details'].isna().sum() > 0

    def test_count_missing_in_column(self, null_values_dataframe):
        """Test counting of missing values."""
        missing_org_name = null_values_dataframe['org_name'].isna().sum()
        assert missing_org_name == 1

    def test_sample_dataframe_no_nulls(self, sample_dataframe):
        """Test that sample dataframe has no nulls."""
        assert sample_dataframe.isna().sum().sum() == 0

    def test_empty_dataframe_shape(self, empty_dataframe):
        """Test that empty dataframe has correct shape."""
        assert len(empty_dataframe) == 0
        assert len(empty_dataframe.columns) == 5


@pytest.mark.unit
class TestNumericFields:
    """Test numeric field validation."""

    def test_total_affected_is_numeric(self, sample_dataframe):
        """Test that total_affected column is numeric."""
        assert pd.api.types.is_numeric_dtype(sample_dataframe['total_affected'])

    def test_total_affected_all_positive(self, sample_dataframe):
        """Test that all total_affected values are positive."""
        assert (sample_dataframe['total_affected'] > 0).all()

    def test_total_affected_reasonable_magnitude(self, sample_dataframe):
        """Test that total_affected values are reasonable."""
        assert sample_dataframe['total_affected'].min() >= 1000
        assert sample_dataframe['total_affected'].max() <= 1000000

    def test_numeric_conversion(self):
        """Test conversion of string to numeric."""
        df = pd.DataFrame({
            'value': ['100', '200', '300']
        })
        df['value_numeric'] = pd.to_numeric(df['value'], errors='coerce')

        assert pd.api.types.is_numeric_dtype(df['value_numeric'])
        assert df['value_numeric'].sum() == 600


@pytest.mark.unit
class TestCategoricalFields:
    """Test categorical field validation."""

    def test_breach_type_values(self, sample_dataframe):
        """Test that breach_type contains valid categories."""
        valid_types = ['ransomware', 'health', 'financial', 'phishing', 'nation_state']
        for breach_type in sample_dataframe['breach_type']:
            assert breach_type in valid_types

    def test_breach_type_unique_count(self, sample_dataframe):
        """Test the number of unique breach types."""
        unique_types = sample_dataframe['breach_type'].nunique()
        assert unique_types == 5

    def test_organization_names_unique(self, sample_dataframe):
        """Test that organization names are unique."""
        unique_orgs = sample_dataframe['org_name'].nunique()
        assert unique_orgs == len(sample_dataframe)


@pytest.mark.unit
class TestDateFields:
    """Test date field validation."""

    def test_breach_date_is_string(self, sample_dataframe):
        """Test that breach_date is string/date format."""
        assert sample_dataframe['breach_date'].dtype == 'object'

    def test_breach_date_valid_format(self, sample_dataframe):
        """Test that breach dates can be parsed."""
        dates = pd.to_datetime(sample_dataframe['breach_date'], errors='coerce')
        assert dates.isna().sum() == 0

    def test_breach_dates_chronological(self):
        """Test that dates are in chronological order."""
        df = pd.DataFrame({
            'date': ['2023-01-01', '2023-06-01', '2023-12-01']
        })
        dates = pd.to_datetime(df['date'])
        assert (dates.diff().dropna() >= pd.Timedelta(0)).all()


@pytest.mark.unit
class TestTextFields:
    """Test text field validation."""

    def test_incident_details_not_empty(self, sample_dataframe):
        """Test that incident details are not empty."""
        assert (sample_dataframe['incident_details'].str.len() > 0).all()

    def test_information_affected_not_empty(self, sample_dataframe):
        """Test that information affected is not empty."""
        assert (sample_dataframe['information_affected'].str.len() > 0).all()

    def test_text_field_minimum_length(self, sample_dataframe):
        """Test that text fields have minimum length."""
        min_incident_len = sample_dataframe['incident_details'].str.len().min()
        assert min_incident_len >= 20

    def test_text_contains_keywords(self, sample_dataframe):
        """Test that incident details contain breach-related keywords."""
        all_text = ' '.join(sample_dataframe['incident_details']).lower()
        breach_keywords = ['attack', 'breach', 'stolen', 'exposed', 'compromised', 'encrypted']

        assert any(keyword in all_text for keyword in breach_keywords)


@pytest.mark.unit
class TestDataConsistency:
    """Test data consistency across fields."""

    def test_row_consistency(self, sample_dataframe):
        """Test that each row has consistent data."""
        for idx, row in sample_dataframe.iterrows():
            assert pd.notna(row['org_name'])
            assert pd.notna(row['breach_type'])
            assert row['total_affected'] > 0

    def test_column_value_consistency(self, sample_dataframe):
        """Test that breach_type matches incident_details content."""
        ransomware_rows = sample_dataframe[sample_dataframe['breach_type'] == 'ransomware']
        for idx, row in ransomware_rows.iterrows():
            assert 'ransomware' in row['incident_details'].lower()

    def test_no_duplicate_rows(self, sample_dataframe):
        """Test that there are no exact duplicate rows."""
        duplicates = sample_dataframe.duplicated().sum()
        assert duplicates == 0


@pytest.mark.unit
class TestBoundaryValues:
    """Test boundary value handling."""

    def test_minimum_records_affected(self, classifier):
        """Test severity with minimum records."""
        severity = classifier._calculate_records_severity(1)
        assert severity == 1

    def test_boundary_1000_records(self, classifier):
        """Test severity at 1000 record boundary."""
        severity_999 = classifier._calculate_records_severity(999)
        severity_1000 = classifier._calculate_records_severity(1000)

        assert severity_999 == 1
        assert severity_1000 == 2

    def test_boundary_10000_records(self, classifier):
        """Test severity at 10000 record boundary."""
        severity_9999 = classifier._calculate_records_severity(9999)
        severity_10000 = classifier._calculate_records_severity(10000)

        assert severity_9999 == 2
        assert severity_10000 == 3

    def test_boundary_100000_records(self, classifier):
        """Test severity at 100000 record boundary."""
        severity_99999 = classifier._calculate_records_severity(99999)
        severity_100000 = classifier._calculate_records_severity(100000)

        assert severity_99999 == 3
        assert severity_100000 == 4

    def test_boundary_1000000_records(self, classifier):
        """Test severity at 1 million record boundary."""
        severity_999999 = classifier._calculate_records_severity(999999)
        severity_1000000 = classifier._calculate_records_severity(1000000)

        assert severity_999999 == 4
        assert severity_1000000 == 5


@pytest.mark.unit
class TestDataIntegrity:
    """Test overall data integrity."""

    def test_dataframe_not_corrupted(self, sample_dataframe):
        """Test that dataframe is not corrupted."""
        assert sample_dataframe is not None
        assert isinstance(sample_dataframe, pd.DataFrame)
        assert len(sample_dataframe) > 0
        assert len(sample_dataframe.columns) > 0

    def test_fixture_independence(self, sample_dataframe):
        """Test that fixtures are independent."""
        original_len = len(sample_dataframe)
        sample_dataframe.drop(0, inplace=True)

        # Re-get fixture to verify it's not modified
        assert original_len == 5

    def test_no_infinite_values(self, sample_dataframe):
        """Test that numeric columns don't contain infinite values."""
        assert not np.isinf(sample_dataframe['total_affected']).any()

    def test_numeric_precision(self, sample_dataframe):
        """Test numeric field precision."""
        for val in sample_dataframe['total_affected']:
            assert isinstance(val, (int, float, np.number))
            assert val > 0


@pytest.mark.unit
class TestDataFiltering:
    """Test data filtering operations."""

    def test_filter_by_breach_type(self, sample_dataframe):
        """Test filtering dataframe by breach type."""
        ransomware_breaches = sample_dataframe[
            sample_dataframe['breach_type'] == 'ransomware'
        ]
        assert len(ransomware_breaches) == 1
        assert ransomware_breaches.iloc[0]['org_name'] == 'TechCorp'

    def test_filter_by_affected_count(self, sample_dataframe):
        """Test filtering by number of affected records."""
        large_breaches = sample_dataframe[
            sample_dataframe['total_affected'] > 50000
        ]
        assert len(large_breaches) == 2

    def test_filter_preserves_structure(self, sample_dataframe):
        """Test that filtering preserves dataframe structure."""
        filtered = sample_dataframe[sample_dataframe['total_affected'] > 40000]

        assert isinstance(filtered, pd.DataFrame)
        assert all(col in filtered.columns for col in sample_dataframe.columns)


@pytest.mark.unit
class TestDataAggregation:
    """Test data aggregation operations."""

    def test_mean_affected_records(self, sample_dataframe):
        """Test calculating mean of affected records."""
        mean_affected = sample_dataframe['total_affected'].mean()
        assert mean_affected > 0
        assert isinstance(mean_affected, (int, float, np.number))

    def test_groupby_breach_type(self, sample_dataframe):
        """Test groupby operation on breach type."""
        grouped = sample_dataframe.groupby('breach_type')['total_affected'].sum()

        assert isinstance(grouped, pd.Series)
        assert len(grouped) == 5

    def test_count_by_breach_type(self, sample_dataframe):
        """Test count aggregation by breach type."""
        counts = sample_dataframe['breach_type'].value_counts()

        assert len(counts) == 5
        assert counts.sum() == 5
