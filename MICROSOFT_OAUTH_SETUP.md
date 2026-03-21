# Microsoft 365 OAuth Setup Guide

## 🔐 Complete Microsoft 365 Authentication Setup

This guide will walk you through setting up real Microsoft 365 OAuth authentication for your SmartHaus M365 Enterprise Platform.

---

## **🚀 STEP 1: Azure App Registration**

### **1.1 Access Azure Portal**
- Go to: [https://portal.azure.com](https://portal.azure.com)
- Sign in with your Microsoft 365 admin account (phil@smarthausgroup.com)

### **1.2 Create App Registration**
- Navigate to **Azure Active Directory** → **App registrations**
- Click **New registration**
- **Name**: `SmartHaus M365 Enterprise Platform`
- **Supported account types**: `Accounts in this organizational directory only`
- **Redirect URI**:
  - Type: `Web`
  - URI: `https://m365.smarthaus.ai/api/auth/callback`
- Click **Register**

### **1.3 Configure API Permissions**
- Go to **API permissions**
- Click **Add a permission**
- Select **Microsoft Graph**
- Choose **Delegated permissions**
- Add these permissions:
  - `User.Read` - Read user profile
  - `Sites.Read.All` - Read SharePoint sites
  - `Group.Read.All` - Read Teams/Office 365 groups
  - `Directory.Read.All` - Read directory data
  - `Calendars.Read` - Read calendars
  - `Mail.Read` - Read email
  - `Files.Read.All` - Read OneDrive files

### **1.4 Grant Admin Consent**
- Click **Grant admin consent for [Your Organization]**
- Confirm the permissions

### **1.5 Get Client Credentials**
- Go to **Overview**
- Copy the **Application (client) ID**
- Go to **Certificates & secrets**
- Click **New client secret**
- **Description**: `Production Secret`
- **Expires**: `24 months`
- Copy the **Value** (this is your client secret)

---

## **🔧 STEP 2: Environment Variables**

### **2.1 Set Vercel Environment Variables**
```bash
# In your Vercel dashboard or CLI
vercel env add MICROSOFT_CLIENT_ID
vercel env add MICROSOFT_CLIENT_SECRET
vercel env add MICROSOFT_REDIRECT_URI
```

### **2.2 Environment Variable Values**
```env
MICROSOFT_CLIENT_ID=your_client_id_from_azure
MICROSOFT_CLIENT_SECRET=your_client_secret_from_azure
MICROSOFT_REDIRECT_URI=https://m365.smarthaus.ai/api/auth/callback
```

---

## **🚀 STEP 3: Deploy Updated API**

### **3.1 Rebuild Dashboard**
```bash
make build-dashboard
```

### **3.2 Deploy to Vercel**
```bash
vercel --prod
```

---

## **🎯 STEP 4: Test Real Authentication**

### **4.1 Test Flow**
1. Go to: `https://m365.smarthaus.ai`
2. Click **Sign in with Microsoft 365**
3. **Microsoft popup should appear** ✅
4. **Select your account**: phil@smarthausgroup.com ✅
5. **Authenticator app should trigger** ✅
6. **Enter verification code** ✅
7. **Dashboard loads with real data** ✅

---

## **🔍 TROUBLESHOOTING**

### **Common Issues:**

#### **Issue: Button clicks but nothing happens**
- **Cause**: Missing environment variables
- **Solution**: Set `MICROSOFT_CLIENT_ID` in Vercel

#### **Issue: "Invalid redirect URI" error**
- **Cause**: Redirect URI mismatch
- **Solution**: Ensure exact match in Azure App Registration

#### **Issue: "Insufficient permissions" error**
- **Cause**: Missing API permissions
- **Solution**: Grant admin consent for all permissions

#### **Issue: "Client secret expired" error**
- **Cause**: Client secret expired
- **Solution**: Generate new client secret in Azure

---

## **🔐 SECURITY CONSIDERATIONS**

### **Production Security:**
- **Client Secret**: Store securely, never expose in code
- **Redirect URIs**: Restrict to your domain only
- **API Permissions**: Use least privilege principle
- **Token Storage**: Use secure, encrypted storage
- **HTTPS**: Always use HTTPS in production

### **Development Security:**
- **Local Testing**: Use demo mode for development
- **Environment Separation**: Keep dev/prod configs separate
- **Secret Rotation**: Rotate client secrets regularly

---

## **📊 EXPECTED BEHAVIOR**

### **Before Setup (Current):**
- Button clicks but nothing happens ❌
- No Microsoft authentication ❌
- Demo mode only ❌

### **After Setup (Target):**
- Button triggers Microsoft popup ✅
- Account selection appears ✅
- Authenticator app integration ✅
- Real M365 data loads ✅
- Professional authentication flow ✅

---

## **🎉 SUCCESS INDICATORS**

### **✅ Authentication Working:**
- Microsoft login popup appears
- Account selection shows phil@smarthausgroup.com
- Authenticator app triggers
- Dashboard loads with real user data
- API calls to Microsoft Graph succeed

### **✅ Data Integration:**
- Real SharePoint sites load
- Real Teams workspaces display
- User profile shows actual M365 data
- Live status from Microsoft services

---

## **🚀 NEXT STEPS**

### **Immediate:**
1. Complete Azure App Registration
2. Set environment variables
3. Deploy updated API
4. Test authentication flow

### **Future Enhancements:**
1. **Token Refresh**: Implement automatic token renewal
2. **User Management**: Add user role management
3. **Audit Logging**: Track authentication events
4. **Multi-Factor**: Enhanced MFA support
5. **Conditional Access**: Implement access policies

---

## **📞 SUPPORT**

### **If You Need Help:**
1. Check Azure App Registration configuration
2. Verify environment variables in Vercel
3. Review browser console for errors
4. Check Vercel function logs
5. Ensure all API permissions are granted

### **Resources:**
- [Microsoft Identity Platform Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [Microsoft Graph API Reference](https://docs.microsoft.com/en-us/graph/api/overview)
- [OAuth 2.0 Authorization Code Flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)

---

**🎯 Your SmartHaus M365 Enterprise Platform will have WORLD-CLASS Microsoft 365 authentication!** 🚀
