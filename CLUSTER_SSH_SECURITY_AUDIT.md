# CLUSTER SSH SECURITY AUDIT - 2026-02-16

## Executive Summary
**🔴 CRITICAL SECURITY VULNERABILITIES FOUND**

Several cluster nodes have insecure SSH configurations that allow password authentication alongside key-based authentication, creating potential security risks.

## Connectivity Status

### ✅ **Working Nodes (5/6)**
| Node | IP | SSH Status | Hostname |
|------|----|-----------:|----------|
| x99-01 | 10.0.0.253 | ✅ ONLINE | Database Leader |
| x99-02 | 10.0.0.252 | ✅ ONLINE | Database Standby |
| x99-04 | 10.0.0.249 | ✅ ONLINE | Database Standby |
| x99-05 | 10.0.0.248 | ✅ ONLINE | Worker |
| x99-06 | 10.0.0.247 | ✅ ONLINE | Database |

### ⚠️ **Problematic Node (1/6)**
| Node | IP | SSH Status | Issue |
|------|----|-----------:|-------|
| x99-03 | 10.0.0.250 | ❌ INTERMITTENT | Connection timeouts/hangs |

**Note:** x99-03 shows "ONLINE" in incus cluster but has SSH connectivity issues.

## Security Vulnerabilities Found

### 🔴 **CRITICAL: Password Authentication Enabled**

**All tested cluster nodes have dangerous SSH configuration:**

```bash
# From sshd -T output on cluster nodes:
passwordauthentication yes     # ❌ SECURITY RISK
pubkeyauthentication yes      # ✅ Good
permitrootlogin without-password  # ⚠️ Partial security
```

**Risk Level:** **HIGH**
- Allows brute force password attacks
- Provides fallback authentication even when keys fail
- Not aligned with security best practices

### 🔴 **CRITICAL: User Account with Password**

**Account Status Check (x99-01 example):**
```
root L 2024-08-27    # ✅ Locked (good)
dalang P 2026-01-15  # ❌ Password set (vulnerable)
```

**Security Impact:**
- `dalang` user has active password (set 2026-01-15)
- Combined with password authentication = SSH vulnerability
- Potential for unauthorized access if password is weak/compromised

### ⚠️ **MODERATE RISKS**

1. **Default SSH Port (22)**
   - Standard port increases exposure to automated attacks
   - Consider non-standard port for additional security

2. **No User Access Restrictions**
   - No `AllowUsers` or `DenyUsers` configured
   - Any valid system user could potentially SSH

3. **Authentication Attempt Limits**
   - `MaxAuthTries: 6` (reasonable)
   - `MaxSessions: 10` (reasonable)

## Current Authentication Flow
```
SSH Connection → Public Key Auth (preferred) → Password Auth (fallback)
                      ↓ SUCCESS                    ↓ VULNERABLE
                 ✅ Secure Access            ❌ Brute Force Risk
```

## Observed Authentication Pattern
**Recent SSH logs show secure key-based authentication:**
```
Accepted publickey for root from 10.0.0.251 port 41688 ssh2: RSA SHA256:rP9k...
```

But password authentication remains available as fallback.

## Immediate Security Recommendations

### 🔥 **URGENT (Fix Immediately)**

1. **Disable Password Authentication on ALL cluster nodes:**
   ```bash
   # On each node:
   echo "PasswordAuthentication no" >> /etc/ssh/sshd_config.d/99-security.conf
   systemctl reload ssh
   ```

2. **Lock dalang user password or remove it:**
   ```bash
   # On each node:
   passwd -l dalang  # Lock password
   # OR
   passwd -d dalang  # Remove password entirely
   ```

### 📋 **Important (Fix Soon)**

3. **Add user restrictions:**
   ```bash
   echo "AllowUsers root" >> /etc/ssh/sshd_config.d/99-security.conf
   ```

4. **Consider non-standard SSH port:**
   ```bash
   echo "Port 2222" >> /etc/ssh/sshd_config.d/99-security.conf
   ```

5. **Investigate x99-03 connectivity issues:**
   - SSH service may be overloaded or misconfigured
   - Network issues affecting node 10.0.0.250

### 🔍 **Monitor**

- Set up SSH attack monitoring
- Regular security configuration audits
- Monitor failed authentication attempts

## Risk Assessment

**Current Risk Level:** 🔴 **HIGH**

**Attack Vectors:**
1. Password brute force against `dalang` user
2. Credential stuffing attacks
3. Automated SSH scanning/attacks

**Mitigation Priority:**
1. Disable password authentication (CRITICAL)
2. Lock/remove user passwords (CRITICAL)  
3. Fix x99-03 connectivity (HIGH)
4. Implement access restrictions (MEDIUM)

## Compliance Status

❌ **NOT COMPLIANT** with security best practices:
- CIS Benchmark: SSH password auth should be disabled
- NIST Guidelines: Multi-factor preferred, passwords discouraged
- Industry Standard: Key-only authentication for servers

## Conclusion

While cluster nodes currently use secure key-based authentication in practice, the enabled password authentication creates unnecessary security risks. **Immediate action required** to disable password authentication and lock user passwords across all cluster nodes.

**Next Steps:**
1. Apply SSH security hardening to all 6 cluster nodes
2. Resolve x99-03 connectivity issues
3. Implement ongoing security monitoring

Updated: 2026-02-16 06:50 UTC