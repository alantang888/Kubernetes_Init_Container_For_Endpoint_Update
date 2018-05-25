from kubernetes import client, config
import argparse
import os


def create_endpoint(endpoint_name: str, namespace: str) -> client.V1Endpoints:
    metadata = client.V1ObjectMeta()
    metadata.name = endpoint_name
    metadata.namespace = namespace

    new_endpoint = client.V1Endpoints(api_version='v1', kind='Endpoints', metadata=metadata)
    return new_endpoint


def create_endpoint_address(ip: str, pod: client.V1Pod) -> client.V1EndpointAddress:
    new_address = client.V1EndpointAddress(ip=ip, node_name=pod.spec.node_name)
    target_ref = client.V1ObjectReference(kind='Pod', name=pod.metadata.name, namespace=pod.metadata.namespace,
                                          uid=pod.metadata.uid, resource_version=pod.metadata.resource_version)
    new_address.target_ref = target_ref
    return new_address


def create_endpoint_port(port: int, name: str, protocol: str='TCP') -> client.V1EndpointPort:
    new_port = client.V1EndpointPort(port=port, name=name, protocol=protocol)
    return new_port


def update_endpoint(endpoint: client.V1Endpoints, ip: str, pod: client.V1Pod):
    if endpoint.subsets is not None and len(endpoint.subsets) > 0:
        subset = endpoint.subsets[0]
    else:
        subset = client.V1EndpointSubset()
        subset.ports = [create_endpoint_port(8200, 'vaultport'), create_endpoint_port(8201, 'backendport')]
        endpoint.subsets = [subset]

    subset.addresses = [create_endpoint_address(ip, pod)]


def parse_args():
    parser = argparse.ArgumentParser(description='Update endpoint IP.')
    parser.add_argument('--pod', required=True, help='Name of target endpoint')
    parser.add_argument('--endpoint', required=True, help='Name of target endpoint')
    parser.add_argument('--namespace', required=True, help='Namespace of target endpoint')
    parser.add_argument('--ip', required=True, help='New target of target endpoint')
    return parser.parse_args()


def main():
    args = parse_args()

    # hack for environment
    if ("KUBERNETES_SERVICE_HOST" not in os.environ or
            "KUBERNETES_SERVICE_PORT" not in os.environ):
        os.environ["KUBERNETES_SERVICE_HOST"] = "openshift.default.svc.cluster.local"
        os.environ["KUBERNETES_SERVICE_PORT"] = "443"

    pod_name = args.pod
    endpoint_name = args.endpoint
    namespace = args.namespace
    ip = args.ip

    config.load_incluster_config()

    v1 = client.CoreV1Api()
    try:
        pod = v1.read_namespaced_pod(pod_name, namespace)
        endpoint = v1.read_namespaced_endpoints(endpoint_name, namespace)
    except Exception as e:
        endpoint = create_endpoint(endpoint_name, namespace)
        v1.create_namespaced_endpoints(namespace, endpoint)

    update_endpoint(endpoint, ip, pod)

    v1.replace_namespaced_endpoints(endpoint_name, namespace, endpoint)


if __name__ == '__main__':
    main()