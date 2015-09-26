===============================
mesocyclone
===============================

A os-client-config tempest-lib interface

* Free software: Apache license


Usage
=====

To initialize a client do something like the following example::

  from meso import client
  from tempest_lib.services.compute import agents_client

  cloud = client.Cloud()
  agent_client = agents_client.AgentsClient(
      service=cloud.cloud_config.get_service_type('compute'),
      **cloud.common_rest_client_kwargs)

Or if you already have an existing ksa Session object use::

  from meso import client
  from tempest_lib.services.compute import agents_client

  cloud = client.KSACloud(session)
  agent_client = agents_client.AgentsClient(
      service=cloud.cloud_config.get_service_type('compute'),
      **cloud.common_rest_client_kwargs)
