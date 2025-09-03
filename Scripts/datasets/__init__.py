"""
Systematic literature review dataset processors.

This module contains individual dataset processors for 15+ systematic reviews
covering over 32,000 articles across multiple research domains.
"""

# Main dataset processors (15 systematic reviews)
from .ArchiML import ArchiML
from .Behave import Behave  
from .CodeClone import CodeClone
from .CodeCompr import CodeCompr
from .DTCPS import DTCPS
from .ESM_2 import ESM_2
from .ESPLE import ESPLE
from .GameSE import GameSE
from .ModelGuidance import ModelGuidance
from .ModelingAssist import ModelingAssist
from .OODP import OODP
from .SecSelfAdapt import SecSelfAdapt
from .SmellReprod import SmellReprod
from .TestNN import TestNN
from .TrustSE import TrustSE

__all__ = [
    "ArchiML", "Behave", "CodeClone", "CodeCompr", "DTCPS", "ESM_2", 
    "ESPLE", "GameSE", "ModelGuidance", "ModelingAssist", "OODP", 
    "SecSelfAdapt", "SmellReprod", "TestNN", "TrustSE"
]
