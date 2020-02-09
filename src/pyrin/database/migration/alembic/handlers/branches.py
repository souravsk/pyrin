# -*- coding: utf-8 -*-
"""
database migration alembic handlers branches module.
"""

from pyrin.database.migration.alembic.decorators import alembic_cli_handler
from pyrin.database.migration.alembic.handlers.base import AlembicReportingCLIHandlerBase


@alembic_cli_handler()
class BranchesCLIHandler(AlembicReportingCLIHandlerBase):
    """
    branches cli handler class.
    """

    def __init__(self):
        """
        initializes an instance of BranchesCLIHandler.
        """

        super().__init__('branches')
