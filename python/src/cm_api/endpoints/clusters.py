# Copyright (c) 2012 Cloudera, Inc. All rights reserved.

try:
  import json
except ImportError:
  import simplejson as json

from cm_api.endpoints.types import ApiCommand, ApiList, BaseApiObject
from cm_api.endpoints import services

__docformat__ = "epytext"

CLUSTERS_PATH = "/clusters"

def create_cluster(resource_root, name):
  """
  Create a cluster
  @param resource_root: The root Resource object.
  @param name: Cluster name
  @return: An ApiCluster object
  """
  apicluster = ApiCluster(resource_root, name)
  apicluster_list = ApiList([apicluster])
  body = json.dumps(apicluster_list.to_json_dict())
  resp = resource_root.post(CLUSTERS_PATH, data=body)
  # The server returns a list of created clusters (with size 1)
  return ApiList.from_json_dict(ApiCluster, resp, resource_root)[0]

def get_cluster(resource_root, name):
  """
  Lookup a cluster by name
  @param resource_root: The root Resource object.
  @param name: Cluster name
  @return: An ApiCluster object
  """
  dic = resource_root.get("%s/%s" % (CLUSTERS_PATH, name))
  return ApiCluster.from_json_dict(dic, resource_root)

def get_all_clusters(resource_root, view=None):
  """
  Get all clusters
  @param resource_root: The root Resource object.
  @return: A list of ApiCluster objects.
  """
  dic = resource_root.get(CLUSTERS_PATH,
          params=view and dict(view=view) or None)
  return ApiList.from_json_dict(ApiCluster, dic, resource_root)

def delete_cluster(resource_root, name):
  """
  Delete a cluster by name
  @param resource_root: The root Resource object.
  @param name: Cluster name
  @return: The deleted ApiCluster object
  """
  resp = resource_root.delete("%s/%s" % (CLUSTERS_PATH, name))
  return ApiCluster.from_json_dict(resp, resource_root)


class ApiCluster(BaseApiObject):
  RW_ATTR = ('name',)

  def __init__(self, resource_root, name):
    BaseApiObject.ctor_helper(**locals())

  def _path(self):
    return "%s/%s" % (CLUSTERS_PATH, self.name)

  def _cmd(self, cmd, data=None):
    path = self._path() + '/commands/' + cmd
    resp = self._get_resource_root().post(path, data=data)
    return ApiCommand.from_json_dict(resp, self._get_resource_root())

  def create_service(self, name, service_type, version):
    """
    Create a service.

    @param name: Service name
    @param service_type: Service type
    @param version: Service version
    @return: An ApiService object
    """
    return services.create_service(self._get_resource_root(), name,
        service_type, version, self.name)

  def delete_service(self, name):
    """
    Delete a service by name.

    @param name Service name
    @return The deleted ApiService object
    """
    return services.delete_service(self._get_resource_root(), name, self.name)

  def get_service(self, name):
    """
    Lookup a service by name.

    @param name: Service name
    @return: An ApiService object
    """
    return services.get_service(self._get_resource_root(), name, self.name)

  def get_all_services(self, view = None):
    """
    Get all services in this cluster.

    @return: A list of ApiService objects.
    """
    return services.get_all_services(self._get_resource_root(), self.name, view)

  def collect_host_stats(self, start_datetime, end_datetime, includeInfoLog=False):
    """
    Issue the collect host stats command.

    @param start_datetime: The start of the collection period. Type datetime.
    @param end_datetime: The end of the collection period. Type datetime.
    @param includeInfoLog: Whether to include INFO level log messages.
    """
    args = {
        'startTime': start_datetime.isoformat(),
        'endTime': end_datetime.isoformat(),
        'includeInfoLog': includeInfoLog,
    }
    return self._cmd('collectHostStats', data=json.dumps(args))