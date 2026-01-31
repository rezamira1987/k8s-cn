"""
DeviceConfig Controller - Step 13.3
Reconcile: read spec, write status (no device actions yet)
"""

from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

GROUP = "netops.example.com"
VERSION = "v1alpha1"
PLURAL = "deviceconfigs"


def load_kube():
    try:
        config.load_kube_config()
    except Exception:
        config.load_incluster_config()


def reconcile(api: client.CustomObjectsApi, obj: dict) -> None:
    meta = obj.get("metadata", {})
    spec = obj.get("spec", {})

    name = meta["name"]
    namespace = meta.get("namespace", "default")
    generation = meta.get("generation", 0)

    device_ref = spec.get("deviceRef", {})
    intent = spec.get("intent", {})
    dry_run = spec.get("dryRun", False)

    # For now: just reflect that we observed it and stored a friendly summary
    status = {
        "observedGeneration": generation,
        "phase": "pending",
        "message": f"observed deviceRef={device_ref.get('name')} dryRun={dry_run} intentKeys={sorted(intent.keys())}",
    }

    body = {"status": status}

    try:
        api.patch_namespaced_custom_object_status(
            group=GROUP,
            version=VERSION,
            namespace=namespace,
            plural=PLURAL,
            name=name,
            body=body,
        )
        print(f"[RECONCILED] {namespace}/{name} -> phase=pending")
    except ApiException as e:
        print(f"[ERROR] failed to patch status for {namespace}/{name}: {e.status} {e.reason}")


def main():
    load_kube()

    api = client.CustomObjectsApi()
    w = watch.Watch()

    print("Watching DeviceConfig objects (with reconcile)...")

    for event in w.stream(
        api.list_cluster_custom_object,
        group=GROUP,
        version=VERSION,
        plural=PLURAL,
    ):
        event_type = event["type"]
        obj = event["object"]

        # Ignore deletes for now
        if event_type == "DELETED":
            meta = obj.get("metadata", {})
            print(f"[DELETED] {meta.get('namespace','default')}/{meta.get('name')}")
            continue

        reconcile(api, obj)


if __name__ == "__main__":
    main()
