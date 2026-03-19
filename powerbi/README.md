# Power BI Dashboard Templates

This directory contains Power BI dashboard templates for the SmartHaus AI Workforce management system.

## Dashboard Templates

### 1. Agent Performance Dashboard (`agent-performance-dashboard.pbix`)
- **Purpose**: Real-time performance analytics for all 39 AI agents
- **Data Sources**: Agent Status API, Task Management API, Performance Metrics API
- **Key Metrics**:
  - Total agents and departments
  - Performance by department
  - Task completion trends
  - Risk distribution
  - Top performing agents

### 2. Department Metrics Dashboard (`department-metrics-dashboard.pbix`)
- **Purpose**: Department-level analytics and performance metrics
- **Data Sources**: Department Status API, M365 Services API, Teams Activity API
- **Key Metrics**:
  - Department overview matrix
  - Agent distribution
  - Performance trends
  - M365 services status
  - Resource utilization

### 3. Workflow Analytics Dashboard (`workflow-analytics-dashboard.pbix`)
- **Purpose**: Power Automate workflow performance and automation analytics
- **Data Sources**: Power Automate API, SharePoint REST API, Workflow Triggers API
- **Key Metrics**:
  - Workflow execution summary
  - Success rates and failure analysis
  - Execution trends
  - Trigger performance
  - SharePoint list activity

## Setup Instructions

### Prerequisites
1. Power BI Desktop installed
2. Access to SmartHaus M365 tenant
3. API endpoints running (localhost:9000)

### Configuration Steps

1. **Import Dashboard Templates**
   ```bash
   # Open Power BI Desktop
   # File > Open > Browse
   # Select the .pbix files from this directory
   ```

2. **Configure Data Sources**
   - Update API URLs to point to your environment
   - Configure authentication for Microsoft Graph API
   - Set up refresh schedules

3. **Customize Visualizations**
   - Adjust chart types and colors
   - Modify filters and slicers
   - Add custom measures and calculated columns

4. **Publish to Power BI Service**
   - Save to Power BI workspace
   - Configure automatic refresh
   - Set up sharing permissions

### API Endpoints Required

- `http://localhost:9000/api/agents/status` - Agent status data
- `http://localhost:9000/api/agents/{agent_id}/tasks` - Task data
- `http://localhost:9000/api/agents/{agent_id}/performance` - Performance metrics
- `http://localhost:9000/api/m365/empire-overview` - M365 services status

### Authentication Setup

1. **Microsoft Graph API**
   - Register app in Azure AD
   - Grant required permissions
   - Configure OAuth2 authentication

2. **Power Automate API**
   - Use service principal authentication
   - Grant Power Platform admin permissions

3. **SharePoint REST API**
   - Use app-only authentication
   - Grant SharePoint permissions

## Refresh Schedules

- **Real-time Data**: 1-5 minutes
- **Performance Metrics**: 5-10 minutes
- **Department Analytics**: 10-15 minutes
- **Workflow Analytics**: 15-30 minutes

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify API endpoints are accessible
   - Check authentication credentials
   - Validate API permissions

2. **Data Refresh Failures**
   - Check data source connectivity
   - Verify API rate limits
   - Review error logs

3. **Visualization Issues**
   - Validate data types
   - Check for null values
   - Verify calculated measures

### Support

For technical support, contact the SmartHaus operations team or refer to the main project documentation.
