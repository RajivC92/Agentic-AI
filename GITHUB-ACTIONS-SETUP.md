# 🚀 GitHub Actions CI/CD Setup for NewsGenie

This document explains how to configure and use the GitHub Actions workflows for automated testing, building, and deployment of the NewsGenie application.

## 📁 Workflow Files

### 1. **CI/CD Pipeline** (`.github/workflows/ci-cd-pipeline.yml`)
**Comprehensive production pipeline** with:
- ✅ Code quality checks (Black, isort, flake8)
- 🔒 Security scanning (Bandit, Safety, Trivy)
- 🧪 Multi-version Python testing (3.9, 3.10, 3.11)
- 🐳 Docker multi-arch builds (AMD64, ARM64)
- 🚀 Multi-environment deployments (Dev → Staging → Production)
- 📊 Coverage reporting and notifications

### 2. **Continuous Integration** (`.github/workflows/ci.yml`)
**Lightweight CI for PRs and feature branches**:
- ⚡ Quick code formatting and linting checks
- 🔍 Basic test execution
- 🐳 Docker build validation

### 3. **Security Scanning** (`.github/workflows/security.yml`)
**Automated security monitoring**:
- 📅 Weekly security scans
- 🔍 Dependency vulnerability checks
- 📋 Security report generation

## 🔧 Required Repository Setup

### 1. **Repository Secrets**
Configure these secrets in GitHub repository settings:

```bash
# Container Registry (if using private registry)
REGISTRY_USERNAME=your-username
REGISTRY_PASSWORD=your-token

# Kubernetes Configuration (Base64 encoded kubeconfig files)
KUBE_CONFIG_DEV=<base64-encoded-dev-kubeconfig>
KUBE_CONFIG_STAGING=<base64-encoded-staging-kubeconfig>
KUBE_CONFIG_PROD=<base64-encoded-prod-kubeconfig>

# API Keys for testing (optional, for integration tests)
OPENAI_API_KEY=your-openai-key
NEWSAPI_KEY=your-newsapi-key
TAVILY_API_KEY=your-tavily-key

# Notifications (optional)
SLACK_WEBHOOK=your-slack-webhook-url
```

### 2. **Repository Variables**
Configure these in repository settings → Variables:

```bash
# Environment URLs
DEV_URL=https://dev-newsgenie.example.com
STAGING_URL=https://staging-newsgenie.example.com
PROD_URL=https://newsgenie.example.com

# Container Registry
REGISTRY=ghcr.io  # or your private registry
```

### 3. **Branch Protection Rules**
Recommended branch protection for `main`:
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Include administrators
- ✅ Required status checks:
  - `Code Quality & Security Scan`
  - `Run Tests (3.11)`
  - `Test Docker Build`

## 🌊 Workflow Triggers

### **Automatic Triggers**
- 🔄 **Push to `main`**: Full CI/CD → Staging deployment
- 🔄 **Push to `develop`**: Full CI/CD → Dev deployment
- 🏷️ **Tags (`v*`)**: Full CI/CD → Production deployment
- 🔀 **Pull Requests**: Lightweight CI only
- 🌿 **Feature branches**: Lightweight CI only
- 📅 **Schedule**: Weekly security scans (Mondays 9 AM UTC)

### **Manual Triggers**
- 🎯 **Workflow Dispatch**: Deploy to specific environment
  ```bash
  # Via GitHub UI or CLI
  gh workflow run "NewsGenie CI/CD Pipeline" \
    -f environment=production
  ```

## 📋 Pipeline Stages

### **Stage 1: Code Quality & Security** ⏱️ ~3 mins
```yaml
Jobs:
  - Black code formatting check
  - isort import sorting check
  - Flake8 linting analysis
  - Bandit security scanning
  - Safety dependency vulnerability check
  - Version generation
```

### **Stage 2: Testing** ⏱️ ~5 mins
```yaml
Matrix Strategy:
  - Python 3.9, 3.10, 3.11
  - Unit tests with pytest
  - Coverage reporting
  - Integration test simulation
```

