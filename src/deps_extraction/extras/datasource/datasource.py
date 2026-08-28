import logging
import threading
from contextlib import contextmanager
from typing import Any, Dict, Generator

from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import URL, Connection, Engine

from .constants import DBDialect, DBDriver

__all__ = ["Database", "metadata"]


metadata = MetaData()

DEFAULT_POOL_RECYCLE: int = 1800


class Database:  # noqa: WPS230
    def __init__(
        self,
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
        dialect: DBDialect = DBDialect.POSTGRES,
        driver: DBDriver = DBDriver.PSYCOPG2,
        metaflags: dict = None,
        require_secure_transport: bool = False,
        sslkey: str = "",
        sslcert: str = "",
        sslrootcert: str = "",
        sslmode: str = "verify-full",
    ) -> None:
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.dialect = dialect
        self.driver = driver
        self.drivename = f"{dialect.value}+{driver.value}"
        self.metaflags = metaflags if metaflags is not None else {}
        self.require_secure_transport = require_secure_transport
        self._sslkey = sslkey
        self._sslcert = sslcert
        self._sslmode = sslmode
        self._sslrootcert = sslrootcert

        self.engine: Engine = None
        self.engine_url: URL = None

        self._registry = threading.local()
        self._logger = logging.getLogger(self.__class__.__name__)

    def get_connection(self) -> Connection:
        conn = getattr(self._registry, "connection", None)
        if conn is None:
            conn = self.engine.connect()
            self._registry.connection = conn

        return conn

    def close_connection(self) -> None:
        conn = getattr(self._registry, "connection", None)
        if conn is not None:
            conn.close()
            self._registry.connection = None

    @contextmanager
    def connection(self, *, isolation_level: str | None = None) -> Generator[Connection, None, None]:
        conn = self.get_connection()
        base_conn = conn
        if isolation_level is not None:
            conn = conn.execution_options(isolation_level=isolation_level)
            self._registry.connection = conn
        transaction = conn.begin_nested() if conn.in_transaction() else conn.begin()
        try:
            yield conn
            transaction.commit()
        except Exception:
            if transaction.is_active:
                transaction.rollback()
            raise
        finally:
            if isolation_level is not None:
                self._registry.connection = base_conn
            if not conn.in_transaction():
                self.close_connection()

    def configure_connection(self, connection) -> Connection:
        return connection

    def connect(self) -> None:
        self._logger.debug("Initialize database engine")
        self.engine_url = URL.create(
            drivername=self.drivename,
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            query=self.metaflags,
        )
        connect_args: Dict[str, Any] = {}
        if self.require_secure_transport:
            if self.driver == DBDriver.PG8000:
                connect_args = {"ssl_context": True}
            elif self.driver == DBDriver.PSYCOPG2:
                connect_args = {
                    "sslcert": self._sslcert,
                    "sslkey": self._sslkey,
                    "sslmode": self._sslmode,
                    "sslrootcert": self._sslrootcert,
                }
        self.engine = create_engine(
            self.engine_url,
            pool_size=5,
            max_overflow=0,
            pool_pre_ping=True,
            pool_recycle=DEFAULT_POOL_RECYCLE,
            connect_args=connect_args,
        )

    def close(self) -> None:
        self._logger.debug("Close database connection")
        conn = getattr(self._registry, "connection", None)
        if not conn:
            return
        self._registry.connection = None
        try:
            conn.commit()
        except Exception:
            conn.rollback()
        conn.close()

    def healthcheck(self):
        with self.connection() as conn:
            conn.execute(text("select 1;"))
