/**
 * Microsoft Teams Notifications for Advisory Services
 * Sends real-time notifications for intake, assessments, and project updates
 */

export interface TeamsNotification {
  type: 'intake_started' | 'intake_completed' | 'risk_assessment' | 'certification_request' | 'project_update';
  title: string;
  message: string;
  data?: Record<string, any>;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  channel?: string;
}

export interface IntakeNotification {
  serviceId: string;
  serviceName: string;
  clientName?: string;
  organization?: string;
  estimatedValue?: string;
  riskScore?: number;
  modules: string[];
}

export interface RiskAssessmentNotification {
  serviceId: string;
  riskScore: number;
  riskCategory: string;
  riskDetails: string[];
  recommendations: string[];
}

export interface CertificationNotification {
  track: string;
  level: string;
  candidateCount: number;
  timeline: string;
  prerequisites: string[];
}

export interface ProjectUpdateNotification {
  projectId: string;
  projectName: string;
  status: 'started' | 'in_progress' | 'completed' | 'on_hold';
  progress: number;
  nextMilestone: string;
  teamMembers: string[];
}

class TeamsNotificationService {
  private webhookUrl: string;
  private isEnabled: boolean;

  constructor() {
    // Get Teams webhook URL from environment
    this.webhookUrl = process.env.TEAMS_WEBHOOK_URL || '';
    this.isEnabled = !!this.webhookUrl;

    if (!this.isEnabled) {
      console.warn('Teams notifications disabled - TEAMS_WEBHOOK_URL not configured');
    }
  }