### **Stage 3: Build & Push** ⏱️ ~8 mins
```yaml
Docker Build:
  - Multi-architecture (AMD64, ARM64)
  - Layer caching optimization
  - Metadata extraction
  - Push to GitHub Container Registry
```

### **Stage 4: Security Scanning** ⏱️ ~4 mins
```yaml
Container Security:
  - Trivy vulnerability scanning
  - SARIF report generation
  - Security tab integration
```

### **Stage 5: Deployment** ⏱️ ~6 mins per env
```yaml
Environment Flow:
  - Development (develop branch)
  - Staging (main branch)
  - Production (tags or manual)
```

## 🚀 Deployment Environments

### **Development Environment**
- **Trigger**: Push to `develop` branch
- **URL**: https://dev-newsgenie.example.com
- **Features**: Latest features, experimental builds
- **Rollback**: Automatic on failure

### **Staging Environment**
- **Trigger**: Push to `main` branch
- **URL**: https://staging-newsgenie.example.com
- **Features**: Production-like testing, smoke tests
- **Approval**: Manual review required

### **Production Environment**
- **Trigger**: Git tags (`v*`) or manual workflow dispatch
- **URL**: https://newsgenie.example.com
- **Features**: Stable releases, comprehensive monitoring
- **Approval**: Manual review + staging success required

## 📊 Monitoring & Notifications

### **Built-in Monitoring**
- 📈 GitHub Actions execution history
- 📋 Test coverage reports
- 🔒 Security scan results in Security tab
- 📦 Container vulnerability reports

### **External Notifications**
- 💬 **Slack**: Deployment status updates
- 📧 **Email**: Security alert notifications
- 📱 **Teams**: Integration via webhook

### **Monitoring Commands**
```bash
# Check workflow status
gh run list --workflow="NewsGenie CI/CD Pipeline"

# View specific run logs
gh run view <run-id> --log

# Cancel running workflow
gh run cancel <run-id>

# Re-run failed jobs
gh run rerun <run-id>
```

## 🛠️ Local Development Integration

### **Pre-commit Hooks**
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### **Local Testing**
```bash
# Run the same checks locally
make format-check  # Black + isort
make lint         # Flake8
make security     # Bandit + Safety
make test         # Pytest with coverage
make docker-build # Local Docker build
```

### **Environment Variables**
Create `.env.local`:
```bash
ENVIRONMENT=local
OPENAI_API_KEY=your-local-key
NEWSAPI_KEY=your-local-key
TAVILY_API_KEY=your-local-key
```

## 🔧 Customization Guide

### **Adding New Environments**
1. Add environment in `ci-cd-pipeline.yml`
2. Create corresponding secrets (KUBE_CONFIG_*)
3. Update environment URLs
4. Configure environment-specific variables

### **Custom Deployment Targets**
```yaml
# Add to ci-cd-pipeline.yml
deploy-custom:
  name: Deploy to Custom Environment
  runs-on: ubuntu-latest
  environment:
    name: custom
    url: https://custom-newsgenie.example.com
  steps:
    # Custom deployment steps
```

### **Integration with Different Container Registries**
```yaml
# For AWS ECR
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-west-2

- name: Login to Amazon ECR
  uses: aws-actions/amazon-ecr-login@v2
```

## 🚨 Troubleshooting

### **Common Issues**
1. **Failed Security Scans**: Update dependencies, review Bandit findings
2. **Docker Build Failures**: Check Dockerfile syntax, dependency conflicts
3. **Deployment Failures**: Verify Kubernetes configs, resource limits
4. **Test Failures**: Review test logs, update mock data

### **Debug Commands**
```bash
# Enable debug logging
gh run list --limit 50 --json conclusion,status,name

# Download artifacts
gh run download <run-id>

# View detailed logs
gh run view <run-id> --log --job="Job Name"
```

---

**💡 Pro Tips:**
- Use draft releases for testing production deployments
- Enable GitHub Discussions for workflow feedback
- Set up status badges for README.md
- Use environment protection rules for sensitive deployments
- Consider using GitHub Environments for approval workflows

This CI/CD setup demonstrates enterprise-grade DevOps practices and will significantly enhance your project's appeal to recruiters! 🎯