# DEPLOYMENT GUIDE - FA23-BAI-045
## Repository: https://github.com/raziurrehmankhan5-alt/selfhealing-mlops-FA23-BAI-045.git

---

## STEP 1: GitHub Repository Setup (Your Local Machine)

```bash
# Clone the repository
git clone https://github.com/raziurrehmankhan5-alt/selfhealing-mlops-FA23-BAI-045.git
cd selfhealing-mlops-FA23-BAI-045

# Set up the main branch
# Copy these files from the outputs folder:
# - Dockerfile
# - Jenkinsfile
# - exporter.py
# - prometheus.yml
# - alert.rules.yml
# - alertmanager.yml
# - EC2_SETUP.sh
# - README.md
# - stable-fallback-app.py
# - rollback-Jenkinsfile

# Create directories
mkdir -p k8s tests templates

# Copy K8s files into k8s/
# - blue-deployment.yaml
# - green-deployment.yaml
# - service.yaml
# - pvc.yaml

# Copy test files into tests/
# - test_api.py
# - test_ui.py

# Copy templates/index.html (PROVIDED from project spec)

# CRITICAL: Get app.py and requirements.txt from the PROVIDED files in the project spec
# Place app.py (main branch version) in root
# Place requirements.txt in root

# Commit and push main branch
git add .
git commit -m "FA23-BAI-045: Complete CI/CD pipeline setup"
git push origin main

# Create stable-fallback branch
git checkout -b stable-fallback
# Replace app.py with the stable version (use stable-fallback-app.py contents)
cat > app.py << 'EOF'
from flask import Flask, request, jsonify
import re
app = Flask(__name__)

POSITIVE_WORDS = {"good","great","excellent","happy","love",
 "wonderful","best","amazing","fantastic","superb"}
NEGATIVE_WORDS = {"bad","terrible","horrible","hate","worst",
 "awful","poor","dreadful","disgusting"}

_last_confidence = 0.95

@app.route("/health", methods=["GET"])
def health():
 return jsonify({"status":"healthy","model":"rule-based-stable-v0",
 "model_version":"stable-v0-9FEB"})

@app.route("/predict", methods=["POST"])
def predict():
 global _last_confidence
 data = request.get_json()
 words = set(re.findall(r'\w+', data.get('text','').lower()))
 if len(words & NEGATIVE_WORDS) > len(words & POSITIVE_WORDS):
 label, confidence = "NEGATIVE", 0.92
 else:
 label, confidence = "POSITIVE", 0.95
 _last_confidence = confidence
 return jsonify({"label":label,"confidence":confidence,
 "model_version":"stable-v0-9FEB"})

@app.route("/api/latest-confidence", methods=["GET"])
def latest_confidence():
 return jsonify({"confidence": _last_confidence})

if __name__ == "__main__":
 app.run(host="0.0.0.0", port=5000)
EOF

# Copy requirements.txt and Dockerfile to stable-fallback
git add app.py
git commit -m "stable-fallback: rule-based model 9FEB"
git push origin stable-fallback

# Switch back to main
git checkout main
```

---

## STEP 2: EC2 Instance Setup (SSH into 13.63.198.254)

```bash
# SSH into EC2
ssh -i /path/to/your/key.pem ubuntu@13.63.198.254

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# Log out and log back in to apply group changes
exit
# SSH back in
ssh -i /path/to/your/key.pem ubuntu@13.63.198.254

# Install Java
sudo apt install -y openjdk-11-jdk

# Install Jenkins
sudo apt install -y jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Get Jenkins initial password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
# Copy this password, you'll need it

# Install kubectl
sudo apt install -y kubectl

# Install Minikube
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube
sudo mv minikube /usr/local/bin/

# Start Minikube
minikube start --driver=docker --cpus=4 --memory=4096

# Install Grafana
sudo apt install -y grafana-server
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Pull Prometheus and Alertmanager images
docker pull prometheus:latest
docker pull prom/alertmanager:latest
```

---

## STEP 3: Jenkins Configuration (Web UI at http://13.63.198.254:8080)

