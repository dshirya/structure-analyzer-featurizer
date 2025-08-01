#!/usr/bin/env python
##############################################################################
#
# (c) 2025 Sangjoon Lee.
# All rights reserved.
#
# File coded by: Sangjoon Lee, Anton Oliynyk, Emil Jaffal, Danila Shiryaev.
#
# See GitHub contributions for a more detailed list of contributors.
# https://github.com/bobleesj/structure-analyzer-featurizer/graphs/contributors  # noqa: E501
#
# See LICENSE.rst for license information.
#
##############################################################################
"""Definition of __version__."""

#  We do not use the other three variables, but can be added back if needed.
#  __all__ = ["__date__", "__git_commit__", "__timestamp__", "__version__"]

# obtain version information
from importlib.metadata import version

__version__ = version("structure_analyzer_featurizer")

# End of file
