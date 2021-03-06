# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os

import os_client_config
import os_client_config.defaults
from tempest.lib import auth

from meso import ksa_provider


def get_client_manager(name=None, **kwargs):
    return Cloud(name, **kwargs).get_os_clients()


class Cloud(object):
    def __init__(self, name=None, build_interval=1, build_timeout=60,
                 disable_ssl_certificate_validation=False, ca_certs=None,
                 trace_requests='', default_domain=None):
        super(Cloud, self).__init__()
        config = os_client_config.OpenStackConfig()
        if not name:
            self.cloud_config = config.get_all_clouds()[0]
        else:
            self.cloud_config = config.get_one_cloud(name)
        self.default_domain = default_domain
        if not self.default_domain:
            self.default_domain = os.environ.get(
                'OS_DEFAULT_DOMAIN', 'default')
        provider_args = self.cloud_config.get_auth_args()
        provider_args['auth_version'] = self.cloud_config.get_api_version(
            'identity')
        if provider_args['auth_version'] not in provider_args['auth_url']:
            provider_args['auth_url'] = os.path.join(
                provider_args['auth_url'],
                'v' + provider_args['auth_version'])
        auth_provider = self._get_auth_provider(**provider_args)
        dscv = disable_ssl_certificate_validation
        # All that is missing is the service key which is the service_type for
        # the particular client being initialized.
        self.common_rest_client_kwargs = {
            'auth_provider': auth_provider,
            'region': self.cloud_config.get_region_name(),
            'build_interval': build_interval,
            'build_timeout': build_timeout,
            'disable_ssl_certificate_validation': dscv,
            'ca_certs': ca_certs,
            'trace_requests': trace_requests,
        }

    def get_os_clients(self):
        """Return a client manager object similar to tempest.client"""
        pass

    def _get_auth_provider(self, username, password, project_name,
                           auth_url, user_domain_name=None,
                           project_domain_name=None, auth_version='3'):
        provider_kwargs = {
            'username': username,
            'password': password,
        }
        if auth_version == '3':
            provider_kwargs['identity_version'] = 'v3'
            provider_kwargs['project_name'] = project_name
            provider_class = auth.KeystoneV3AuthProvider
            if not project_domain_name and not user_domain_name:
                provider_kwargs['user_domain_name'] = self.default_domain
                provider_kwargs['project_domain_name'] = self.default_domain
            elif project_domain_name:
                provider_kwargs['project_domain_name'] = project_domain_name
                if not user_domain_name:
                    provider_kwargs['user_domain_name'] = project_domain_name
                else:
                    provider_kwargs['user_domain_name'] = user_domain_name
            elif user_domain_name:
                provider_kwargs['user_domain_name'] = user_domain_name
                provider_kwargs['project_domain_name'] = user_domain_name
        else:
            provider_kwargs['identity_version'] = 'v2'
            provider_kwargs['tenant_name'] = project_name
            provider_class = auth.KeystoneV2AuthProvider
        credentials = auth.get_credentials(auth_url, fill_in=True,
                                           **provider_kwargs)
        return provider_class(credentials, auth_url)


class KSACloud(object):
    def __init__(self, session, name=None, build_interval=1, build_timeout=60,
                 disable_ssl_certificate_validation=False, ca_certs=None,
                 trace_requests='', cloud_config=None):
        if not cloud_config:
            config = os_client_config.OpenStackConfig()
            if not name:
                self.cloud_config = config.get_all_clouds()[0]
            else:
                self.cloud_config = config.get_one_cloud(name)
        else:
            self.cloud_config = cloud_config
        auth_provider = ksa_provider.KSAAuthProvider(session)
        dscv = disable_ssl_certificate_validation
        self.common_rest_client_kwargs = {
            'auth_provider': auth_provider,
            'region': self.cloud_config.get_region_name(),
            'build_interval': build_interval,
            'build_timeout': build_timeout,
            'disable_ssl_certificate_validation': dscv,
            'ca_certs': ca_certs,
            'trace_requests': trace_requests,
        }
