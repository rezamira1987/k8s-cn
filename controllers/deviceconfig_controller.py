"""
DeviceConfig Controller - Step 13.4
Reconcile:
- Read DeviceConfig.spec
- Resolve referenced NetworkDevice
- Write status based on whether NetworkDevice exists

No device actions yet.
"""

from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

GROUP = "netops.example.com"
VERSION = "v1alpha1"
DEVICECONFIGS = "deviceconfigs"
NETWORKDEVICES = "networkdevices"


def load_kube():
    try:
        config.load_kube_config()
    except Exception:
        config.load_incluster_config()


def get_network_device(
    api: client.CustomObjectsApi, namespace: str, name: str
) -> dict | None:
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


def patch_deviceconfig_status(
    api: client.CustomObjectsApi,
    namespace: str,
    name: str,
    status: dict,
) -> None:
    api.patch_namespaced_custom_object_status(
        group=GROUP,
        version=VERSION,
        namespace=namespace,
        plural=DEVICECONFIGS,
        name=name,
        body={"status": status},
    )


def reconcile(api: client.CustomObjectsApi, obj: dict) -> None:
    meta = obj.get("metadata", {})
    spec = obj.get("spec", {})

    name = meta["name"]
    namespace = meta.get("namespace", "default")
    generation = meta.get("generation", 0)

    device_ref = spec.get("deviceRef", {}) or {}
    device_name = device_ref.get("name")
    dry_run = spec.get("dryRun", False)
    intent = spec.get("intent", {}) or {}

    base_status = {
        "observedGeneration": generation,
    }

    if not device_name:
        status = {
            **base_status,
            "phase": "error",
            "message": "deviceRef.name is required",
            "lastError": {"code": "MissingDeviceRef", "detail": "spec.deviceRef.name is empty"},
        }
        patch_deviceconfig_status(api, namespace, name, status)
        print(f"[RECONCILED] {namespace}/{name} -> error (missing deviceRef.name)")
        return

    nd = get_network_device(api, namespace, device_name)

    if nd is None:
        status = {
            **base_status,
            "phase": "error",
            "message": f"referenced NetworkDevice '{device_name}' not found",
            "lastError": {"code": "NetworkDeviceNotFound", "detail": device_name},
        }
        patch_deviceconfig_status(api, namespace, name, status)
        print(f"[RECONCILED] {namespace}/{name} -> error (NetworkDevice not found: {device_name})")
        return

    nd_spec = nd.get("spec", {}) or {}
    endpoint = (nd_spec.get("endpoint") or {}).get("address")
    vendor = (nd_spec.get("platform") or {}).get("vendor")
    osname = (nd_spec.get("platform") or {}).get("os")

    status = {
        **base_status,
        "phase": "pending",
        "message": (
            f"resolved device={device_name} vendor={vendor} os={osname} "
            f"endpoint={endpoint} dryRun={dry_run} intentKeys={sorted(intent.keys())}"
        ),
    }
    patch_deviceconfig_status(api, namespace, name, status)
    print(f"[RECONCILED] {namespace}/{name} -> pending (resolved NetworkDevice={device_name})")


def main():
    load_kube()
    api = client.CustomObjectsApi()
    w = watch.Watch()

    print("Watching DeviceConfig objects (resolve deviceRef)...")

    for event in w.stream(
        api.list_cluster_custom_object,
        group=GROUP,
        version=VERSION,
        plural=DEVICECONFIGS,
    ):
        event_type = event["type"]
        obj = event["object"]

        if event_type == "DELETED":
            meta = obj.get("metadata", {})
            print(f"[DELETED] {meta.get('namespace','default')}/{meta.get('name')}")
            continue

        reconcile(api, obj)


if __name__ == "__main__":
    main()
