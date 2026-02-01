# k8s-netops-crd

A learning project to build a Kubernetes-based control plane for network devices
(spine/leaf, EVPN/VXLAN style), using CRDs and a custom controller.

## What exists so far

### Custom Resource Definitions (CRDs)
- **NetworkDevice**
  - Represents a managed network device (switch/router)
  - Similar concept to a Kubernetes Node
- **DeviceConfig**
  - Represents desired configuration intent for a device
  - Similar concept to Deployment/ConfigMap


### Current Controller
- A Python-based controller that:
  - Watches `DeviceConfig` objects
  - Reacts to add/update events
  - Reads `spec`
  - Writes basic reconciliation data into `status`

> No real device configuration is applied yet.
> This stage focuses purely on Kubernetes control-plane mechanics.

## Repository Structure
.
├── crds/ # CRD definitions (API schema)
├── controllers/ # Python controllers (reconcile logic)
├── requirements.txt
├── README.md

## Status Model
The controller currently updates:
- `status.phase`
- `status.observedGeneration`
- `status.message`

This confirms the reconcile loop is functional.

## Next Steps (planned)
- Resolve `NetworkDevice` references inside the controller
- Add adapter abstraction (NETCONF / gNMI)
- Apply real configuration intents
- Handle errors, retries, and drift detection
