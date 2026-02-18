# OPENCLAW PERMISSION CONTROLS ENABLED - 2026-02-16

## Executive Summary
✅ **SAFER CONFIGURATION APPLIED** - OpenClaw will now ask for permission before executing potentially dangerous operations

## Permission Control Configuration

### **What Changed:**
```json
"models": {
  "anthropic/claude-sonnet-4-20250514": {
    "tools": {
      "exec": {
        "ask": "always"           ← Ask before ALL shell commands
      },
      "edit": {
        "ask": "on-destructive"   ← Ask before file modifications
      },
      "write": {
        "ask": "on-destructive"   ← Ask before file creation
      }
    }
  }
}
```

### **Permission Levels Explained:**

#### **`exec.ask: "always"`**
- **Triggers on:** ALL shell command executions
- **Examples:** `ls`, `ps aux`, `ufw status`, `systemctl restart`, `rm`, `chmod`, etc.
- **Behavior:** OpenClaw will ask "Execute this command?" before running ANY shell command
- **Purpose:** Maximum control over system operations

#### **`edit.ask: "on-destructive"`**  
- **Triggers on:** File modifications that could lose data
- **Examples:** Overwriting existing files, editing system configs, modifying important files
- **Safe operations:** Small edits, appending to logs, non-critical file changes
- **Purpose:** Prevent accidental data loss

#### **`write.ask: "on-destructive"`**
- **Triggers on:** Creating files in sensitive locations
- **Examples:** Writing to `/etc/`, `/root/`, system directories
- **Safe operations:** Writing to workspace, temporary files, user documents  
- **Purpose:** Prevent system configuration corruption

## How This Affects Our Interaction

### **📋 What You'll See Now:**
When I need to run commands, you'll get prompts like:
```
🔧 I need to execute: systemctl restart ssh
This will restart the SSH service. 
Proceed? [y/N]
```

### **🎯 Commands That Will Ask:**
- **System administration:** `systemctl`, `ufw`, `iptables`, `chmod`, `chown`
- **File operations:** `rm`, `mv`, `cp` (when destructive)
- **Network operations:** `ss`, `netstat`, `curl`, `wget`
- **Process management:** `kill`, `killall`, `pkill`
- **Package management:** `apt`, `npm`, `pip`
- **Even safe commands:** `ls`, `ps`, `grep`, `cat` (because exec.ask is "always")

### **🚫 What Won't Ask:**
- **Read operations:** Reading files with the `Read` tool
- **Memory operations:** Updating memory files
- **Analysis operations:** Processing data I already have
- **Non-destructive writes:** Writing to workspace, creating documentation

## Benefits of This Configuration

### **🛡️ Security Improvements:**
- **Prevents accidental system damage** from AI errors
- **Gives you control** over every system operation
- **Protects against prompt injection** attacks
- **Allows careful review** of potentially dangerous commands
- **Prevents runaway automation** that could break things

### **🎯 Operational Benefits:**
- **Transparency:** You see exactly what commands I want to run
- **Education:** You learn what commands are needed for different tasks
- **Control:** You can stop operations before they cause problems
- **Auditing:** Clear trail of what was approved and executed

### **⚖️ Trade-offs:**
- **More interactive:** You'll need to approve commands manually
- **Slower operations:** Each command requires your confirmation
- **More prompts:** Even safe commands like `ls` will ask
- **Interruption:** Workflow paused for each system operation

## Usage Examples

### **Safe Administrative Flow:**
```
Me: "Let me check the firewall status"
System: "Execute: ufw status? [y/N]"
You: "y"
Me: Shows results and continues analysis
```

### **Dangerous Operation Flow:**
```
Me: "I need to restart the SSH service" 
System: "Execute: systemctl restart ssh? [y/N]"
You: "y" ← You approve because you understand the risk
Me: Executes and confirms success
```

### **Bulk Operations:**
```
Me: "I need to run several diagnostic commands"
System: "Execute: ps aux? [y/N]" 
You: "y"
System: "Execute: ss -ltn? [y/N]"
You: "y" 
... (continues for each command)
```

## Fine-Tuning Options

### **If Too Restrictive:**
You can modify the configuration to be less aggressive:

```json
"exec": {
  "ask": "on-destructive"    ← Only ask for dangerous commands
}
```

### **If Not Restrictive Enough:**
Current setting is maximum security. You could add more controls:

```json
"browser": {
  "ask": "always"           ← Ask before web browsing
},
"memory_search": {
  "ask": "always"           ← Ask before memory searches
}
```

### **Command-Specific Controls:**
```json
"exec": {
  "ask": "always",
  "allowList": ["ls", "ps", "cat"],  ← These don't ask
  "denyList": ["rm", "dd"]           ← These are blocked completely  
}
```

## Reverting If Needed

### **Restore Previous Behavior:**
```bash
# Restore the config before permission controls
cp /root/.openclaw/openclaw.json.before-permissions /root/.openclaw/openclaw.json
chmod 600 /root/.openclaw/openclaw.json
```

### **Or Remove Just Permission Controls:**
Edit `/root/.openclaw/openclaw.json` and remove the `"tools"` section from the model configuration.

## Security Impact Assessment

### **✅ Greatly Improved Security:**
- **Malicious command prevention:** Cannot execute harmful commands without approval
- **Prompt injection resistance:** Attacks cannot bypass user confirmation  
- **System protection:** Accidental damage prevented by confirmation step
- **Audit trail:** All approved commands logged and traceable

### **🎯 Attack Vector Mitigation:**
- **Social engineering:** Harder to trick you into approving bad commands
- **AI hallucination:** Prevents AI from running imaginary or wrong commands
- **Configuration errors:** You can catch mistakes before they cause damage
- **Automated attacks:** Cannot chain commands without individual approval

## Operational Recommendations

### **Best Practices:**
1. **Read each prompt carefully** before approving
2. **Ask questions** if you don't understand a command
3. **Deny suspicious operations** - better safe than sorry
4. **Batch approve** similar diagnostic commands
5. **Take time to think** before approving destructive operations

### **When to Approve:**
- ✅ Diagnostic commands you understand (`ps`, `ls`, `grep`)
- ✅ Operations you specifically requested 
- ✅ Standard maintenance operations (`systemctl status`)
- ✅ File operations in safe locations (`/tmp`, workspace)

### **When to Deny:**
- ❌ Commands you don't recognize or understand
- ❌ Operations that could affect system stability
- ❌ File operations in critical directories (`/etc`, `/boot`)
- ❌ Network operations to unknown destinations
- ❌ Anything that feels "too powerful" or suspicious

## Summary

🔒 **Permission Controls Successfully Enabled**

**Configuration:** Maximum security - ask before all shell commands and destructive file operations  
**Purpose:** Prevent accidental system damage and provide complete operational control  
**Trade-off:** More interactive but much safer  
**Reversal:** Simple configuration restore available if needed  

**Going forward, every system command I want to run will ask for your permission first. This gives you complete control over what happens to your system.**

---
**Permission Controls Enabled:** 2026-02-16 13:25 UTC  
**Security Level:** Maximum - all commands require approval  
**Status:** ✅ ACTIVE - OpenClaw will now ask before executing commands