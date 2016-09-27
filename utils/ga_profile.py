# -*- coding: utf-8 -*-
import googleanalytics
from utils.oauth2 import OA2CredentialsFactory


class GAProfilesFactory:
    _profiles_cache = {}

    @classmethod
    def _build_profile(klass, profile_config, global_config):
        oa2_credentials = profile_config.get("credentials", global_config.get("default_oa2_credentials"))
        credentials = OA2CredentialsFactory.get_credentials(global_config, oa2_credentials)
        profile = googleanalytics.authenticate(
            identity=profile_config.get("identity"),
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
            access_token=credentials.access_token,
            account=profile_config.get("account"),
            webproperty=profile_config.get("webproperty"),
        )
        return profile

    @classmethod
    def close_all(klass):
        pass

    @classmethod
    def get_profile(klass, global_config, name):
        if name not in klass._profiles_cache:
            profile_config = [c for c in global_config["googleanalytics_profiles"] if c["name"] == name]
            if not profile_config:
                raise RuntimeError("No se encuentra el profile %s en googleanalytics_profiles" % name)
            klass._profiles_cache[name] = klass._build_profile(profile_config[0], global_config)
        return klass._profiles_cache[name]
