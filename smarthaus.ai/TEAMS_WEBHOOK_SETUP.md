# 🚀 Microsoft Teams Webhook Setup for Advisory Services

## 🎯 **What This Enables:**

**Real-time Teams notifications for:**
- 🚀 **New Intake Started** - When someone selects an advisory service
- ✅ **Intake Completed** - When risk assessment and planning is done
- ⚠️ **Risk Assessment** - High-risk findings and recommendations
- 🎓 **Certification Requests** - AIDF certification inquiries
- 📊 **Project Updates** - Status changes and milestone completions

## 🔧 **Setup Steps:**

### **1. Create Teams Channels (if not exists):**
```
📋 advisory-services     - All advisory service notifications
⚠️  risk-management     - Risk assessment alerts
🎓 aidf-certification   - Certification requests
📊 project-management   - Project status updates
```

### **2. Add Incoming Webhooks to Each Channel:**

**For each channel:**
1. **Open Channel** → Click **⋯** (More options)
2. **Connectors** → **Incoming Webhook**
3. **Configure** → Give it a name (e.g., "Advisory Services Bot")
4. **Create** → Copy the webhook URL

### **3. Configure Environment Variables:**

**Add to your `.env.local`:**
```bash
# Teams Webhooks
TEAMS_WEBHOOK_URL=https://smarthausgroup.webhook.office.com/webhookb2/...

# Base URLs
NEXT_PUBLIC_BASE_URL=https://smarthaus.ai
NEXT_PUBLIC_M365_DASHBOARD_URL=https://smarthaus.ai/project-management
```

### **4. Test the Integration:**

**Start an advisory intake:**
1. Go to `/advisory/intake`
2. Select any service
3. Check Teams for notification

## 📱 **What Notifications Look Like:**

### **🚀 Intake Started:**
```
🚀 New Advisory Service Intake Started

Service: Strategic AI/ML Advisory
Organization: New Client
Estimated Value: TBD
Modules: Client Profile & Maturity Assessment, AI Maturity & Initiative Mapping

[View Intake Details] [Open M365 Dashboard]
```

### **✅ Intake Completed:**
```
✅ Advisory Service Intake Completed

Service: Strategic AI/ML Advisory
Organization: New Client
Risk Score: 25/100
Modules: Client Profile & Maturity Assessment, AI Maturity & Initiative Mapping

[Review Intake Results] [Create Project Plan]
```

### **⚠️ Risk Assessment:**
```
⚠️ Risk Assessment Completed

Service: Strategic AI/ML Advisory
Risk Score: 75/100
Category: High Risk
Risk Count: 3

Key Risks:
• No executive sponsor
• KPIs not defined
• No technical lead identified

[View Full Assessment]
```

## 🔗 **Integration Points:**

### **1. Intake System (`/advisory/intake`):**
- **Service Selection** → Teams notification
- **Module Completion** → Progress updates
- **Risk Assessment** → Risk score alerts

### **2. M365 Dashboard (`/project-management`):**
- **Project Creation** → Teams notification
- **Status Updates** → Progress tracking
- **Milestone Completion** → Achievement alerts

### **3. Risk Assessment (`/advisory/risk-assessment`):**
- **Assessment Start** → Teams notification
- **High-Risk Findings** → Immediate alerts
- **Recommendations** → Action item notifications

### **4. AIDF Certification (`/advisory/aidf-certification`):**
- **Certification Request** → Teams notification
- **Prerequisites Check** → Status updates
- **Training Progress** → Milestone tracking

## 🎨 **Customization Options:**

### **Notification Channels:**
- **advisory-services** - All advisory notifications
- **risk-management** - Risk-specific alerts
- **aidf-certification** - Certification updates
- **project-management** - Project status updates

### **Priority Levels:**
- **Low** - Project updates, progress tracking
- **Medium** - Intake started/completed, certification requests
- **High** - High-risk findings, urgent issues
- **Urgent** - Critical failures, security issues

### **Rich Cards:**
- **Adaptive Cards** with action buttons
- **Fact sets** with key information
- **Color coding** by risk level
- **Direct links** to relevant pages

## 🚨 **Troubleshooting:**

### **Notifications Not Working:**
1. **Check webhook URL** - Must be valid and accessible
2. **Verify environment variables** - TEAMS_WEBHOOK_URL must be set
3. **Check Teams permissions** - Webhook must have send permissions
4. **Review console logs** - Look for error messages

### **Common Issues:**
- **Webhook expired** - Recreate webhook in Teams
- **URL blocked** - Check firewall/proxy settings
- **Rate limiting** - Teams has webhook rate limits
- **Card format** - Ensure Adaptive Card format is correct

## 🎯 **Next Steps:**

1. **Set up Teams channels** for different notification types
2. **Configure webhooks** for each channel
3. **Add environment variables** to your deployment
4. **Test notifications** with advisory service intake
5. **Customize notification content** for your team's needs

**Your advisory services will now send real-time Teams notifications for every client interaction!** 🚀
