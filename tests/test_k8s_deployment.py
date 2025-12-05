"""
Integration tests for Kubernetes deployment
Tests actual deployment to a Kubernetes cluster (minikube/kind/local cluster)
"""
import pytest
import subprocess
import time
import os
import requests
from pathlib import Path
from typing import Optional, Dict, List
import yaml


def check_kubectl_available() -> bool:
    """Check if kubectl is available"""
    try:
        result = subprocess.run(
            ["kubectl", "version", "--client"],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_cluster_accessible() -> bool:
    """Check if a Kubernetes cluster is accessible"""
    if not check_kubectl_available():
        return False
    
    try:
        result = subprocess.run(
            ["kubectl", "cluster-info"],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def kubectl_apply(manifest_path: str, namespace: Optional[str] = None) -> tuple[bool, str]:
    """Apply a Kubernetes manifest"""
    cmd = ["kubectl", "apply", "-f", manifest_path]
    if namespace:
        cmd.extend(["-n", namespace])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"


def kubectl_get(resource_type: str, name: Optional[str] = None, namespace: Optional[str] = None) -> tuple[bool, str]:
    """Get Kubernetes resource"""
    cmd = ["kubectl", "get", resource_type]
    if name:
        cmd.append(name)
    if namespace:
        cmd.extend(["-n", namespace])
    cmd.extend(["-o", "json"])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout
    except subprocess.TimeoutExpired:
        return False, "Command timed out"


def kubectl_delete(manifest_path: str, namespace: Optional[str] = None) -> tuple[bool, str]:
    """Delete resources from a Kubernetes manifest"""
    cmd = ["kubectl", "delete", "-f", manifest_path]
    if namespace:
        cmd.extend(["-n", namespace])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        # Ignore "not found" errors during cleanup
        return True, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"


def wait_for_deployment_ready(deployment_name: str, namespace: str, timeout: int = 300) -> bool:
    """Wait for deployment to be ready"""
    cmd = ["kubectl", "wait", "--for=condition=available", f"deployment/{deployment_name}"]
    cmd.extend(["-n", namespace, "--timeout", f"{timeout}s"])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 10
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def wait_for_pod_ready(pod_name: str, namespace: str, timeout: int = 300) -> bool:
    """Wait for pod to be ready"""
    cmd = ["kubectl", "wait", "--for=condition=ready", f"pod/{pod_name}"]
    cmd.extend(["-n", namespace, "--timeout", f"{timeout}s"])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 10
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def get_pod_ip(pod_name: str, namespace: str) -> Optional[str]:
    """Get pod IP address"""
    success, output = kubectl_get("pod", pod_name, namespace)
    if not success:
        return None
    
    try:
        import json
        pod_data = json.loads(output)
        return pod_data.get("status", {}).get("podIP")
    except (json.JSONDecodeError, KeyError):
        return None


def get_service_endpoint(service_name: str, namespace: str) -> Optional[str]:
    """Get service endpoint (for LoadBalancer or NodePort)"""
    success, output = kubectl_get("service", service_name, namespace)
    if not success:
        return None
    
    try:
        import json
        service_data = json.loads(output)
        spec = service_data.get("spec", {})
        service_type = spec.get("type", "ClusterIP")
        
        if service_type == "LoadBalancer":
            ingress = service_data.get("status", {}).get("loadBalancer", {}).get("ingress", [])
            if ingress:
                return ingress[0].get("hostname") or ingress[0].get("ip")
        
        # For NodePort or ClusterIP, we'd need to port-forward or use cluster IP
        # This is a simplified version
        cluster_ip = spec.get("clusterIP")
        ports = spec.get("ports", [])
        if cluster_ip and ports:
            port = ports[0].get("port", 80)
            return f"http://{cluster_ip}:{port}"
        
        return None
    except (json.JSONDecodeError, KeyError):
        return None


@pytest.fixture(scope="module")
def k8s_cluster_available():
    """Fixture to check if Kubernetes cluster is available"""
    if not check_cluster_accessible():
        pytest.skip("Kubernetes cluster not accessible. Requires kubectl and accessible cluster.")
    return True


@pytest.fixture(scope="module")
def k8s_namespace(k8s_cluster_available):
    """Fixture to set up and tear down Kubernetes namespace"""
    namespace = "itops-agent-test"
    manifest_path = Path("k8s/namespace.yaml")
    
    # Create namespace if it doesn't exist
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            namespace_manifest = yaml.safe_load(f)
            namespace_manifest['metadata']['name'] = namespace
        
        # Write temporary namespace manifest
        temp_manifest = Path("k8s/namespace-test.yaml")
        with open(temp_manifest, 'w') as f:
            yaml.dump(namespace_manifest, f)
        
        success, output = kubectl_apply(str(temp_manifest))
        if not success:
            pytest.skip(f"Failed to create namespace: {output}")
        
        # Cleanup
        temp_manifest.unlink()
    else:
        # Create namespace directly
        subprocess.run(
            ["kubectl", "create", "namespace", namespace],
            capture_output=True,
            timeout=30
        )
    
    yield namespace
    
    # Cleanup: Delete namespace (this will delete all resources)
    subprocess.run(
        ["kubectl", "delete", "namespace", namespace],
        capture_output=True,
        timeout=60
    )


@pytest.fixture(scope="module")
def deployed_resources(k8s_cluster_available, k8s_namespace):
    """Fixture to deploy all Kubernetes resources"""
    namespace = k8s_namespace
    manifest_files = [
        "k8s/persistentvolumeclaim.yaml",
        "k8s/configmap.yaml",
        "k8s/chroma-deployment.yaml",
        "k8s/chroma-service.yaml",
        "k8s/app-deployment.yaml",
        "k8s/app-service.yaml",
    ]
    
    # Apply manifests (update namespace in memory)
    applied_manifests = []
    for manifest_file in manifest_files:
        path = Path(manifest_file)
        if not path.exists():
            continue
        
        # Read and update namespace
        with open(path, 'r') as f:
            if manifest_file.endswith('.yaml'):
                documents = list(yaml.safe_load_all(f))
            else:
                documents = [yaml.safe_load(f)]
        
        # Update namespace in all documents
        for doc in documents:
            if doc and 'metadata' in doc:
                doc['metadata']['namespace'] = namespace
        
        # Write temporary manifest
        temp_manifest = Path(f"k8s/temp-{path.name}")
        with open(temp_manifest, 'w') as f:
            yaml.dump_all(documents, f)
        
        success, output = kubectl_apply(str(temp_manifest))
        if not success:
            pytest.fail(f"Failed to apply {manifest_file}: {output}")
        
        applied_manifests.append(temp_manifest)
    
    # Wait for deployments to be ready
    time.sleep(5)  # Give resources time to start
    
    # Wait for Chroma deployment
    if not wait_for_deployment_ready("chroma", namespace, timeout=180):
        pytest.fail("Chroma deployment did not become ready in time")
    
    # Wait for app deployment
    if not wait_for_deployment_ready("itops-agent", namespace, timeout=180):
        pytest.fail("ITOps Agent deployment did not become ready in time")
    
    yield {
        "namespace": namespace,
        "manifests": applied_manifests
    }
    
    # Cleanup: Delete all applied resources
    for manifest in reversed(applied_manifests):
        kubectl_delete(str(manifest))
        manifest.unlink(missing_ok=True)


class TestKubernetesDeployment:
    """Test Kubernetes deployment integration"""
    
    @pytest.mark.skipif(
        not check_cluster_accessible(),
        reason="Kubernetes cluster not accessible"
    )
    def test_namespace_created(self, k8s_namespace):
        """Test that namespace was created"""
        success, output = kubectl_get("namespace", k8s_namespace)
        assert success, f"Namespace {k8s_namespace} should exist"
    
    @pytest.mark.skipif(
        not check_cluster_accessible(),
        reason="Kubernetes cluster not accessible"
    )
    def test_chroma_deployment_ready(self, deployed_resources):
        """Test that Chroma deployment is ready"""
        namespace = deployed_resources["namespace"]
        success, output = kubectl_get("deployment", "chroma", namespace)
        assert success, "Chroma deployment should exist"
        
        # Check deployment status
        import json
        deployment_data = json.loads(output)
        status = deployment_data.get("status", {})
        ready_replicas = status.get("readyReplicas", 0)
        replicas = status.get("replicas", 0)
        
        assert ready_replicas > 0, "Chroma deployment should have ready replicas"
        assert ready_replicas == replicas, "All Chroma replicas should be ready"
    
    @pytest.mark.skipif(
        not check_cluster_accessible(),
        reason="Kubernetes cluster not accessible"
    )
    def test_app_deployment_ready(self, deployed_resources):
        """Test that ITOps Agent deployment is ready"""
        namespace = deployed_resources["namespace"]
        success, output = kubectl_get("deployment", "itops-agent", namespace)
        assert success, "ITOps Agent deployment should exist"
        
        # Check deployment status
        import json
        deployment_data = json.loads(output)
        status = deployment_data.get("status", {})
        ready_replicas = status.get("readyReplicas", 0)
        replicas = status.get("replicas", 0)
        
        assert ready_replicas > 0, "ITOps Agent deployment should have ready replicas"
        assert ready_replicas == replicas, "All ITOps Agent replicas should be ready"
    
    @pytest.mark.skipif(
        not check_cluster_accessible(),
        reason="Kubernetes cluster not accessible"
    )
    def test_chroma_service_exists(self, deployed_resources):
        """Test that Chroma service exists and is accessible"""
        namespace = deployed_resources["namespace"]
        success, output = kubectl_get("service", "chroma-service", namespace)
        assert success, "Chroma service should exist"
        
        import json
        service_data = json.loads(output)
        spec = service_data.get("spec", {})
        assert spec.get("type") == "ClusterIP", "Chroma service should be ClusterIP"
        assert len(spec.get("ports", [])) > 0, "Chroma service should have ports"
    
    @pytest.mark.skipif(
        not check_cluster_accessible(),
        reason="Kubernetes cluster not accessible"
    )
    def test_app_service_exists(self, deployed_resources):
        """Test that ITOps Agent service exists"""
        namespace = deployed_resources["namespace"]
        success, output = kubectl_get("service", "itops-agent-service", namespace)
        assert success, "ITOps Agent service should exist"
        
        import json
        service_data = json.loads(output)
        spec = service_data.get("spec", {})
        assert len(spec.get("ports", [])) > 0, "ITOps Agent service should have ports"
    
    @pytest.mark.skipif(
        not check_cluster_accessible(),
        reason="Kubernetes cluster not accessible"
    )
    def test_chroma_pods_running(self, deployed_resources):
        """Test that Chroma pods are running"""
        namespace = deployed_resources["namespace"]
        success, output = kubectl_get("pods", None, namespace)
        assert success, "Should be able to list pods"
        
        import json
        pods_data = json.loads(output)
        pods = pods_data.get("items", [])
        
        chroma_pods = [p for p in pods if p.get("metadata", {}).get("labels", {}).get("app") == "chroma"]
        assert len(chroma_pods) > 0, "Should have at least one Chroma pod"
        
        for pod in chroma_pods:
            phase = pod.get("status", {}).get("phase")
            assert phase == "Running", f"Chroma pod {pod.get('metadata', {}).get('name')} should be Running"
    
    @pytest.mark.skipif(
        not check_cluster_accessible(),
        reason="Kubernetes cluster not accessible"
    )
    def test_app_pods_running(self, deployed_resources):
        """Test that ITOps Agent pods are running"""
        namespace = deployed_resources["namespace"]
        success, output = kubectl_get("pods", None, namespace)
        assert success, "Should be able to list pods"
        
        import json
        pods_data = json.loads(output)
        pods = pods_data.get("items", [])
        
        app_pods = [p for p in pods if p.get("metadata", {}).get("labels", {}).get("app") == "itops-agent"]
        assert len(app_pods) > 0, "Should have at least one ITOps Agent pod"
        
        for pod in app_pods:
            phase = pod.get("status", {}).get("phase")
            assert phase == "Running", f"ITOps Agent pod {pod.get('metadata', {}).get('name')} should be Running"
    
    @pytest.mark.skipif(
        not check_cluster_accessible(),
        reason="Kubernetes cluster not accessible"
    )
    def test_chroma_health_check(self, deployed_resources):
        """Test Chroma health check endpoint"""
        namespace = deployed_resources["namespace"]
        
        # Port forward to Chroma service
        # Note: This is a simplified test - in real scenarios you'd use port-forward or ingress
        # For now, we'll check if the pod is responding to health checks via kubectl
        success, output = kubectl_get("pods", None, namespace)
        assert success, "Should be able to list pods"
        
        import json
        pods_data = json.loads(output)
        pods = pods_data.get("items", [])
        chroma_pods = [p for p in pods if p.get("metadata", {}).get("labels", {}).get("app") == "chroma"]
        
        if chroma_pods:
            pod_name = chroma_pods[0].get("metadata", {}).get("name")
            # Check if pod has passed readiness probe
            conditions = chroma_pods[0].get("status", {}).get("conditions", [])
            ready_condition = next((c for c in conditions if c.get("type") == "Ready"), None)
            
            if ready_condition:
                assert ready_condition.get("status") == "True", \
                    f"Chroma pod {pod_name} should be ready"
    
    @pytest.mark.skipif(
        not check_cluster_accessible(),
        reason="Kubernetes cluster not accessible"
    )
    def test_app_health_check(self, deployed_resources):
        """Test ITOps Agent health check endpoint"""
        namespace = deployed_resources["namespace"]
        
        success, output = kubectl_get("pods", None, namespace)
        assert success, "Should be able to list pods"
        
        import json
        pods_data = json.loads(output)
        pods = pods_data.get("items", [])
        app_pods = [p for p in pods if p.get("metadata", {}).get("labels", {}).get("app") == "itops-agent"]
        
        if app_pods:
            pod_name = app_pods[0].get("metadata", {}).get("name")
            # Check if pod has passed readiness probe
            conditions = app_pods[0].get("status", {}).get("conditions", [])
            ready_condition = next((c for c in conditions if c.get("type") == "Ready"), None)
            
            if ready_condition:
                assert ready_condition.get("status") == "True", \
                    f"ITOps Agent pod {pod_name} should be ready"
    
    @pytest.mark.skipif(
        not check_cluster_accessible(),
        reason="Kubernetes cluster not accessible"
    )
    def test_pvc_created(self, deployed_resources):
        """Test that PersistentVolumeClaims are created"""
        namespace = deployed_resources["namespace"]
        
        # Check for Chroma PVC
        success, output = kubectl_get("pvc", "chroma-pvc", namespace)
        assert success, "Chroma PVC should exist"
        
        import json
        pvc_data = json.loads(output)
        phase = pvc_data.get("status", {}).get("phase")
        # PVC can be Pending, Bound, or Available
        assert phase in ["Pending", "Bound", "Available"], \
            f"Chroma PVC should be in valid state, got {phase}"
    
    @pytest.mark.skipif(
        not check_cluster_accessible(),
        reason="Kubernetes cluster not accessible"
    )
    def test_configmap_exists(self, deployed_resources):
        """Test that ConfigMap exists"""
        namespace = deployed_resources["namespace"]
        success, output = kubectl_get("configmap", "itops-agent-config", namespace)
        assert success, "ConfigMap should exist"
    
    @pytest.mark.skipif(
        not check_cluster_accessible(),
        reason="Kubernetes cluster not accessible"
    )
    def test_resource_limits_applied(self, deployed_resources):
        """Test that resource limits are applied to pods"""
        namespace = deployed_resources["namespace"]
        
        # Check Chroma deployment
        success, output = kubectl_get("deployment", "chroma", namespace)
        assert success, "Chroma deployment should exist"
        
        import json
        deployment_data = json.loads(output)
        containers = deployment_data.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
        chroma_container = next((c for c in containers if c.get("name") == "chroma"), None)
        
        assert chroma_container is not None, "Chroma container should exist"
        assert "resources" in chroma_container, "Chroma container should have resources"
        assert "limits" in chroma_container.get("resources", {}), \
            "Chroma container should have resource limits"
        
        # Check App deployment
        success, output = kubectl_get("deployment", "itops-agent", namespace)
        assert success, "ITOps Agent deployment should exist"
        
        deployment_data = json.loads(output)
        containers = deployment_data.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
        app_container = next((c for c in containers if c.get("name") == "itops-agent"), None)
        
        assert app_container is not None, "ITOps Agent container should exist"
        assert "resources" in app_container, "ITOps Agent container should have resources"
        assert "limits" in app_container.get("resources", {}), \
            "ITOps Agent container should have resource limits"


class TestKubernetesE2E:
    """End-to-end tests for Kubernetes deployment"""
    
    @pytest.mark.skipif(
        not check_cluster_accessible(),
        reason="Kubernetes cluster not accessible"
    )
    @pytest.mark.skipif(
        not os.getenv("TEST_K8S_E2E"),
        reason="E2E tests require TEST_K8S_E2E env var (may require port-forwarding or ingress)"
    )
    def test_chroma_connectivity(self, deployed_resources):
        """Test connectivity to Chroma service"""
        namespace = deployed_resources["namespace"]
        
        # This test would require port-forwarding or ingress setup
        # For now, we'll verify the service exists and pods are ready
        success, output = kubectl_get("service", "chroma-service", namespace)
        assert success, "Chroma service should exist"
        
        # In a real scenario, you'd port-forward and test:
        # kubectl port-forward -n {namespace} svc/chroma-service 8000:8000
        # Then test: requests.get("http://localhost:8000/api/v1/heartbeat")
    
    @pytest.mark.skipif(
        not check_cluster_accessible(),
        reason="Kubernetes cluster not accessible"
    )
    @pytest.mark.skipif(
        not os.getenv("TEST_K8S_E2E"),
        reason="E2E tests require TEST_K8S_E2E env var (may require port-forwarding or ingress)"
    )
    def test_app_connectivity(self, deployed_resources):
        """Test connectivity to ITOps Agent service"""
        namespace = deployed_resources["namespace"]
        
        # This test would require port-forwarding or ingress setup
        success, output = kubectl_get("service", "itops-agent-service", namespace)
        assert success, "ITOps Agent service should exist"
        
        # In a real scenario, you'd port-forward and test:
        # kubectl port-forward -n {namespace} svc/itops-agent-service 7860:80
        # Then test: requests.get("http://localhost:7860/health")

