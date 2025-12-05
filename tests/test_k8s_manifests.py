"""
Tests for Kubernetes manifest validation
"""
import pytest
import yaml
from pathlib import Path
import subprocess
import os


class TestKubernetesManifests:
    """Test Kubernetes manifest files"""
    
    @pytest.fixture
    def manifest_files(self):
        """List of Kubernetes manifest files to test"""
        return [
            "k8s/namespace.yaml",
            "k8s/configmap.yaml",
            "k8s/secret.yaml.template",
            "k8s/persistentvolumeclaim.yaml",
            "k8s/chroma-deployment.yaml",
            "k8s/chroma-service.yaml",
            "k8s/app-deployment.yaml",
            "k8s/app-service.yaml",
            "k8s/hpa.yaml"
        ]
    
    def test_manifest_files_exist(self, manifest_files):
        """Verify all manifest files exist"""
        for manifest_file in manifest_files:
            path = Path(manifest_file)
            assert path.exists(), f"Manifest file {manifest_file} should exist"
    
    def test_yaml_syntax(self, manifest_files):
        """Test that all YAML files have valid syntax"""
        for manifest_file in manifest_files:
            path = Path(manifest_file)
            if not path.exists():
                continue
                
            try:
                with open(path, 'r') as f:
                    yaml.safe_load_all(f)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML syntax in {manifest_file}: {e}")
    
    def test_namespace_manifest(self):
        """Test namespace manifest structure"""
        namespace_path = Path("k8s/namespace.yaml")
        if not namespace_path.exists():
            pytest.skip("Namespace manifest not found")
        
        with open(namespace_path, 'r') as f:
            manifest = yaml.safe_load(f)
        
        assert manifest['kind'] == 'Namespace', \
            "Namespace manifest should be of kind Namespace"
        assert 'metadata' in manifest, \
            "Namespace manifest should have metadata"
        assert manifest['metadata']['name'] == 'itops-agent', \
            "Namespace should be named itops-agent"
    
    def test_configmap_manifest(self):
        """Test ConfigMap manifest structure"""
        configmap_path = Path("k8s/configmap.yaml")
        if not configmap_path.exists():
            pytest.skip("ConfigMap manifest not found")
        
        with open(configmap_path, 'r') as f:
            manifest = yaml.safe_load(f)
        
        assert manifest['kind'] == 'ConfigMap', \
            "ConfigMap manifest should be of kind ConfigMap"
        assert 'data' in manifest, \
            "ConfigMap should have data section"
        assert manifest['metadata']['namespace'] == 'itops-agent', \
            "ConfigMap should be in itops-agent namespace"
    
    def test_secret_template(self):
        """Test secret template structure"""
        secret_path = Path("k8s/secret.yaml.template")
        if not secret_path.exists():
            pytest.skip("Secret template not found")
        
        with open(secret_path, 'r') as f:
            content = f.read()
            # Split by --- to handle multiple documents
            documents = yaml.safe_load_all(content)
            manifest = next(documents, None)
        
        if manifest:
            assert manifest['kind'] == 'Secret', \
                "Secret template should be of kind Secret"
            assert manifest['type'] == 'Opaque', \
                "Secret should be of type Opaque"
    
    def test_deployment_manifests(self):
        """Test deployment manifest structure"""
        deployment_files = [
            "k8s/chroma-deployment.yaml",
            "k8s/app-deployment.yaml"
        ]
        
        for deployment_file in deployment_files:
            path = Path(deployment_file)
            if not path.exists():
                continue
            
            with open(path, 'r') as f:
                manifest = yaml.safe_load(f)
            
            assert manifest['kind'] == 'Deployment', \
                f"{deployment_file} should be of kind Deployment"
            assert 'spec' in manifest, \
                f"{deployment_file} should have spec section"
            assert 'template' in manifest['spec'], \
                f"{deployment_file} should have template in spec"
            assert 'containers' in manifest['spec']['template']['spec'], \
                f"{deployment_file} should have containers"
    
    def test_service_manifests(self):
        """Test service manifest structure"""
        service_files = [
            "k8s/chroma-service.yaml",
            "k8s/app-service.yaml"
        ]
        
        for service_file in service_files:
            path = Path(service_file)
            if not path.exists():
                continue
            
            with open(path, 'r') as f:
                manifest = yaml.safe_load(f)
            
            assert manifest['kind'] == 'Service', \
                f"{service_file} should be of kind Service"
            assert 'spec' in manifest, \
                f"{service_file} should have spec section"
            assert 'ports' in manifest['spec'], \
                f"{service_file} should have ports"
            assert 'selector' in manifest['spec'], \
                f"{service_file} should have selector"
    
    def test_pvc_manifest(self):
        """Test PersistentVolumeClaim manifest structure"""
        pvc_path = Path("k8s/persistentvolumeclaim.yaml")
        if not pvc_path.exists():
            pytest.skip("PVC manifest not found")
        
        with open(pvc_path, 'r') as f:
            documents = list(yaml.safe_load_all(f))
        
        assert len(documents) > 0, \
            "PVC manifest should contain at least one resource"
        
        for manifest in documents:
            assert manifest['kind'] == 'PersistentVolumeClaim', \
                "All resources in PVC manifest should be PersistentVolumeClaim"
            assert 'spec' in manifest, \
                "PVC should have spec section"
            assert 'resources' in manifest['spec'], \
                "PVC should have resources"
    
    def test_hpa_manifest(self):
        """Test HorizontalPodAutoscaler manifest structure"""
        hpa_path = Path("k8s/hpa.yaml")
        if not hpa_path.exists():
            pytest.skip("HPA manifest not found")
        
        with open(hpa_path, 'r') as f:
            manifest = yaml.safe_load(f)
        
        assert manifest['kind'] == 'HorizontalPodAutoscaler', \
            "HPA manifest should be of kind HorizontalPodAutoscaler"
        assert 'spec' in manifest, \
            "HPA should have spec section"
        assert 'scaleTargetRef' in manifest['spec'], \
            "HPA should have scaleTargetRef"
        assert 'minReplicas' in manifest['spec'], \
            "HPA should have minReplicas"
        assert 'maxReplicas' in manifest['spec'], \
            "HPA should have maxReplicas"
    
    @pytest.mark.skipif(
        not os.getenv("TEST_KUBECTL_VALIDATE"),
        reason="kubectl validation requires TEST_KUBECTL_VALIDATE env var and kubectl"
    )
    def test_kubectl_validate(self, manifest_files):
        """Test manifests using kubectl validate (if available)"""
        for manifest_file in manifest_files:
            path = Path(manifest_file)
            if not path.exists():
                continue
            
            try:
                result = subprocess.run(
                    ["kubectl", "apply", "--dry-run=client", "-f", str(path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                # Note: kubectl may return non-zero for warnings, so we check stderr
                if result.returncode != 0 and "error" in result.stderr.lower():
                    pytest.fail(
                        f"kubectl validation failed for {manifest_file}: {result.stderr}"
                    )
            except subprocess.TimeoutExpired:
                pytest.fail(f"kubectl validation timed out for {manifest_file}")
            except FileNotFoundError:
                pytest.skip("kubectl not available")


class TestKubernetesSecurity:
    """Test Kubernetes security best practices"""
    
    def test_no_secrets_in_manifests(self):
        """Verify no actual secrets are in manifest files"""
        manifest_files = [
            "k8s/configmap.yaml",
            "k8s/app-deployment.yaml",
            "k8s/chroma-deployment.yaml"
        ]
        
        secret_patterns = [
            "password",
            "api_key",
            "secret",
            "token"
        ]
        
        for manifest_file in manifest_files:
            path = Path(manifest_file)
            if not path.exists():
                continue
            
            with open(path, 'r') as f:
                content = f.read().lower()
            
            # Check that we're not storing actual secrets (only placeholders)
            for pattern in secret_patterns:
                if pattern in content:
                    # Allow placeholders but not actual values
                    assert "your_" in content or "placeholder" in content or "template" in manifest_file, \
                        f"Potential secret found in {manifest_file} (check for {pattern})"
    
    def test_resource_limits_defined(self):
        """Verify resource limits are defined in deployments"""
        deployment_files = [
            "k8s/chroma-deployment.yaml",
            "k8s/app-deployment.yaml"
        ]
        
        for deployment_file in deployment_files:
            path = Path(deployment_file)
            if not path.exists():
                continue
            
            with open(path, 'r') as f:
                manifest = yaml.safe_load(f)
            
            containers = manifest.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
            assert len(containers) > 0, \
                f"{deployment_file} should have containers"
            
            for container in containers:
                assert 'resources' in container, \
                    f"Container {container.get('name')} in {deployment_file} should have resources"
                if 'resources' in container:
                    assert 'limits' in container['resources'] or 'requests' in container['resources'], \
                        f"Container {container.get('name')} should have resource limits or requests"
    
    def test_health_checks_defined(self):
        """Verify health checks are defined in deployments"""
        deployment_files = [
            "k8s/chroma-deployment.yaml",
            "k8s/app-deployment.yaml"
        ]
        
        for deployment_file in deployment_files:
            path = Path(deployment_file)
            if not path.exists():
                continue
            
            with open(path, 'r') as f:
                manifest = yaml.safe_load(f)
            
            containers = manifest.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
            
            for container in containers:
                has_liveness = 'livenessProbe' in container
                has_readiness = 'readinessProbe' in container
                
                assert has_liveness or has_readiness, \
                    f"Container {container.get('name')} should have health checks"