```
1. Unlock Jenkins
   - Paste the initial password from Step 2
   - Install "Suggested Plugins"
   - Create admin user

2. Install Additional Plugins
   - Manage Jenkins > Plugins
   - Search and install:
     * Docker plugin
     * Docker Pipeline
     * Generic Webhook Trigger

3. Add Docker Credentials
   - Credentials > System > Global credentials
   - Add Credentials:
     * Kind: Username with password
     * Username: fa23bai0045
     * Password: [Your DockerHub password/token]
     * ID: docker-credentials

4. Create Credentials for Jenkins API
   - Your profile > Configure
   - API Token > Generate
   - Copy the token (you'll need it for the grading form)
```

---

## STEP 4: Create Jenkins Jobs

### Job 1: sentiment-ci-pipeline

```
New Item > Pipeline > sentiment-ci-pipeline

Configuration:
- Description: CI/CD pipeline for sentiment analysis
- Build Triggers: GitHub hook trigger for GITscm polling
- Pipeline:
  * Definition: Pipeline script from SCM
  * SCM: Git
  * Repository URL: https://github.com/raziurrehmankhan5-alt/selfhealing-mlops-FA23-BAI-045.git
  * Branch: */main
  * Script path: Jenkinsfile
```

### Job 2: rollback-to-stable

```
New Item > Pipeline > rollback-to-stable

Configuration:
- Description: Rollback traffic to stable green deployment
- Build Triggers: Generic Webhook Trigger
  * Token: ROLLBACK_773134_TOKEN
- Pipeline:
  * Definition: Pipeline script from SCM
  * SCM: Git
  * Repository URL: https://github.com/raziurrehmankhan5-alt/selfhealing-mlops-FA23-BAI-045.git
  * Branch: */main
  * Script path: rollback-Jenkinsfile
```

---

## STEP 5: GitHub Webhook Setup

```
1. Go to: https://github.com/raziurrehmankhan5-alt/selfhealing-mlops-FA23-BAI-045
2. Settings > Webhooks > Add webhook
3. Configuration:
   - Payload URL: http://13.63.198.254:8080/github-webhook/
   - Content type: application/json
   - Events: Just the push event
   - Active: ✓ checked
4. Click "Add webhook"
```

---

## STEP 6: Start Prometheus and Alertmanager (EC2)

```bash
# Create directories for configs
mkdir -p ~/monitoring
cd ~/monitoring

# Copy prometheus.yml from your repo
# Copy alert.rules.yml from your repo

# Run Prometheus container
docker run -d --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  -v $(pwd)/alert.rules.yml:/etc/prometheus/rules/alert.rules.yml \
  prometheus:latest

# Verify Prometheus is running
curl http://localhost:9090/api/v1/query?query=up
# Should return some data

# Copy alertmanager.yml from your repo
docker run -d --name alertmanager \
  -p 9093:9093 \
  -v $(pwd)/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
  prom/alertmanager:latest

# Verify Alertmanager is running
curl http://localhost:9093/api/v1/status
```

---

## STEP 7: Start Custom Exporter (EC2)

```bash
# Copy exporter.py from your repo to EC2
# Run it in background
nohup python exporter.py > exporter.log 2>&1 &

# Verify exporter is running
curl http://localhost:8000/metrics | grep prediction_confidence_score
# Should show: prediction_confidence_score 1.0
```

---

## STEP 8: Verify Prometheus Scraping

```bash
# Check if exporter is being scraped
curl http://13.63.198.254:9090/api/v1/targets

# Should show sentiment-ml-exporter with status "up"
# OR visit web UI: http://13.63.198.254:9090/targets
```

---

## STEP 9: Configure Grafana Dashboard

```
1. Go to http://13.63.198.254:3000
2. Login: admin / admin
3. Add Data Source:
   - Configuration > Data Sources > Add data source
   - Type: Prometheus
   - URL: http://localhost:9090
   - Click "Save & test"
4. Create Dashboard:
   - Create > Dashboard
   - Name: "MLOps - Sentiment API Health"
5. Add Panel:
   - Add > Panel
   - Title: "Prediction Confidence Score"
   - Data source: Prometheus
   - Metrics: prediction_confidence_score
   - Visualization: Time series
   - Thresholds:
     * Add threshold: 0.64 (Red)
   - Save dashboard
```

