"""
Machine Learning Models Module

Provides reusable ML classes for breach impact prediction validation.
Used by scripts 60 and 61 for model training and evaluation.
"""

from .breach_impact_model import BreachImpactModel
from .model_evaluation import ModelEvaluator
from .feature_importance import FeatureImportanceAnalyzer

__all__ = ['BreachImpactModel', 'ModelEvaluator', 'FeatureImportanceAnalyzer']
