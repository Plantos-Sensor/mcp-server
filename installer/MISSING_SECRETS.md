# Missing GitHub Secrets

Good news! You already have most secrets configured. You only need to add **2 more secrets**:

## ✅ Secrets You Already Have

| Your Secret Name | Used For | Status |
|------------------|----------|--------|
| MACOS_CERTIFICATE | Base64-encoded Developer ID certificate | ✅ Ready |
| MACOS_CERTIFICATE_PASSWORD | Certificate password | ✅ Ready |
| APPLE_ID | Your Apple ID email | ✅ Ready |
| APPLE_APP_PASSWORD | App-specific password for notarization | ✅ Ready |
| APPLE_TEAM_ID | Your 10-character Team ID | ✅ Ready |

## 🔴 Secrets You Need to Add

Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`

### 1. KEYCHAIN_PASSWORD

**What it is:** A temporary password for the build keychain (can be any secure password)

**How to create:**
```bash
# Generate a random secure password
openssl rand -base64 32
```

**Example value:** `hX9kL2mP4qR7sT0vW3yZ6cB8nF1jG5eH4dA9bC2fE7`

Copy the generated password and add it as a new secret named `KEYCHAIN_PASSWORD`.

---

### 2. APPLE_DEVELOPER_ID

**What it is:** Your full code signing identity string

**How to find it:**
```bash
# List all code signing identities
security find-identity -v -p codesigning
```

Look for a line like:
```
1) ABC123DEF456... "Developer ID Application: Your Name (TEAM123456)"
```

**Copy the full string in quotes**, for example:
- `Developer ID Application: Plantos Inc (ABC123DEF)`
- `Developer ID Application: Tyler Dennis (XYZ987WQR)`

Add this as a new secret named `APPLE_DEVELOPER_ID`.

---

## Quick Setup Commands

```bash
# 1. Generate keychain password
echo "KEYCHAIN_PASSWORD:"
openssl rand -base64 32
echo ""

# 2. Get your Developer ID
echo "APPLE_DEVELOPER_ID:"
security find-identity -v -p codesigning | grep "Developer ID Application"
```

## After Adding Secrets

Once you've added both secrets, you're ready to create the v1.0.0 release:

```bash
cd /Users/tylerdennis/plantos/mcp-installer
git add .
git commit -m "feat: Prepare v1.0.0 release with signed installers"
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

GitHub Actions will automatically build, sign, and notarize installers for all platforms!

## Summary

**You need to add:**
1. ✅ KEYCHAIN_PASSWORD (generate with openssl)
2. ✅ APPLE_DEVELOPER_ID (get from security command)

**Total secrets needed: 7**
- Already have: 5 ✅
- Need to add: 2 🔴

That's it! 🎉
