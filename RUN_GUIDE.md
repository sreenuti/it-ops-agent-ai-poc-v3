# How to Run the IT Ops Agent System

This guide provides detailed, step-by-step instructions for running the IT Ops Agent System in different environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Method 1: Local Development](#method-1-local-development)
- [Method 2: Docker Deployment](#method-2-docker-deployment)
- [Method 3: Kubernetes Deployment](#method-3-kubernetes-deployment)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## Prerequisites

### Required Software

1. **Python 3.10 or higher**
   ```bash
   # Check Python version
   python --version
   # or
   python3 --version
   ```

2. **pip** (Python package manager)
   ```bash
   pip --version
   ```

3. **Git** (to clone the repository)
   ```bash
   git --version
   ```

4. **OpenAI API Key**
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Get your API key from [API Keys page](https://platform.openai.com/api-keys)
   - Save it securely - you'll need it for configuration

### Optional Software (depending on deployment method)

- **Docker** & **Docker Compose** - For containerized deployment
  ```bash
  docker --version
  docker-compose --version
  ```

- **kubectl** - For Kubernetes deployment
  ```bash
  kubectl version --client
  ```

- **Kubernetes cluster** - minikube, kind, or cloud cluster

---

## Quick Start

For the fastest setup, follow these steps:

```bash
# 1. Clone repository
git clone <repository-url>
cd "ITOps PoC v3"

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file with your OpenAI API key
echo OPENAI_API_KEY=your_key_here > .env

# 6. Start Chroma DB (using Docker)
cd docker
docker-compose up -d chroma
cd ..

# 7. Load sample instructions
python scripts/load_instructions.py

# 8. Start the application
python -m src.api.gradio_app
```

Then open `http://localhost:7860` in your browser!

---

## Method 1: Local Development

This method runs the application directly on your machine with all services.

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>

# Navigate to project directory
cd "ITOps PoC v3"

# Verify you're in the right directory (should see src/, tests/, etc.)
ls
```

### Step 2: Set Up Python Virtual Environment

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (prompt should show (venv))
```

**Linux/Mac:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (prompt should show (venv))
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Verify installation (check for key packages)
pip list | grep -E "(openai|langchain|gradio|chromadb)"
```

**Expected output:** Should list installed packages without errors.

### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory:

**Windows (PowerShell):**
```powershell
# Create .env file
@"
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_HOST=localhost
CHROMA_PORT=8000
AGENT_FRAMEWORK=langchain
LOG_LEVEL=INFO
"@ | Out-File -FilePath .env -Encoding utf8
```

**Linux/Mac/Windows (Command Prompt):**
```bash
# Create .env file manually or use:
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_HOST=localhost
CHROMA_PORT=8000
AGENT_FRAMEWORK=langchain
LOG_LEVEL=INFO
EOF
```

**Manual Creation:**
1. Create a new file named `.env` in the project root
2. Add the following content (replace `your_openai_api_key_here` with your actual key):

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (defaults provided)
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_COLLECTION_NAME=itops_instructions
AGENT_FRAMEWORK=langchain
OPENAI_MODEL=gpt-4
LOG_LEVEL=INFO
APP_HOST=0.0.0.0
APP_PORT=7860
```

**Important:** 
- Never commit the `.env` file to git (it's already in `.gitignore`)
- Keep your API key secure
- For production, use environment variables or secrets management

### Step 5: Start Chroma Database

You have two options for running Chroma:

#### Option A: Using Docker Compose (Recommended)

```bash
# Navigate to docker directory
cd docker

# Start Chroma service in detached mode
docker-compose up -d chroma

# Verify Chroma is running
docker-compose ps

# Check logs
docker-compose logs chroma

# Return to project root
cd ..
```

**Expected:** Chroma should start and be accessible on port 8000.

#### Option B: Using Docker Run

```bash
# Run Chroma container
docker run -d \
  --name itops-chroma \
  -p 8000:8000 \
  -v chroma_data:/chroma/chroma \
  -e IS_PERSISTENT=TRUE \
  -e PERSIST_DIRECTORY=/chroma/chroma \
  chromadb/chroma:latest

# Verify container is running
docker ps | grep chroma
```

#### Option C: Install Chroma Locally (Advanced)

```bash
# Install Chroma client (already in requirements.txt)
# Chroma will run in embedded mode
# No additional setup needed - uses local file storage
```

**Note:** For local development, Docker is recommended as it's easier to manage.

### Step 6: Verify Chroma is Running

```bash
# Test Chroma connection (should return heartbeat)
curl http://localhost:8000/api/v1/heartbeat

# Or test in Python
python -c "import requests; print(requests.get('http://localhost:8000/api/v1/heartbeat').json())"
```

**Expected:** Should return a heartbeat response.

### Step 7: Load Sample Instructions

The system comes with pre-built instruction files for common IT ops tasks. Load them into the database:

```bash
# Load all instruction files from data/instructions/
python scripts/load_instructions.py
```

**Expected output:**
```
IT Ops Agent - Instruction Loader
==================================================
Found 23 instruction file(s) to load...

✓ Loaded instruction: password_reset (ID: ...)
✓ Loaded instruction: vpn_troubleshooting (ID: ...)
...
==================================================
Loaded 23/23 instruction(s) successfully
==================================================
```

**Troubleshooting:**
- If you see connection errors, ensure Chroma is running (Step 5)
- If no files found, verify `data/instructions/` directory exists
- Check that JSON files are valid format

### Step 8: Verify Setup (Optional but Recommended)

Run tests to ensure everything is configured correctly:

```bash
# Run configuration tests
pytest tests/test_config.py -v

# Run vector database tests
pytest tests/test_vector_db.py -v

# Quick smoke test
pytest tests/test_project_setup.py -v
```

### Step 9: Start the Application

```bash
# Start the Gradio interface
python -m src.api.gradio_app
```

**Expected output:**
```
Running on local URL:  http://127.0.0.1:7860
Running on public URL: ...

To create a public link, set `share=True` in `launch()`.
```

### Step 10: Access the Application

1. Open your web browser
2. Navigate to: `http://localhost:7860`
3. You should see the IT Ops Agent chat interface

### Step 11: Test the Application

Try these sample queries:

1. **Password Reset:**
   ```
   Reset password for user john.doe in AWS IAM
   ```

2. **VPN Troubleshooting:**
   ```
   Troubleshoot VPN connection issues
   ```

3. **Account Unlock:**
   ```
   Unlock account for user jane.smith
   ```

**Tips:**
- Start with **Dry Run Mode** enabled to see commands without executing
- Check the console/terminal for detailed logs
- Review the generated commands before executing

### Step 12: Verify Health Endpoints

Open a new terminal and test the health endpoints:

```bash
# Health check
curl http://localhost:7860/health

# Expected: {"status": "healthy"}

# Metrics (JSON format)
curl http://localhost:7860/metrics/json

# Metrics (Prometheus format)
curl http://localhost:7860/metrics
```

---

## Method 2: Docker Deployment

This method runs everything in Docker containers - easier to manage and more production-like.

### Step 1: Prerequisites

Ensure Docker and Docker Compose are installed:

```bash
# Check Docker
docker --version

# Check Docker Compose
docker-compose --version
```

### Step 2: Clone Repository

```bash
git clone <repository-url>
cd "ITOps PoC v3"
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root (same as Method 1, Step 4):

```env
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_COLLECTION_NAME=itops_instructions
AGENT_FRAMEWORK=langchain
OPENAI_MODEL=gpt-4
LOG_LEVEL=INFO
```

**Note:** In Docker Compose, Chroma host is `chroma` (service name), not `localhost`.

### Step 4: Build Docker Images

```bash
# Navigate to docker directory
cd docker

# Build the application image
docker-compose build app

# This may take a few minutes the first time
```

**Expected:** Should complete without errors.

### Step 5: Start All Services

```bash
# Start both Chroma and App services
docker-compose up -d

# Check status
docker-compose ps
```

**Expected output:**
```
NAME           STATUS          PORTS
itops-chroma   Up (healthy)    0.0.0.0:8000->8000/tcp
itops-agent    Up (healthy)    0.0.0.0:7860->7860/tcp
```

### Step 6: Check Logs

```bash
# View all logs
docker-compose logs

# Follow app logs
docker-compose logs -f app

# Follow Chroma logs
docker-compose logs -f chroma

# Check specific service
docker-compose logs app | tail -50
```

### Step 7: Load Sample Instructions

```bash
# Execute the load script inside the app container
docker-compose exec app python scripts/load_instructions.py
```

**Expected:** Should load all instruction files successfully.

### Step 8: Access the Application

Open browser to: `http://localhost:7860`

### Step 9: Verify Services

```bash
# Check container health
docker-compose ps

# Test health endpoint
curl http://localhost:7860/health

# Test Chroma connection from host
curl http://localhost:8000/api/v1/heartbeat
```

### Step 10: Stop Services

```bash
# Stop services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove containers, and remove volumes
docker-compose down -v
```

**Warning:** Using `-v` will delete all data including loaded instructions!

### Step 11: Update and Redeploy

```bash
# After making code changes, rebuild
docker-compose build app

# Restart services
docker-compose up -d

# Or rebuild and restart in one command
docker-compose up -d --build app
```

---

## Method 3: Kubernetes Deployment

This method deploys to a Kubernetes cluster - best for production environments.

### Prerequisites

- Kubernetes cluster (minikube, kind, or cloud cluster)
- kubectl configured and connected
- Access to create namespaces, deployments, services

### Step 1: Verify Cluster Access

```bash
# Check cluster connection
kubectl cluster-info

# Check nodes
kubectl get nodes

# Current context
kubectl config current-context
```

### Step 2: Clone Repository

```bash
git clone <repository-url>
cd "ITOps PoC v3"
```

### Step 3: Create Namespace

```bash
# Apply namespace
kubectl apply -f k8s/namespace.yaml

# Verify
kubectl get namespace itops-agent
```

### Step 4: Create Secrets

```bash
# Copy template
cp k8s/secret.yaml.template k8s/secret.yaml

# Edit secret.yaml and add your values:
# - OPENAI_API_KEY
# - AWS credentials (if needed)
# - Other sensitive values

# Apply secret
kubectl apply -f k8s/secret.yaml

# Verify (should show as Opaque)
kubectl get secret -n itops-agent
```

**Important:** Never commit `secret.yaml` to git (use `.gitignore`).

### Step 5: Create ConfigMap

```bash
# Apply ConfigMap
kubectl apply -f k8s/configmap.yaml

# Verify
kubectl get configmap -n itops-agent
kubectl describe configmap itops-config -n itops-agent
```

### Step 6: Create Persistent Volume

```bash
# Apply PVC
kubectl apply -f k8s/persistentvolumeclaim.yaml

# Verify
kubectl get pvc -n itops-agent

# Wait for binding
kubectl wait --for=condition=Bound pvc/chroma-data -n itops-agent --timeout=60s
```

### Step 7: Deploy Chroma Database

```bash
# Deploy Chroma
kubectl apply -f k8s/chroma-deployment.yaml
kubectl apply -f k8s/chroma-service.yaml

# Wait for deployment to be ready
kubectl wait --for=condition=available --timeout=300s \
  deployment/chroma -n itops-agent

# Check pods
kubectl get pods -n itops-agent -l app=chroma

# Check logs
kubectl logs -n itops-agent -l app=chroma --tail=50
```

### Step 8: Deploy Application

```bash
# Deploy application
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/app-service.yaml

# Wait for deployment
kubectl wait --for=condition=available --timeout=300s \
  deployment/itops-agent -n itops-agent

# Check pods
kubectl get pods -n itops-agent

# Check logs
kubectl logs -n itops-agent -l app=itops-agent --tail=50
```

### Step 9: Verify Deployment

```bash
# Check all resources
kubectl get all -n itops-agent

# Check services
kubectl get svc -n itops-agent

# Check deployments
kubectl get deployments -n itops-agent

# Describe deployment
kubectl describe deployment itops-agent -n itops-agent
```

### Step 10: Access the Application

**Option A: Port Forward (for testing)**

```bash
# Port forward to access locally
kubectl port-forward svc/itops-agent-service 7860:80 -n itops-agent

# In another terminal, test
curl http://localhost:7860/health
```

**Option B: Load Balancer (production)**

If using a cloud provider with LoadBalancer:

```bash
# Get external IP
kubectl get svc itops-agent-service -n itops-agent

# Access via external IP
curl http://<EXTERNAL_IP>/health
```

**Option C: Ingress (recommended for production)**

Configure an Ingress resource to expose the service with a domain name.

### Step 11: Load Sample Instructions

```bash
# Execute load script in app pod
kubectl exec -it -n itops-agent deployment/itops-agent -- \
  python scripts/load_instructions.py

# Or use pod name
POD_NAME=$(kubectl get pods -n itops-agent -l app=itops-agent -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it -n itops-agent $POD_NAME -- python scripts/load_instructions.py
```

### Step 12: Configure Horizontal Pod Autoscaling (Optional)

```bash
# Apply HPA
kubectl apply -f k8s/hpa.yaml

# Check HPA status
kubectl get hpa -n itops-agent

# Monitor scaling
kubectl get hpa -n itops-agent -w
```

### Step 13: Monitor and Maintain

```bash
# Watch pods
kubectl get pods -n itops-agent -w

# View logs
kubectl logs -f -n itops-agent -l app=itops-agent

# Check events
kubectl get events -n itops-agent --sort-by='.lastTimestamp'

# Describe pod for troubleshooting
kubectl describe pod <pod-name> -n itops-agent
```

### Step 14: Update Deployment

```bash
# Update image (if using image registry)
kubectl set image deployment/itops-agent \
  itops-agent=your-registry/itops-agent:v2 -n itops-agent

# Or apply updated manifests
kubectl apply -f k8s/app-deployment.yaml

# Watch rollout
kubectl rollout status deployment/itops-agent -n itops-agent

# Rollback if needed
kubectl rollout undo deployment/itops-agent -n itops-agent
```

### Step 15: Clean Up (when done)

```bash
# Delete all resources
kubectl delete -f k8s/

# Or delete namespace (removes everything)
kubectl delete namespace itops-agent
```

---

## Verification

### 1. Health Check

```bash
# Local/Docker
curl http://localhost:7860/health

# Kubernetes (via port-forward)
curl http://localhost:7860/health

# Expected: {"status": "healthy"}
```

### 2. Metrics Endpoint

```bash
# JSON metrics
curl http://localhost:7860/metrics/json

# Prometheus metrics
curl http://localhost:7860/metrics
```

### 3. Database Connection

```bash
# Check Chroma is accessible
curl http://localhost:8000/api/v1/heartbeat

# Or from application logs
# Should see successful Chroma connection messages
```

### 4. Test Queries

Try these queries in the Gradio interface:

1. **Simple query:**
   ```
   Reset password for user test@example.com
   ```

2. **Complex query:**
   ```
   Troubleshoot VPN connection issues for remote user
   ```

3. **Follow-up query (tests conversation context):**
   ```
   What commands would that generate?
   ```

### 5. Check Logs

**Local:**
```bash
# Application logs
tail -f logs/itops_agent.log

# Or console output if running directly
```

**Docker:**
```bash
docker-compose logs -f app
```

**Kubernetes:**
```bash
kubectl logs -f -n itops-agent -l app=itops-agent
```

---

## Troubleshooting

### Common Issues

#### 1. "Module not found" or Import Errors

**Solution:**
```bash
# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 2. "Cannot connect to Chroma" Error

**Solution:**
```bash
# Check Chroma is running
docker ps | grep chroma

# Or
curl http://localhost:8000/api/v1/heartbeat

# Restart Chroma if needed
cd docker && docker-compose restart chroma
```

#### 3. "OpenAI API key not found" Error

**Solution:**
```bash
# Verify .env file exists and has OPENAI_API_KEY
cat .env | grep OPENAI_API_KEY

# Or set environment variable directly
export OPENAI_API_KEY=your_key_here  # Linux/Mac
set OPENAI_API_KEY=your_key_here     # Windows CMD
$env:OPENAI_API_KEY="your_key_here"  # Windows PowerShell
```

#### 4. Port Already in Use

**Solution:**
```bash
# Find process using port 7860
# Windows:
netstat -ano | findstr :7860

# Linux/Mac:
lsof -i :7860

# Kill the process or change port in .env:
# APP_PORT=7861
```

#### 5. Docker Build Fails

**Solution:**
```bash
# Check Dockerfile syntax
docker build --no-cache -t test -f docker/Dockerfile .

# Check for sufficient disk space
docker system df

# Clean up if needed
docker system prune -a
```

#### 6. Kubernetes Pods Not Starting

**Solution:**
```bash
# Check pod status
kubectl get pods -n itops-agent

# Describe pod for errors
kubectl describe pod <pod-name> -n itops-agent

# Check logs
kubectl logs <pod-name> -n itops-agent

# Check events
kubectl get events -n itops-agent --sort-by='.lastTimestamp'
```

#### 7. Instructions Not Loading

**Solution:**
```bash
# Verify instruction files exist
ls data/instructions/*.json

# Check JSON syntax
python -m json.tool data/instructions/password_reset.json

# Retry loading
python scripts/load_instructions.py

# Check Chroma connection
python -c "from src.vector_db.chroma_client import ChromaClient; print(ChromaClient().test_connection())"
```

#### 8. Gradio Interface Not Loading

**Solution:**
```bash
# Check application is running
# Should see "Running on local URL" message

# Check firewall settings
# Ensure port 7860 is accessible

# Try accessing via 127.0.0.1 instead of localhost
# http://127.0.0.1:7860

# Check browser console for errors (F12)
```

### Debug Mode

Enable debug logging:

```env
# In .env file
LOG_LEVEL=DEBUG
DEBUG=true
```

Or set environment variable:
```bash
export LOG_LEVEL=DEBUG  # Linux/Mac
set LOG_LEVEL=DEBUG     # Windows
```

### Getting Help

1. Check logs for detailed error messages
2. Review `TESTING.md` for test procedures
3. Check `ARCHITECTURE.md` for system design
4. Review GitHub issues (if available)
5. Check component-specific documentation

---

## Next Steps

After successfully running the project:

1. **Explore the UI:**
   - Try different IT ops queries
   - Test dry-run mode
   - Explore conversation context

2. **Review Documentation:**
   - [TESTING.md](TESTING.md) - Comprehensive testing guide
   - [USER_GUIDE.md](USER_GUIDE.md) - Usage examples
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
   - [API_REFERENCE.md](API_REFERENCE.md) - API documentation

3. **Customize:**
   - Add your own instruction files to `data/instructions/`
   - Configure different agent frameworks
   - Adjust logging and monitoring

4. **Develop:**
   - Run the test suite: `pytest`
   - Make code changes
   - Add new features

5. **Deploy:**
   - Set up production environment
   - Configure monitoring and alerts
   - Set up backup procedures

---

## Quick Reference Commands

### Local Development

```bash
# Start Chroma
cd docker && docker-compose up -d chroma && cd ..

# Load instructions
python scripts/load_instructions.py

# Run app
python -m src.api.gradio_app

# Run tests
pytest
```

### Docker

```bash
# Start all services
cd docker && docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Kubernetes

```bash
# Deploy everything
kubectl apply -f k8s/

# Port forward
kubectl port-forward svc/itops-agent-service 7860:80 -n itops-agent

# View logs
kubectl logs -f -n itops-agent -l app=itops-agent
```

---

**Happy Running! 🚀**

For questions or issues, refer to the troubleshooting section or check the project documentation.

