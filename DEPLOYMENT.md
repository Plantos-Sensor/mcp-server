# Deployment Guide - Remote MCP Server

This guide will walk you through deploying the Plantos MCP Server as a remote service on AWS EC2.

## Prerequisites

- AWS Account with admin access
- AWS CLI installed and configured
- An EC2 instance (or you'll create one)
- Domain name (optional but recommended)

---

## Step 1: Create ECR Repository

Run this command to create your Docker image repository:

```bash
cd /Users/tylerdennis/plantos/mcp-server
chmod +x aws-setup.sh
./aws-setup.sh
```

**Save the output** - you'll need the `ECR_REPOSITORY` value for GitHub secrets.

---

## Step 2: Set Up EC2 Instance

### Option A: Use Existing EC2 Instance

If you already have an EC2 instance running your backend API, you can use the same one.

**Requirements:**
- Docker installed
- Port 8080 available (or another port of your choice)
- Security group allows inbound traffic on port 8080

**Install Docker** (if not already installed):
```bash
# SSH into your EC2 instance
ssh -i your-key.pem ec2-user@your-ec2-ip

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install AWS CLI (if not present)
sudo yum install aws-cli -y

# Log out and back in for docker group to take effect
exit
ssh -i your-key.pem ec2-user@your-ec2-ip

# Verify Docker works
docker ps
```

### Option B: Create New EC2 Instance

1. **Launch EC2 Instance:**
   - Go to AWS Console → EC2 → Launch Instance
   - Name: `plantos-mcp-server`
   - AMI: Amazon Linux 2 or Ubuntu 22.04
   - Instance type: `t3.micro` (or `t3.small` for better performance)
   - Key pair: Create new or use existing
   - Security group: Create with these inbound rules:
     - SSH (22) from your IP
     - Custom TCP (8080) from anywhere (0.0.0.0/0)
   - Storage: 20 GB gp3

2. **Connect and install Docker:**
   ```bash
   ssh -i your-key.pem ec2-user@your-new-instance-ip

   # Install Docker
   sudo yum update -y
   sudo yum install docker -y
   sudo service docker start
   sudo usermod -a -G docker ec2-user

   # Install AWS CLI
   sudo yum install aws-cli -y

   # Log out and back in
   exit
   ssh -i your-key.pem ec2-user@your-new-instance-ip
   ```

3. **Configure EC2 IAM Role** (for ECR access):
   - Go to IAM → Roles → Create Role
   - Trusted entity: AWS service → EC2
   - Permissions: `AmazonEC2ContainerRegistryReadOnly`
   - Name: `ec2-ecr-read-role`
   - Attach to your EC2 instance: EC2 → Instance → Actions → Security → Modify IAM role

---

## Step 3: Configure GitHub Secrets

Go to your GitHub repository: `https://github.com/Plantos-Sensor/mcp-server/settings/secrets/actions`

Click **New repository secret** and add each of these:

### Required Secrets

**AWS_ACCESS_KEY_ID**
```
Your AWS access key (from IAM user with ECR and EC2 permissions)
```
How to get:
1. Go to AWS Console → IAM → Users → Your User → Security credentials
2. Create access key → CLI
3. Copy Access key ID

**AWS_SECRET_ACCESS_KEY**
```
Your AWS secret access key
```
Copy from the same place as above (shown only once!)

**AWS_REGION**
```
us-east-1
```
(or whatever region you chose)

**ECR_REPOSITORY**
```
plantos-mcp-server
```
(from Step 1 output)

**EC2_HOST**
```
ec2-xx-xxx-xxx-xxx.compute-1.amazonaws.com
```
Your EC2 instance's public DNS or IP address

**EC2_USER**
```
ec2-user
```
(use `ubuntu` if you chose Ubuntu AMI)

**EC2_SSH_KEY**
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA... (your entire .pem file contents)
...
-----END RSA PRIVATE KEY-----
```
Copy the **entire** contents of your EC2 key pair .pem file

**PLANTOS_API_URL**
```
https://api.plantos.co
```
Your backend API URL

**MCP_SERVER_URL**
```
http://your-ec2-ip:8080
```
Where your MCP server will be accessible (we'll improve this in Step 5)

---

## Step 4: Deploy!

Once all secrets are configured:

1. **Commit and push to main:**
   ```bash
   cd /Users/tylerdennis/plantos/mcp-server
   git add .
   git commit -m "feat: Convert to remote MCP server with HTTP transport"
   git push origin main
   ```

2. **Watch the deployment:**
   - Go to GitHub Actions: `https://github.com/Plantos-Sensor/mcp-server/actions`
   - Watch "Deploy MCP Server to EC2" workflow
   - Should take 3-5 minutes

3. **Verify deployment:**
   ```bash
   # Test health endpoint
   curl http://your-ec2-ip:8080/health

   # Should return: {"status":"healthy","mode":"http","version":"1.0.0"}
   ```

---

## Step 5: Set Up Domain (Recommended)

Instead of using `http://ec2-ip:8080`, set up a proper domain with HTTPS.

### Option A: CloudFront + Certificate Manager (Easiest)

1. **Request SSL Certificate:**
   - AWS Console → Certificate Manager
   - Request certificate
   - Domain: `mcp.plantos.co`
   - Validation: DNS (add CNAME to your domain)

2. **Create CloudFront Distribution:**
   - Origin: Your EC2 public IP:8080
   - Viewer protocol: Redirect HTTP to HTTPS
   - Alternate domain: `mcp.plantos.co`
   - SSL certificate: Use the one you created
   - Cache behavior: Pass all headers (for API key authentication)

3. **Update DNS:**
   - Add CNAME record: `mcp.plantos.co` → CloudFront distribution URL

### Option B: Nginx Reverse Proxy on EC2

1. **SSH into EC2 and install nginx:**
   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-ip
   sudo amazon-linux-extras install nginx1 -y
   sudo systemctl start nginx
   sudo systemctl enable nginx
   ```

2. **Configure nginx:**
   ```bash
   sudo nano /etc/nginx/conf.d/mcp.conf
   ```

   Add this:
   ```nginx
   server {
       listen 80;
       server_name mcp.plantos.co;

       location / {
           proxy_pass http://localhost:8080;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

3. **Install SSL with Certbot:**
   ```bash
   sudo yum install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d mcp.plantos.co
   ```

4. **Reload nginx:**
   ```bash
   sudo systemctl reload nginx
   ```

5. **Update security group:**
   - Add inbound rule: HTTPS (443) from anywhere

6. **Update DNS:**
   - Add A record: `mcp.plantos.co` → Your EC2 Elastic IP

---

## Step 6: Update User-Facing Config

Once domain is set up, update the config in your UI:

Edit `/Users/tylerdennis/plantos/farming-advisor-ui/src/app/mcp/download/page.tsx`:

Change line 51:
```typescript
"url": "https://mcp.plantos.co",  // Instead of http://ec2-ip:8080
```

Users will then use:
```json
{
  "mcpServers": {
    "plantos": {
      "url": "https://mcp.plantos.co",
      "transport": {
        "type": "http",
        "headers": {
          "X-API-Key": "their-api-key"
        }
      }
    }
  }
}
```

---

## Step 7: Test End-to-End

1. **Get an API key** from your Plantos settings

2. **Create test config:**
   ```bash
   # macOS
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # Windows
   notepad %APPDATA%\Claude\claude_desktop_config.json
   ```

3. **Add config:**
   ```json
   {
     "mcpServers": {
       "plantos": {
         "url": "https://mcp.plantos.co",
         "transport": {
           "type": "http",
           "headers": {
             "X-API-Key": "your-actual-api-key"
           }
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop**

5. **Test in Claude:**
   - Open new conversation
   - Ask: "What tools do you have from Plantos?"
   - Try: "Analyze farm location at 30.2672, -97.7431"

---

## Monitoring & Maintenance

### View Logs
```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
docker logs -f plantos-mcp
```

### Restart Server
```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
docker restart plantos-mcp
```

### Manual Deploy (if GitHub Actions fails)
```bash
ssh -i your-key.pem ec2-user@your-ec2-ip

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URI

# Pull latest
docker pull YOUR_ECR_URI/plantos-mcp-server:latest

# Stop old container
docker stop plantos-mcp
docker rm plantos-mcp

# Run new container
docker run -d \
  --name plantos-mcp \
  --restart unless-stopped \
  -p 8080:8080 \
  -e MCP_TRANSPORT=http \
  -e PLANTOS_API_URL=https://api.plantos.co \
  YOUR_ECR_URI/plantos-mcp-server:latest
```

---

## Troubleshooting

### "Permission denied" when deploying
- Check EC2_SSH_KEY secret has correct private key format
- Verify EC2 security group allows SSH from GitHub Actions IPs

### "Cannot connect to ECR"
- Verify IAM role is attached to EC2 instance
- Check AWS credentials in GitHub secrets

### "Health check failed"
- SSH into EC2: `docker logs plantos-mcp`
- Check if port 8080 is blocked by security group
- Verify `PLANTOS_API_URL` environment variable is correct

### Claude Desktop can't connect
- Check `claude_desktop_config.json` has correct URL
- Verify API key is valid (test with curl)
- Check MCP server logs for authentication errors

---

## Cost Estimation

- **ECR Storage:** ~$0.10/month for Docker images
- **EC2 t3.micro:** ~$8/month (free tier eligible)
- **Data Transfer:** Minimal for MCP usage
- **CloudFront (optional):** ~$1-5/month depending on usage

**Total: ~$8-15/month**

---

## Next Steps

1. Run `./aws-setup.sh` to create ECR repository
2. Set up EC2 instance or use existing one
3. Add all GitHub secrets
4. Push to main branch
5. Set up domain with SSL
6. Test with Claude Desktop

Need help? Check the logs or open an issue!
