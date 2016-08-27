import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor

psycopg2.extensions.register_adapter(list, psycopg2.extensions.SQL_IN)


class _Cursor(DictCursor):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()


class DictContextConnection(connection):
    def cursor(self, *args, **kwargs):
        kwargs.setdefault('cursor_factory', _Cursor)
        return super(DictContextConnection, self).cursor(*args, **kwargs)


class RemoteDictContextConnection(DictContextConnection):
    def close(self, *args, **kargs):
        if hasattr(self, "_tunnel"):
            try:
                self._tunnel.stop()
            except:
                pass
        return super(RemoteDictContextConnection, self).close(*args, **kargs)


class DBFactory:
    _db_cache = {}

    @classmethod
    def _build_db(klass, db_config, global_config):
        dbname = db_config["dbname"]
        host = db_config.get("host", None)
        user = db_config.get("user", None)
        password = db_config.get("password", None)
        port = db_config.get("port", None)

        if "remote" in db_config:
            from utils.remote import RemoteConnections
            remote_conn = RemoteConnections.get(global_config, db_config["remote"])
            remote_tunnel = remote_conn.make_tunnel(
                (host or "localhost", int(port or "5432"))
            )
            remote_tunnel.start()
            host = remote_tunnel.local_bind_host
            port = remote_tunnel.local_bind_port
            connection_factory = RemoteDictContextConnection
        else:
            connection_factory = DictContextConnection

        ret = psycopg2.connect(database=dbname, host=host, user=user, password=password,
                               port=port,
                               connection_factory=connection_factory)
        if "remote" in db_config:
            ret._tunnel = remote_tunnel
        return ret

    @classmethod
    def close_all(klass):
        for db_name in klass._db_cache.keys():
            klass._db_cache[db_name].close()
            del klass._db_cache[db_name]

    @classmethod
    def get_db(klass, global_config, db_name):
        if db_name not in klass._db_cache:
            db_config = [c for c in global_config["databases"] if c["name"] == db_name]
            if not db_config:
                raise RuntimeError("No se encuentra la db %s en databases" % db_name)
            klass._db_cache[db_name] = klass._build_db(db_config[0], global_config)
        return klass._db_cache[db_name]
