"""
Engine package initialization.
"""

import importlib
import sys


def _ensure_numpy_pickle_compatibility():
    """Provide a compatibility alias for joblib pickles created with NumPy 2.x.

    Some serialized models reference ``numpy._core`` modules, while older
    environments only expose ``numpy.core``. Registering aliases allows the
    existing model artifacts to load without retraining.
    """

    try:
        import numpy as np
        import numpy.core as numpy_core
    except Exception:
        return

    sys.modules.setdefault("numpy._core", numpy_core)
    if not hasattr(np, "_core"):
        setattr(np, "_core", numpy_core)

    common_submodules = [
        "multiarray",
        "numeric",
        "umath",
        "_multiarray_umath",
        "overrides",
        "fromnumeric",
        "shape_base",
        "arrayprint",
        "defchararray",
        "einsumfunc",
        "function_base",
        "getlimits",
        "numerictypes",
        "records",
        "memmap",
        "scalarmath",
        "_exceptions",
    ]

    for name in common_submodules:
        try:
            module = importlib.import_module(f"numpy.core.{name}")
        except Exception:
            continue
        sys.modules.setdefault(f"numpy._core.{name}", module)


_ensure_numpy_pickle_compatibility()

from .inference_engine import InferenceEngine
from .hybrid_module import HybridModule, DiagnosticResult
from .preprocessor import Preprocessor
from .rf_classifier import RFClassifier

__all__ = [
    'InferenceEngine',
    'HybridModule',
    'DiagnosticResult',
    'Preprocessor',
    'RFClassifier',
]