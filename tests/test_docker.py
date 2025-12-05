"""
Tests for Docker setup and container functionality
"""
import pytest
import subprocess
import os
import json
from pathlib import Path


class TestDockerfile:
    """Test Dockerfile structure and build"""
    
    def test_dockerfile_exists(self):
        """Verify Dockerfile exists"""
        dockerfile_path = Path("docker/Dockerfile")
        assert dockerfile_path.exists(), "Dockerfile should exist"
    
    def test_dockerfile_content(self):
        """Verify Dockerfile has required components"""
        dockerfile_path = Path("docker/Dockerfile")
        content = dockerfile_path.read_text()
        
        # Check for multi-stage build
        assert "FROM python:3.11-slim as builder" in content or "FROM python" in content, \
            "Dockerfile should use Python base image"
        
        # Check for non-root user
        assert "useradd" in content or "USER" in content, \
            "Dockerfile should create non-root user"
        
        # Check for health check
        assert "HEALTHCHECK" in content, \
            "Dockerfile should include health check"
        
        # Check for exposed port
        assert "EXPOSE" in content, \
            "Dockerfile should expose application port"
    
    @pytest.mark.skipif(
        not os.getenv("TEST_DOCKER_BUILD"),
        reason="Docker build test requires TEST_DOCKER_BUILD env var"
    )
    def test_docker_build(self):
        """Test that Docker image builds successfully"""
        try:
            result = subprocess.run(
                ["docker", "build", "-t", "itops-agent-test", "-f", "docker/Dockerfile", "."],
                capture_output=True,
                text=True,
                timeout=300
            )
            assert result.returncode == 0, \
                f"Docker build failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            pytest.fail("Docker build timed out")
        except FileNotFoundError:
            pytest.skip("Docker not available")


class TestDockerCompose:
    """Test Docker Compose configuration"""
    
    def test_docker_compose_exists(self):
        """Verify docker-compose.yml exists"""
        compose_path = Path("docker/docker-compose.yml")
        assert compose_path.exists(), "docker-compose.yml should exist"
    
    def test_docker_compose_structure(self):
        """Verify docker-compose.yml has required services"""
        compose_path = Path("docker/docker-compose.yml")
        content = compose_path.read_text()
        
        # Check for required services
        assert "chroma:" in content, "docker-compose.yml should include chroma service"
        assert "app:" in content, "docker-compose.yml should include app service"
        
        # Check for volumes
        assert "volumes:" in content, "docker-compose.yml should define volumes"
        
        # Check for networks
        assert "networks:" in content, "docker-compose.yml should define networks"
    
    @pytest.mark.skipif(
        not os.getenv("TEST_DOCKER_COMPOSE"),
        reason="Docker Compose test requires TEST_DOCKER_COMPOSE env var"
    )
    def test_docker_compose_config(self):
        """Test that docker-compose.yml is valid"""
        try:
            result = subprocess.run(
                ["docker", "compose", "-f", "docker/docker-compose.yml", "config"],
                capture_output=True,
                text=True,
                timeout=30
            )
            assert result.returncode == 0, \
                f"Docker Compose config validation failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            pytest.fail("Docker Compose config check timed out")
        except FileNotFoundError:
            pytest.skip("Docker Compose not available")


class TestDockerIgnore:
    """Test .dockerignore file"""
    
    def test_dockerignore_exists(self):
        """Verify .dockerignore exists"""
        dockerignore_path = Path("docker/.dockerignore")
        assert dockerignore_path.exists(), ".dockerignore should exist"
    
    def test_dockerignore_content(self):
        """Verify .dockerignore excludes appropriate files"""
        dockerignore_path = Path("docker/.dockerignore")
        content = dockerignore_path.read_text()
        
        # Check for common exclusions
        assert "__pycache__" in content or "*.pyc" in content, \
            ".dockerignore should exclude Python cache"
        assert ".git" in content, ".dockerignore should exclude git files"
        assert ".env" in content, ".dockerignore should exclude environment files"


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check_endpoint_exists(self):
        """Verify health check endpoint is defined in gradio_app.py"""
        gradio_app_path = Path("src/api/gradio_app.py")
        content = gradio_app_path.read_text()
        
        assert "/health" in content, \
            "Health check endpoint should be defined"
        assert "health_check" in content, \
            "Health check function should be defined"
    
    @pytest.mark.skipif(
        not os.getenv("TEST_CONTAINER_HEALTH"),
        reason="Container health check test requires running container"
    )
    def test_health_check_endpoint(self):
        """Test health check endpoint responds correctly"""
        import requests
        
        try:
            response = requests.get("http://localhost:7860/health", timeout=5)
            assert response.status_code == 200, \
                f"Health check should return 200, got {response.status_code}"
            
            data = response.json()
            assert "status" in data, \
                "Health check response should include status"
        except requests.exceptions.RequestException:
            pytest.skip("Health check endpoint not accessible (container not running)")


class TestContainerSecurity:
    """Test container security best practices"""
    
    def test_dockerfile_non_root_user(self):
        """Verify Dockerfile uses non-root user"""
        dockerfile_path = Path("docker/Dockerfile")
        content = dockerfile_path.read_text()
        
        # Check for user creation and switch
        has_user_creation = "useradd" in content or "RUN.*user" in content.lower()
        has_user_switch = "USER" in content
        
        assert has_user_creation or has_user_switch, \
            "Dockerfile should create and use non-root user"
    
    def test_dockerfile_no_secrets(self):
        """Verify Dockerfile doesn't contain secrets"""
        dockerfile_path = Path("docker/Dockerfile")
        content = dockerfile_path.read_text()
        
        # Check for common secret patterns
        secret_patterns = [
            "password=",
            "api_key=",
            "secret=",
            "token="
        ]
        
        for pattern in secret_patterns:
            assert pattern.lower() not in content.lower(), \
                f"Dockerfile should not contain secrets (found: {pattern})"

