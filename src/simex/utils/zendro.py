import os
import requests

from sgqlc.operation import Operation
from sgqlc.endpoint.http import HTTPEndpoint

from simex.sipecam_zendro_schema import sipecam_zendro_schema
from simex.settings import SIPECAM_ZENDRO_GQL_URL, SIPECAM_ZENDRO_GQL_USER, \
SIPECAM_ZENDRO_GQL_PASSWORD

def get_credentials():
    return {
            "username": SIPECAM_ZENDRO_GQL_USER,
            "password": SIPECAM_ZENDRO_GQL_PASSWORD,
           }
def get_zendro_url_for_login():
    return os.path.join(SIPECAM_ZENDRO_GQL_URL,"login")

def get_zendro_url_for_gql():
    return os.path.join(SIPECAM_ZENDRO_GQL_URL, "graphql")

def get_token():
    """
    Get a token that allows to make zendro queries.

    Returns:
        token (str):  token.
    """
    login = requests.post(get_zendro_url_for_login(),
                          data=get_credentials())

    if login.status_code == 200:
        return login.json()['token']
    else:
        print("bad credentials in .simex_env")
        return None
def get_sgqlc_endpoint_and_operation_for_query():
    token = get_token()

    headers = {
        "Authorization": "Bearer " + token,
        "Accept": "application/json",
        'Content-Type': 'application/json; charset=utf-8'
    }

    endpoint = HTTPEndpoint(get_zendro_url_for_gql(),
                            headers)
    return (endpoint,
            Operation(sipecam_zendro_schema.Query))

def query_for_copy_files_to_standard_directory(serial_number,
                                               first_date,
                                               second_date):
    """
    Execute in GQL of Zendro:
    query {
      physical_devices(pagination: {limit: 0},
                       search: {field: serial_number,
                                value: "<serial_number>",
                                operator: like})
                        {
                        device_deploymentsFilter(pagination: {limit: 0},
                                                 search: {operator: and,
                                                          search: [{field: date_deployment,
                                                                    value: "<first_date>",
                                                                    valueType: String,
                                                                    operator: gte},
                                                                  {field: date_deployment,
                                                                   value: "<second_date>",
                                                                   valueType: String,
                                                                   operator: lte}]
                                                          })
                                                 {
                                                  node {
                                                      nomenclatura
                                                       }
                                                  cumulus {
                                                      name
                                                       }
                                                  date_deployment
                                                  }
                        }
          }
    """
    endpoint, op = get_sgqlc_endpoint_and_operation_for_query()

    op.physical_devices(pagination={"limit": 0},
                        search={"field": "serial_number",
                                "value": serial_number,
                                "operator": "like"})

    op.physical_devices.device_deployments_filter(pagination={"limit": 0},
                                                  search={"operator": "and",
                                                          "search": [{"field"   : "date_deployment",
                                                                      "value"   : first_date,
                                                                      "valueType": "String",
                                                                      "operator": "gte"},
                                                                     {"field"   : "date_deployment",
                                                                      "value"   : second_date,
                                                                      "valueType": "String",
                                                                      "operator": "lte"}
                                                                     ]
                                                          }
                                                  )
    op.physical_devices.device_deployments_filter.node.nomenclatura() #after this line op has type sgqlc selection
    op.physical_devices.device_deployments_filter.cumulus.name()
    op.physical_devices.device_deployments_filter.date_deployment()
    query_result = endpoint(op)
    return (query_result, op)

def query_alternative_auxiliar_for_copy_files_to_standard_directory(serial_number):
    """
    Execute in GQL of Zendro:
    query {
      physical_devices(pagination: {limit: 0}, 
                       search: {field: serial_number, 
                       value: "<serial_number>", 
                       operator: like}) 
                       {
                        device_deploymentsFilter(pagination: {limit: 0})
                                                 {
                                                   date_deployment
                                                 }
                       }
    }
    """
    endpoint, op = get_sgqlc_endpoint_and_operation_for_query()
    op.physical_devices(pagination={"limit": 0},
                        search={"field": "serial_number",
                                "value": serial_number,
                                "operator": "like"})
    op.physical_devices.device_deployments_filter(pagination={"limit": 0}).date_deployment()
    query_result = endpoint(op)
    return (query_result, op)

def query_alternative_for_copy_files_to_standard_directory(serial_number,
                                                           date_for_filter):
    """
    Execute in GQL of Zendro:
    query {
      physical_devices(pagination: {limit: 0}, 
                       search: {field: serial_number, 
                                value: "<serial_number>", 
                                operator: like})
                       {
                        device_deploymentsFilter(pagination: {limit: 0}, 
                                                 search: {field: date_deployment, 
                                                 value: "<date_for_filter>", 
                                                 operator: eq})
                                                 {
                                                  node {
                                                    nomenclatura
                                                  }
                                                  cumulus {
                                                    name
                                                  }
                                                  date_deployment
                                                 }
                       }
    }    
    """
    endpoint, op = get_sgqlc_endpoint_and_operation_for_query()
    op.physical_devices(pagination={"limit": 0},
                        search={"field": "serial_number",
                                "value": serial_number,
                                "operator": "like"})
    op.physical_devices.device_deployments_filter(pagination={"limit": 0},
                                                  search={"field": "date_deployment",
                                                          "value": date_for_filter,
                                                          "operator": "eq"})
    op.physical_devices.device_deployments_filter.node.nomenclatura() #after this line op has type sgqlc selection
    op.physical_devices.device_deployments_filter.cumulus.name()
    query_result = endpoint(op)
    return (query_result, op)