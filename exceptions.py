"""Custom exceptions so callers can handle failures gracefully."""


class AnalyzerError(Exception):
    """Base class for all application errors."""


class InvalidInputError(AnalyzerError):
    """The job description is empty or not usable."""


class ConfigurationError(AnalyzerError):
    """Missing API key, unsupported provider, or missing dependency."""


class AnalysisError(AnalyzerError):
    """A workflow node failed to produce a result."""
