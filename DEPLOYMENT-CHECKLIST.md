# 🚀 Quick Deployment Checklist

Follow these steps to deploy your remote MCP server:

## ☐ Step 1: AWS ECR Setup (5 minutes)
```bash
cd /Users/tylerdennis/plantos/mcp-server
./aws-setup.sh
```
- [ ] Copy the ECR repository name from output

## ☐ Step 2: EC2 Setup (10-15 minutes)

### If using existing EC2:
- [ ] SSH into EC2 instance
- [ ] Install Docker if not present
- [ ] Verify port 8080 is available
- [ ] Attach IAM role with ECR read permissions

### If creating new EC2:
- [ ] Launch t3.micro instance
- [ ] Security group: SSH (22) + TCP (8080)
- [ ] Install Docker and AWS CLI
- [ ] Attach IAM role: `AmazonEC2ContainerRegistryReadOnly`
- [ ] Note down public IP/DNS

## ☐ Step 3: GitHub Secrets (5 minutes)

Go to: `https://github.com/Plantos-Sensor/mcp-server/settings/secrets/actions`

Add these secrets:

- [ ] `AWS_ACCESS_KEY_ID` - From IAM user
- [ ] `AWS_SECRET_ACCESS_KEY` - From IAM user
- [ ] `AWS_REGION` - e.g., `us-east-1`
- [ ] `ECR_REPOSITORY` - `plantos-mcp-server`
- [ ] `EC2_HOST` - Your EC2 public DNS/IP
- [ ] `EC2_USER` - `ec2-user` or `ubuntu`
- [ ] `EC2_SSH_KEY` - Full contents of `.pem` file
- [ ] `PLANTOS_API_URL` - `https://api.plantos.co`
- [ ] `MCP_SERVER_URL` - `http://your-ec2-ip:8080`

## ☐ Step 4: Deploy (5 minutes)
```bash
cd /Users/tylerdennis/plantos/mcp-server
git add .
git commit -m "feat: Deploy remote MCP server"
git push origin main
```

- [ ] Watch GitHub Actions workflow
- [ ] Wait for deployment to complete (~3-5 min)
- [ ] Test: `curl http://your-ec2-ip:8080/health`

## ☐ Step 5: Domain Setup (Optional - 15 minutes)

### Quick Option - CloudFront:
- [ ] Request SSL cert in ACM for `mcp.plantos.co`
- [ ] Create CloudFront distribution pointing to EC2:8080
- [ ] Add DNS CNAME: `mcp.plantos.co` → CloudFront URL
- [ ] Update `MCP_SERVER_URL` secret to `https://mcp.plantos.co`

### Full Control - Nginx on EC2:
- [ ] Install nginx on EC2
- [ ] Configure reverse proxy
- [ ] Install SSL with Certbot
- [ ] Add DNS A record: `mcp.plantos.co` → EC2 Elastic IP
- [ ] Update `MCP_SERVER_URL` secret to `https://mcp.plantos.co`

## ☐ Step 6: Test with Claude Desktop (5 minutes)

1. [ ] Get API key from Plantos settings
2. [ ] Edit Claude config file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
3. [ ] Add configuration:
```json
{
  "mcpServers": {
    "plantos": {
      "url": "https://mcp.plantos.co",
      "transport": {
        "type": "http",
        "headers": {
          "X-API-Key": "your-api-key-here"
        }
      }
    }
  }
}
```
4. [ ] Restart Claude Desktop
5. [ ] Test: "What tools do you have from Plantos?"
6. [ ] Test: "Analyze farm location at 30.2672, -97.7431"

## ☐ Step 7: Update UI (5 minutes)

Once domain is working:
- [ ] Update `/mcp/download` page URL to `https://mcp.plantos.co`
- [ ] Deploy frontend changes
- [ ] Test the config copy button works

---

## 🎉 Done!

Your remote MCP server is now live. Users can connect by:
1. Getting their API key from Settings
2. Adding the config to Claude Desktop
3. Restarting Claude Desktop

## 📊 Verify Everything Works

- [ ] MCP server health: `curl https://mcp.plantos.co/health`
- [ ] Claude Desktop shows Plantos tools
- [ ] Claude can execute Plantos tools successfully
- [ ] GitHub Actions deploys on push to main

## 🔧 Troubleshooting

If something doesn't work:
1. Check EC2 logs: `ssh ec2-user@your-ip "docker logs plantos-mcp"`
2. Verify GitHub Actions workflow succeeded
3. Test API key: `curl -H "X-API-Key: your-key" https://mcp.plantos.co/mcp/list-tools`
4. See full troubleshooting guide in `DEPLOYMENT.md`

---

**Estimated Total Time:** 45-60 minutes (30 min without domain setup)

**Questions?** Check `DEPLOYMENT.md` for detailed instructions!
