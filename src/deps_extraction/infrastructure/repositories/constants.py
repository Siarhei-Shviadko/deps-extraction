from enum import Enum, auto


class DatabaseErrorTypeEnum(Enum):
    UNIQUE_VIOLATION = auto()
    FOREIGN_KEY_VIOLATION = auto()


# according https://www.postgresql.org/docs/current/errcodes-appendix.html
class PostgresErrorCodeEnum(Enum):
    UNIQUE_VIOLATION = "23505"
    FOREIGN_KEY_VIOLATION = "23503"
