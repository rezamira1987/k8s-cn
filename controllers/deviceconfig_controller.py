from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

from adapters.base import (
    DeviceEndpoint,
    DevicePlatform,
    DeviceCredentialsRef,
    NetworkDeviceSpec,
)
from adapters.dummy import DummyAdapter

GROUP = "netops.example.com"
VERSION = "v1alpha1"
DEVICECONFIGS = "deviceconfigs"
NETWORKDEVICES = "networkdevices"


def load_kube():
    try:
        config.load_kube_config()
    except Exception:
        config.load_incluster_config()


def get_network_device(api, namespace, name):
    try:
        return api.get_namespaced_custom_object(
            group=GROUP,
            version=VERSION,
            namespace=namespace,
            plural=NETWORKDEVICES,
            name=name,
        )
    except ApiException as e:
        if e.status == 404:
            return None
        raise


def patch_status(api, namespace, name, status):
    api.patch_namespaced_custom_object_status(
        group=GROUP,
        version=VERSION,
        namespace=namespace,
        plural=DEVICECONFIGS,
        name=name,
        body={"status": status},
    )


def build_device_spec(nd_obj):
    spec = nd_obj.get("spec", {})
    endpoint = spec.get("endpoint", {})
    platform = spec.get("platform", {})

    return NetworkDeviceSpec(
        name=nd_obj["metadata"]["name"],
        namespace=nd_obj["metadata"].get("namespace", "default"),
        endpoint=DeviceEndpoint(
            address=endpoint["address"],
            port=endpoint.get("port", 830),
        ),
        platform=DevicePlatform(
            vendor=platform.get("vendor"),
            os=platform.get("os"),
            model=platform.get("model"),
        ),
        transport=spec.get("transport", "netconf"),
        credentials_ref=(
            DeviceCredentialsRef(**spec["credentialsRef"])
            if "credentialsRef" in spec
            else None
        ),
        role=spec.get("role"),
    )


def reconcile(api, adapter, obj):
    meta = obj["metadata"]
    spec = obj["spec"]

    name = meta["name"]
    namespace = meta.get("namespace", "default")
    generation = meta.get("generation", 0)

    device_name = spec.get("deviceRef", {}).get("name")
    intent = spec.get("intent", {}) or {}
    dry_run = spec.get("dryRun", False)

    base = {"observedGeneration": generation}

    if not device_name:
        patch_status(api, namespace, name, {
            **base,
            "phase": "error",
            "message": "deviceRef.name missing",
        })
        return

    nd = get_network_device(api, namespace, device_name)
    if nd is None:
        patch_status(api, namespace, name, {
            **base,
            "phase": "error",
            "message": f"NetworkDevice '{device_name}' not found",
        })
        return

    device = build_device_spec(nd)

    # 1) validate
    v = adapter.validate_intent(intent)
    if not v.ok:
        patch_status(api, namespace, name, {
            **base,
            "phase": "error",
            "message": v.detail,
        })
        return

    # 2) apply (dummy)
    r = adapter.apply_intent(device, intent, dry_run=dry_run)

    patch_status(api, namespace, name, {
        **base,
        "phase": "applied" if r.ok else "error",
        "message": r.detail,
        "changed": r.changed,
        "facts": r.facts,
    })


def main():
    load_kube()
    api = client.CustomObjectsApi()
    adapter = DummyAdapter()
    w = watch.Watch()

    print("Watching DeviceConfig objects (with DummyAdapter)...")

    for event in w.stream(
        api.list_cluster_custom_object,
        group=GROUP,
        version=VERSION,
        plural=DEVICECONFIGS,
    ):
        if event["type"] == "DELETED":
            continue
        reconcile(api, adapter, event["object"])


if __name__ == "__main__":
    main()
