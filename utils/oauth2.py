# -*- coding: utf-8 -*-
import argparse
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
import oauth2client.tools as oauthtools


class OA2CredentialsFactory:
    _oauth2_cache = {}

    @classmethod
    def _build_credentials(klass, oauth2_config, global_config):
        client_secrets = oauth2_config["client_secrets"]
        oauth2_storage = oauth2_config["oauth2_storage"]
        scope = oauth2_config["scope"]

        flow = flow_from_clientsecrets(client_secrets, scope=scope)
        storage = Storage(oauth2_storage)
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            parser = argparse.ArgumentParser(description=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter,
                parents=[oauthtools.argparser])
            flags = parser.parse_args([])
            credentials = oauthtools.run_flow(flow, storage, flags)
        return credentials

    @classmethod
    def close_all(klass):
        pass

    @classmethod
    def get_credentials(klass, global_config, name):
        if name not in klass._oauth2_cache:
            oauth2_config = [c for c in global_config["oauth2_auths"] if c["name"] == name]
            if not oauth2_config:
                raise RuntimeError("No se encuentra la autenticación %s en oauth2_auths" % name)
            klass._oauth2_cache[name] = klass._build_credentials(oauth2_config[0], global_config)
        return klass._oauth2_cache[name]
