#!/usr/bin/env python3
"""
🛠️ SmartHaus Group M365 Admin Helper 🛠️

This script helps you complete the M365 setup manually through the admin center
when automated creation encounters permission issues.

Author: AI Assistant
Date: 2025
"""

import json
import os
import webbrowser
from datetime import datetime

class M365AdminHelper:
    """🛠️ Helper class for manual M365 setup"""
    
    def __init__(self):
        self.admin_urls = {
            "main_admin": "https://admin.microsoft.com",
            "sharepoint_admin": "https://admin.microsoft.com/sharepoint",
            "teams_admin": "https://admin.teams.microsoft.com",
            "security_center": "https://security.microsoft.com",
            "compliance_center": "https://compliance.microsoft.com",
            "azure_portal": "https://portal.azure.com",
            "power_automate": "https://flow.microsoft.com",
            "power_apps": "https://make.powerapps.com"
        }
        
        self.site_configs = {
            "Executive": {
                "url": "https://smarthausgroup.sharepoint.com/sites/executive",
                "template": "Team site",
                "description": "Executive leadership and strategic planning",
                "libraries": ["Strategic Documents", "Board Materials", "Executive Reports", "Templates", "Archive"]
            },
            "Operations": {
                "url": "https://smarthausgroup.sharepoint.com/sites/operations",
                "template": "Team site",
                "description": "Day-to-day operations and process management",
                "libraries": ["Process Documents", "SOPs", "Operations Manuals", "Templates", "Archive"]
            },
            "Development": {
                "url": "https://smarthausgroup.sharepoint.com/sites/development",
                "template": "Team site",
                "description": "Software development and technical projects",
                "libraries": ["Code Documentation", "Technical Specs", "Project Files", "Templates", "Archive"]
            },
            "Sales_Marketing": {
                "url": "https://smarthausgroup.sharepoint.com/sites/sales-marketing",
                "template": "Team site",
                "description": "Sales, marketing, and business development",
                "libraries": ["Sales Materials", "Marketing Assets", "Client Proposals", "Templates", "Archive"]
            },
            "Finance_HR": {
                "url": "https://smarthausgroup.sharepoint.com/sites/finance-hr",
                "template": "Team site",
                "description": "Financial management and human resources",
                "libraries": ["Financial Documents", "HR Policies", "Payroll", "Templates", "Archive"]
            },
            "Client_Projects": {
                "url": "https://smarthausgroup.sharepoint.com/sites/client-projects",
                "template": "Team site",
                "description": "Client project management and deliverables",
                "libraries": ["Project Plans", "Client Deliverables", "Project Documentation", "Templates", "Archive"]
            }
        }
        
        self.teams_configs = {
            "Leadership": {
                "name": "SmartHaus Leadership",
                "description": "Executive team communications",
                "privacy": "Private",
                "channels": ["General", "Strategic Planning", "Board Updates", "Announcements", "Resources"]
            },
            "Operations": {
                "name": "SmartHaus Operations",
                "description": "Operational team collaboration",
                "privacy": "Private",
                "channels": ["General", "Process Improvement", "Daily Ops", "Announcements", "Resources"]
            },
            "Development": {
                "name": "SmartHaus Development",
                "description": "Development team collaboration",
                "privacy": "Private",
                "channels": ["General", "Code Reviews", "Architecture", "DevOps", "Resources"]
            },
            "Sales_Marketing": {
                "name": "SmartHaus Sales Marketing",
                "description": "Sales and marketing collaboration",
                "privacy": "Private",
                "channels": ["General", "Lead Generation", "Campaigns", "Client Success", "Resources"]
            }
        }

    def print_header(self):
        """🎯 Print the header"""
        print("🛠️ SmartHaus Group M365 Admin Helper 🛠️")
        print("=" * 60)
        print("This tool will guide you through manual M365 setup")
        print("when automated creation encounters permission issues.")
        print("=" * 60)

    def open_admin_center(self):
        """🔐 Open Microsoft 365 Admin Center"""
        print("\n🔐 Opening Microsoft 365 Admin Center...")
        print("Please sign in with your Global Administrator account.")
        webbrowser.open(self.admin_urls["main_admin"])
        
        input("\nPress Enter after you've signed in to continue...")

    def setup_sharepoint_sites(self):
        """🏗️ Guide through SharePoint site creation"""
        print("\n🏗️ Setting up SharePoint Sites")
        print("=" * 40)
        
        print("1. Navigate to SharePoint Admin Center")
        print("   - From Admin Center, click 'SharePoint' in the left menu")
        print("   - Or go directly to:", self.admin_urls["sharepoint_admin"])
        
        webbrowser.open(self.admin_urls["sharepoint_admin"])
        
        print("\n2. Create Site Collections")
        print("   - Click 'Active sites' in the left menu")
        print("   - Click '+ Create' button")
        print("   - Choose 'Other options'")
        print("   - Select 'Team site' template")
        
        for site_name, config in self.site_configs.items():
            print(f"\n   📁 Creating {site_name} site:")
            print(f"      - Site name: {site_name}")
            print(f"      - URL: {config['url']}")
            print(f"      - Template: {config['template']}")
            print(f"      - Description: {config['description']}")
            print(f"      - Owner: [Your admin email]")
        
        input("\nPress Enter after creating all sites...")

    def setup_teams_workspaces(self):
        """👥 Guide through Teams workspace creation"""
        print("\n👥 Setting up Microsoft Teams Workspaces")
        print("=" * 45)
        
        print("1. Navigate to Teams Admin Center")
        print("   - From Admin Center, click 'Teams' in the left menu")
        print("   - Or go directly to:", self.admin_urls["teams_admin"])
        
        webbrowser.open(self.admin_urls["teams_admin"])
        
        print("\n2. Create Teams")
        print("   - Click 'Teams' in the left menu")
        print("   - Click '+ Add' button")
        
        for team_name, config in self.teams_configs.items():
            print(f"\n   🏢 Creating {team_name} team:")
            print(f"      - Team name: {config['name']}")
            print(f"      - Description: {config['description']}")
            print(f"      - Privacy: {config['privacy']}")
            print(f"      - Owner: [Your admin email]")
            print(f"      - Channels: {', '.join(config['channels'])}")
        
        input("\nPress Enter after creating all teams...")

    def setup_security_policies(self):
        """🔒 Guide through security setup"""
        print("\n🔒 Setting up Security Policies")
        print("=" * 35)
        
        print("1. Multi-Factor Authentication (MFA)")
        print("   - Go to Users → Active Users")
        print("   - Select your admin account")
        print("   - Click 'More' → 'Setup Azure multi-factor auth'")
        print("   - Enable MFA")
        
        print("\n2. Conditional Access Policies")
        print("   - Go to Azure Portal:", self.admin_urls["azure_portal"])
        print("   - Navigate to Azure Active Directory → Security → Conditional Access")
        print("   - Create policy: Require MFA for all users")
        print("   - Create policy: Block legacy authentication")
        
        webbrowser.open(self.admin_urls["azure_portal"])
        
        input("\nPress Enter after setting up security policies...")

    def setup_automation_workflows(self):
        """🤖 Guide through automation setup"""
        print("\n🤖 Setting up Automation Workflows")
        print("=" * 40)
        
        print("1. Power Automate Setup")
        print("   - Go to:", self.admin_urls["power_automate"])
        print("   - Sign in with admin account")
        print("   - Create flows for:")
        print("     * Document approval workflow")
        print("     * Employee onboarding")
        print("     * Client project setup")
        
        webbrowser.open(self.admin_urls["power_automate"])
        
        print("\n2. Power Apps Setup")
        print("   - Go to:", self.admin_urls["power_apps"])
        print("   - Create apps for:")
        print("     * Employee directory")
        print("     * Project tracking")
        print("     * Expense management")
        
        webbrowser.open(self.admin_urls["power_apps"])
        
        input("\nPress Enter after setting up automation...")

    def create_setup_checklist(self):
        """📋 Create a setup checklist"""
        print("\n📋 Creating Setup Checklist")
        print("=" * 30)
        
        checklist = f"""
# 🚀 SmartHaus Group M365 Setup Checklist 🚀
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## ✅ SharePoint Sites Created
"""
        
        for site_name, config in self.site_configs.items():
            checklist += f"- [ ] {site_name}: {config['url']}\n"
        
        checklist += """
## ✅ Teams Workspaces Created
"""
        
        for team_name, config in self.teams_configs.items():
            checklist += f"- [ ] {team_name}: {config['name']}\n"
        
        checklist += """
## ✅ Security Policies Configured
- [ ] MFA enabled for admin accounts
- [ ] MFA enabled for all users
- [ ] Conditional access policies created
- [ ] Data loss prevention configured

## ✅ Automation Workflows Created
- [ ] Document approval workflow
- [ ] Employee onboarding workflow
- [ ] Client project setup workflow
- [ ] Monthly report generation
- [ ] Expense approval process

## ✅ Next Steps
1. [ ] Test all sites and teams
2. [ ] Upload initial documents
3. [ ] Invite team members
4. [ ] Configure external sharing
5. [ ] Set up monitoring and alerts

## 🎯 Success Criteria
- [ ] All 6 SharePoint sites accessible
- [ ] All 4 Teams workspaces functional
- [ ] Security policies enforced
- [ ] Automation workflows working
- [ ] Ready for team growth
"""
        
        # Save checklist
        with open("m365_setup_checklist.md", "w") as f:
            f.write(checklist)
        
        print("✅ Setup checklist created: m365_setup_checklist.md")
        print("📋 Use this to track your progress!")

    def run_manual_setup_guide(self):
        """🚀 Run the complete manual setup guide"""
        try:
            self.print_header()
            
            print("\n🎯 This tool will guide you through manual M365 setup.")
            print("   We'll open the necessary admin centers and provide step-by-step instructions.")
            
            input("\nPress Enter to begin...")
            
            # Step 1: Open Admin Center
            self.open_admin_center()
            
            # Step 2: Setup SharePoint Sites
            self.setup_sharepoint_sites()
            
            # Step 3: Setup Teams Workspaces
            self.setup_teams_workspaces()
            
            # Step 4: Setup Security Policies
            self.setup_security_policies()
            
            # Step 5: Setup Automation
            self.setup_automation_workflows()
            
            # Step 6: Create Checklist
            self.create_setup_checklist()
            
            print("\n🎉 🎉 🎉 MANUAL SETUP GUIDE COMPLETE! 🎉 🎉 🎉")
            print("=" * 60)
            print("✅ All admin centers opened")
            print("✅ Step-by-step instructions provided")
            print("✅ Setup checklist created")
            print("📋 Check m365_setup_checklist.md for your progress tracker")
            print("\n🚀 You're now ready to complete your M365 setup manually!")
            print("🎯 Follow the instructions in each admin center to create your sites and teams.")
            
        except Exception as e:
            print(f"❌ Error in manual setup guide: {str(e)}")

def main():
    """🎯 Main execution function"""
    helper = M365AdminHelper()
    helper.run_manual_setup_guide()

if __name__ == "__main__":
    main()
