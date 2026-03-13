"""Indonesian language adaptation module for LightRAG.

Provides preprocessing utilities (acronym resolution, text normalization)
activated via the USE_INDONESIAN_PREPROCESSING flag in addon_params.
"""

from lightrag.indonesian.preprocessor import preprocess_indonesian_text
from lightrag.indonesian.acronyms import INDONESIAN_ACRONYMS

__all__ = ["preprocess_indonesian_text", "INDONESIAN_ACRONYMS"]