  /**
   * Send notification to Teams
   */
  async sendNotification(notification: TeamsNotification): Promise<boolean> {
    if (!this.isEnabled) {
      console.log('Teams notification (disabled):', notification);
      return false;
    }

    try {
      const card = this.buildTeamsCard(notification);

      const response = await fetch(this.webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(card),
      });

      if (!response.ok) {
        throw new Error(`Teams webhook failed: ${response.status} ${response.statusText}`);
      }

      console.log('Teams notification sent successfully:', notification.type);
      return true;
    } catch (error) {
      console.error('Failed to send Teams notification:', error);
      return false;
    }
  }

  /**
   * Build Teams Adaptive Card
   */
  private buildTeamsCard(notification: TeamsNotification) {
    const baseCard = {
      type: 'message',
      attachments: [{
        contentType: 'application/vnd.microsoft.card.adaptive',
        content: {
          type: 'AdaptiveCard',
          version: '1.4',
          body: [],
          actions: []
        }
      }]
    };

    switch (notification.type) {
      case 'intake_started':
        return this.buildIntakeStartedCard(notification);
      case 'intake_completed':
        return this.buildIntakeCompletedCard(notification);
      case 'risk_assessment':
        return this.buildRiskAssessmentCard(notification);
      case 'certification_request':
        return this.buildCertificationCard(notification);
      case 'project_update':
        return this.buildProjectUpdateCard(notification);
      default:
        return this.buildGenericCard(notification);
    }
  }

  /**
   * Intake Started Card
   */
  private buildIntakeStartedCard(notification: TeamsNotification) {
    const data = notification.data as IntakeNotification;

    return {
      type: 'message',
      attachments: [{
        contentType: 'application/vnd.microsoft.card.adaptive',
        content: {
          type: 'AdaptiveCard',
          version: '1.4',
          body: [
            {
              type: 'TextBlock',
              text: '🚀 **New Advisory Service Intake Started**',
              size: 'Large',
              weight: 'Bolder',
              color: 'Accent'
            },
            {
              type: 'FactSet',
              facts: [
                { title: 'Service', value: data.serviceName },
                { title: 'Organization', value: data.organization || 'Not specified' },
                { title: 'Estimated Value', value: data.estimatedValue || 'TBD' },
                { title: 'Modules', value: data.modules.join(', ') }
              ]
            },
            {
              type: 'TextBlock',
              text: `**Client:** ${data.clientName || 'Anonymous'}`,
              size: 'Medium',
              weight: 'Bolder'
            }
          ],
          actions: [
            {
              type: 'Action.OpenUrl',
              title: 'View Intake Details',
              url: `${process.env.NEXT_PUBLIC_BASE_URL}/advisory/intake/${data.serviceId}`
            },
            {
              type: 'Action.OpenUrl',
              title: 'Open M365 Dashboard',
              url: `${process.env.NEXT_PUBLIC_BASE_URL}/project-management`
            }
          ]
        }
      }]
    };
  }

  /**
   * Intake Completed Card
   */
  private buildIntakeCompletedCard(notification: TeamsNotification) {
    const data = notification.data as IntakeNotification;

    return {
      type: 'message',
      attachments: [{
        contentType: 'application/vnd.microsoft.card.adaptive',
        content: {
          type: 'AdaptiveCard',
          version: '1.4',
          body: [
            {
              type: 'TextBlock',
              text: '✅ **Advisory Service Intake Completed**',
              size: 'Large',
              weight: 'Bolder',
              color: 'Good'
            },
            {
              type: 'FactSet',
              facts: [
                { title: 'Service', value: data.serviceName },
                { title: 'Organization', value: data.organization || 'Not specified' },
                { title: 'Risk Score', value: `${data.riskScore || 0}/100` },
                { title: 'Modules', value: data.modules.join(', ') }
              ]
            }
          ],
          actions: [
            {
              type: 'Action.OpenUrl',
              title: 'Review Intake Results',
              url: `${process.env.NEXT_PUBLIC_BASE_URL}/advisory/intake/${data.serviceId}/results`
            },
            {
              type: 'Action.OpenUrl',
              title: 'Create Project Plan',
              url: `${process.env.NEXT_PUBLIC_BASE_URL}/project-management`
            }
          ]
        }
      }]
    };
  }

  /**
   * Risk Assessment Card
   */
  private buildRiskAssessmentCard(notification: TeamsNotification) {
    const data = notification.data as RiskAssessmentNotification;

    const riskColor = data.riskScore > 70 ? 'Warning' : data.riskScore > 40 ? 'Attention' : 'Good';

    return {
      type: 'message',
      attachments: [{
        contentType: 'application/vnd.microsoft.card.adaptive',
        content: {
          type: 'AdaptiveCard',
          version: '1.4',
          body: [
            {
              type: 'TextBlock',
              text: '⚠️ **Risk Assessment Completed**',
              size: 'Large',
              weight: 'Bolder',
              color: riskColor
            },
            {
              type: 'FactSet',
              facts: [
                { title: 'Service', value: data.serviceName },
                { title: 'Risk Score', value: `${data.riskScore}/100` },
                { title: 'Category', value: data.riskCategory },
                { title: 'Risk Count', value: data.riskDetails.length.toString() }
              ]
            },
            {
              type: 'TextBlock',
              text: '**Key Risks:**',
              size: 'Medium',
              weight: 'Bolder'
            },
            {
              type: 'TextBlock',
              text: data.riskDetails.slice(0, 3).join('\n• '),
              wrap: true
            }
          ],
          actions: [
            {
              type: 'Action.OpenUrl',
              title: 'View Full Assessment',
              url: `${process.env.NEXT_PUBLIC_BASE_URL}/advisory/risk-assessment/${data.serviceId}`
            }
          ]
        }
      }]
    };
  }

  /**
   * Generic Card for other notifications
   */
  private buildGenericCard(notification: TeamsNotification) {
    return {
      type: 'message',
      attachments: [{
        contentType: 'application/vnd.microsoft.card.adaptive',
        content: {
          type: 'AdaptiveCard',
          version: '1.4',
          body: [
            {
              type: 'TextBlock',
              text: notification.title,
              size: 'Large',
              weight: 'Bolder'
            },
            {
              type: 'TextBlock',
              text: notification.message,
              wrap: true
            }
          ]
        }
      }]
    };
  }

  // Convenience methods for different notification types
  async notifyIntakeStarted(data: IntakeNotification): Promise<boolean> {
    return this.sendNotification({
      type: 'intake_started',
      title: 'New Advisory Service Intake',
      message: `${data.serviceName} intake started for ${data.organization || 'new client'}`,
      data,
      priority: 'medium',
      channel: 'advisory-services'
    });
  }

  async notifyIntakeCompleted(data: IntakeNotification): Promise<boolean> {
    return this.sendNotification({
      type: 'intake_completed',
      title: 'Advisory Service Intake Completed',
      message: `${data.serviceName} intake completed with risk score ${data.riskScore || 0}/100`,
      data,
      priority: 'medium',
      channel: 'advisory-services'
    });
  }

  async notifyRiskAssessment(data: RiskAssessmentNotification): Promise<boolean> {
    return this.sendNotification({
      type: 'risk_assessment',
      title: 'Risk Assessment Completed',
      message: `Risk assessment completed for ${data.serviceName} with score ${data.riskScore}/100`,
      data,
      priority: data.riskScore > 70 ? 'high' : 'medium',
      channel: 'risk-management'
    });
  }

  async notifyCertificationRequest(data: CertificationNotification): Promise<boolean> {
    return this.sendNotification({
      type: 'certification_request',
      title: 'AIDF Certification Request',
      message: `${data.candidateCount} candidates requesting ${data.level} ${data.track} certification`,
      data: data as any,
      priority: 'medium',
      channel: 'aidf-certification'
    });
  }

  async notifyProjectUpdate(data: ProjectUpdateNotification): Promise<boolean> {
    return this.sendNotification({
      type: 'project_update',
      title: 'Project Status Update',
      message: `${data.projectName} is ${data.status} with ${data.progress}% progress`,
      data: data as any,
      priority: 'low',
      channel: 'project-management'
    });
  }
}

// Export singleton instance
export const teamsNotifications = new TeamsNotificationService();

// Export types for use in other components
export type {
  TeamsNotification,
  IntakeNotification,
  RiskAssessmentNotification,
  CertificationNotification,
  ProjectUpdateNotification
};
