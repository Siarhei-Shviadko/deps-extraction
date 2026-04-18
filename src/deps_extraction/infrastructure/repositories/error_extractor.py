import logging

from sqlalchemy.exc import StatementError

from deps_extraction.extras.datasource import Database, DBDriver

from .constants import DatabaseErrorTypeEnum, PostgresErrorCodeEnum

logger = logging.getLogger(__name__)

__all__ = ["extract_database_error_type", "convert_pgcode_to_error_type"]


def extract_database_error_type(err: StatementError, database: Database) -> DatabaseErrorTypeEnum:
    if database.driver == DBDriver.PSYCOPG2:
        return convert_pgcode_to_error_type(err.orig.pgcode)
    if database.driver == DBDriver.PG8000:
        return convert_pgcode_to_error_type(err.orig.args[0]["C"])

    msg = f"Unsupported database driver '{database.driver}' during extracting error type"
    logger.error(msg)
    raise


def convert_pgcode_to_error_type(code: str) -> DatabaseErrorTypeEnum:
    code2error_type = {
        PostgresErrorCodeEnum.UNIQUE_VIOLATION.value: DatabaseErrorTypeEnum.UNIQUE_VIOLATION,
        PostgresErrorCodeEnum.FOREIGN_KEY_VIOLATION.value: DatabaseErrorTypeEnum.FOREIGN_KEY_VIOLATION,
    }

    if code not in code2error_type:
        raise

    return code2error_type[code]
