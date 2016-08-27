import os.path
from paramiko import SSHConfig, RSAKey
from sshtunnel import SSHTunnelForwarder, open_tunnel


class RemoteConnection:
    def __init__(self, **kargs):
        self.ssh_config_file = kargs["ssh_config_file"]
        self.ssh_private_key = kargs["ssh_private_key"]
        self.hostname = None
        self.port = 22
        self.user = None
        self.password = None
        if "configname" in kargs:
            ssh_config = SSHConfig()
            ssh_config.parse(open(os.path.expanduser(self.ssh_config_file)))
            host_config = ssh_config.lookup(kargs["configname"])
            if "hostname" in host_config:
                self.hostname = host_config["hostname"]
            if "port" in host_config:
                self.port = int(host_config["port"])
            if "identityfile" in host_config:
                self.ssh_private_key = host_config["identityfile"][0]
            if "user" in host_config:
                self.user = host_config["user"]
        # Seteo los valores que vienen de nuestra config y que pueden pisar lo que
        # sale de configname
        for x in ["user", "password", "hostname"]:
            if x in kargs:
                setattr(self, x, kargs[x])
        if "port" in kargs:
            self.port = int(kargs["port"])

    def make_tunnel(self, remote_bind_address):
        if self.ssh_private_key:
            ssh_private_key = RSAKey.from_private_key_file(os.path.expanduser(self.ssh_private_key))
        else:
            ssh_private_key = None
        return SSHTunnelForwarder((self.hostname, self.port), ssh_config_file=self.ssh_config_file,
                                  ssh_password=self.password, ssh_private_key=ssh_private_key,
                                  ssh_username=self.user, remote_bind_address=remote_bind_address)


    def open_tunnel(self, remote_bind_address):
        if self.ssh_private_key:
            ssh_private_key = RSAKey.from_private_key_file(os.path.expanduser(self.ssh_private_key))
        else:
            ssh_private_key = None
        return open_tunnel((self.hostname, self.port), ssh_config_file=self.ssh_config_file,
                                  ssh_password=self.password, ssh_private_key=ssh_private_key,
                                  ssh_username=self.user, remote_bind_address=remote_bind_address)


class RemoteConnections:
    _db_cache = {}

    @classmethod
    def get(klass, global_config, name):
        remote_config = [c for c in global_config["remotes"] if c["name"] == name]
        if not remote_config:
            raise RuntimeError("No se encuentra el remoto %s en remotes" % name)
        remote_config = remote_config[0]
        global_defaults = {
            "ssh_config_file": "~/.ssh/config",
            "ssh_private_key": "~/.ssh/id_rsa",
        }
        for k, v in global_defaults.items():
            if not k in remote_config:
                remote_config[k] = global_config.get(k, v)
        return RemoteConnection(**remote_config)
