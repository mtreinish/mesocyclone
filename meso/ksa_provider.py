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

import re

from six.moves.urllib import parse as urlparse


class Credentials(object):
    def __init__(self, session):
        self.session = session

    @property
    def user_id(self):
        return self.session.get_user_id()

    @property
    def tenant_id(self):
        return self.session.get_project_id()

    @property
    def password(self):
        # Password is checked for existence in some cases but never directly
        # used as the auth provider is responsible for tokens. Since ksa
        # will handle this lets return something to not break any potential
        # checks, but rely on ksa to do the heavy lifting
        return 'NotARealPassword'

    @property
    def tenant_name(self):
        # I don't think ksa has an easy method for this, we might have to query
        # for it if it's required
        return ''

    @property
    def username(self):
        # I don't think ksa has an easy method for this, we might have to query
        # for it if it's required
        return ''


class KSAAuthProvider(object):
    def __init__(self, session):
        self.session = session
        self.credentials = Credentials(self.session)

    def base_url(self, filters, auth_data):
        service_type = filters.get('service')
        region_name = filters.get('region')
        interface = filters.get('endpoint_type', 'publicURL')
        endpoint_dict = {}
        if service_type:
            endpoint_dict['service_type'] = service_type
        if region_name:
            endpoint_dict['region_name'] = region_name
        if interface:
            endpoint_dict['interface'] = interface
        return self.session.get_endpoint(**endpoint_dict)

    def auth_request(self, method, url, headers=None, body=None, filters=None):
        auth_headers = self.session.get_auth_headers()
        if headers:
            req_headers = headers.copy()
            req_headers.update(auth_headers)
        else:
            req_headers = auth_headers
        base_url = self.base_url(filters=filters)
        if url is None or url == "":
            req_url = base_url
        else:
            _url = "/".join([base_url, url])
            parts = [x for x in urlparse.urlparse(_url)]
            parts[2] = re.sub("/{2,}", "/", parts[2])
            req_url = urlparse.urlunparse(parts)
        return str(req_url), req_headers, body

    def get_token(self):
        self.session.get_token()