---

## STEP 10: Test End-to-End Self-Healing Loop

```bash
# 1. Verify blue (unstable) is active
curl http://13.63.198.254:32500/health
# Expected response: "model_version": "unstable-v1"

# 2. Inject drift
curl -X POST http://13.63.198.254:32500/inject-drift
# Expected: {"status": "drift_injected"}

# 3. Send a test prediction
curl -X POST http://13.63.198.254:32500/predict \
  -H 'Content-Type: application/json' \
  -d '{"text":"Spotlessly clean rooms with attentive staff and superb amenities throughout"}'
# Confidence will drop below 0.64

# 4. Wait ~90 seconds, then check Prometheus alerts
curl http://13.63.198.254:9090/alerts
# Expected: ModelConfidenceDrift alert FIRING

# 5. Check Jenkins logs
# Visit: http://13.63.198.254:8080/job/rollback-to-stable/
# Should see new build triggered

# 6. Verify rollback completed
curl http://13.63.198.254:32500/health
# Expected: "model_version": "stable-v0-9FEB"

# 7. Test stable model prediction
curl -X POST http://13.63.198.254:32500/predict \
  -H 'Content-Type: application/json' \
  -d '{"text":"Spotlessly clean rooms with attentive staff and superb amenities throughout"}'
# Confidence should be 0.92 or 0.95
```

---

## STEP 11: Submit Grading Form

Visit: https://forms.gle/sjYWv13VCJd7ox4c9

Fill in:
1. **Full Name and Roll Number:** Your Name, FA23-BAI-045
2. **GitHub Repository URL:** https://github.com/raziurrehmankhan5-alt/selfhealing-mlops-FA23-BAI-045.git
3. **AWS EC2 Public IP Address:** 13.63.198.254
4. **DockerHub Username:** fa23bai0045
5. **Jenkins Username:** [your Jenkins admin username]
6. **Jenkins API Token:** [from Step 3, item 4]

---

## STEP 12: Submit Report

Create a PDF report with:
- Screenshots of Jenkins pipeline executing (all 6 stages)
- Prometheus dashboard showing alert firing
- Alertmanager showing webhook triggered
- Service endpoint showing green (stable) after rollback
- All scripts/code sections

Submit to: https://www.dropbox.com/request/mfh2t2g28fei97qcpe63

---

## Quick Reference: Your Configuration

| Setting | Value |
|---------|-------|
| Roll Number | FA23-BAI-045 |
| Repository | https://github.com/raziurrehmankhan5-alt/selfhealing-mlops-FA23-BAI-045.git |
| EC2 IP | 13.63.198.254 |
| Docker Username | fa23bai0045 |
| Confidence Threshold | 0.64 |
| Stable Model Code | 9FEB |
| Webhook Token | ROLLBACK_773134_TOKEN |
| Test Category | HOTEL |

---

## Troubleshooting Checklist

- [ ] Docker images building and pushing to DockerHub
- [ ] Minikube running with deployments: `kubectl get deployments`
- [ ] Service on NodePort 32500: `kubectl get svc`
- [ ] Prometheus target UP: `http://13.63.198.254:9090/targets`
- [ ] Exporter reporting metric: `curl http://13.63.198.254:8000/metrics`
- [ ] GitHub webhook green checkmark: Repo settings > Webhooks
- [ ] Jenkins jobs created with exact names
- [ ] alert.rules.yml has threshold 0.64
- [ ] alertmanager.yml has token ROLLBACK_773134_TOKEN
- [ ] stable-fallback branch has code 9FEB
- [ ] All element IDs in index.html match test_ui.py

---

## Do NOT Modify After Pushing

These values are locked in the code. Changing them will cause grading script failure:
- Threshold: 0.64
- Model code: 9FEB
- Webhook token: ROLLBACK_773134_TOKEN
- All K8s resource names
- All Jenkins stage names
- All test function names
