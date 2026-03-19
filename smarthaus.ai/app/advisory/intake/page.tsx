"use client";

import React from "react";
import { services } from "@/app/lib/intake/registry";
import { useRouter } from "next/navigation";
import { teamsNotifications } from "@/app/lib/teams/notifications";

export default function IntakeLanding() {
  const router = useRouter();
  const [selected, setSelected] = React.useState<string | null>(null);
  const svc = services.find((s) => s.id === selected) || null;

  const handleServiceSelection = async (serviceId: string) => {
    setSelected(serviceId);

    // Send Teams notification for service selection
    const service = services.find(s => s.id === serviceId);
    if (service) {
      try {
        await teamsNotifications.notifyIntakeStarted({
          serviceId: service.id,
          serviceName: service.title,
          organization: 'New Client', // This would come from form data
          estimatedValue: 'TBD',
          riskScore: 0,
          modules: service.modules.map(m => m.title)
        });

        console.log('Teams notification sent for service selection');
      } catch (error) {
        console.error('Failed to send Teams notification:', error);
      }
    }
  };

  return (
    <div className="intake-landing-page">
      {/* Hero Section */}
      <section className="hero section-lg quantum-grid" style={{ minHeight: '50vh' }}>
        <div className="container text-center">
          <h1 className="hero-title">
            LEVEL-160 Consulting Intake
          </h1>
          <p className="hero-subtitle">
            Enterprise-grade intake powered by AIDF mathematical validation.
            Choose a service to begin a tailored assessment that builds your client profile
            and readiness assessment with mathematical precision.
          </p>
          <div className="proof" style={{ margin: '2rem auto', maxWidth: '48rem' }}>
            <div className="formula" style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>
              ClientProfile = ∫(Requirements × Capabilities × Constraints)dt
            </div>
            <p style={{ fontSize: '0.9rem', opacity: 0.8 }}>
              Mathematical integration of client requirements, capabilities, and constraints over time
            </p>
          </div>
        </div>
      </section>

      {/* Service Selection */}
      <section className="section graph-paper-bg">
        <div className="container">
          <h2 className="text-center mb-8">Select Your Service</h2>
          <div className="service-grid">
            {services.map((s) => (
              <div key={s.id} className="service-card" onClick={() => handleServiceSelection(s.id)}>
                <div className="service-icon">{s.icon}</div>
                <h3>{s.title}</h3>
                <p>{s.description}</p>
                <div className="service-highlights">
                  {s.highlights.map((highlight, index) => (
                    <span key={index} className="highlight-tag">{highlight}</span>
                  ))}
                </div>
                <div className="service-equation">
                  {s.equation}
                </div>
                <button className="button button-outline" style={{ marginTop: '1rem' }}>
                  Select Service
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Selected Service Details */}
      {svc && (
        <section className="section" style={{ background: 'var(--header-bg-solid)' }}>
          <div className="container">
            <div className="selected-service-details">
              <div className="service-header">
                <h2>{svc.title}</h2>
                <div className="service-meta">
                  <span className="version">Version {svc.version}</span>
                  <span className="status">LEVEL-160 Ready</span>
                </div>
              </div>

              <div className="service-description">
                <p>{svc.description}</p>
              </div>

              <div className="modules-section">
                <h3>LEVEL-160 Modules</h3>
                <div className="modules-grid">
                  {svc.modules.map((m) => (
                    <div key={m.id} className="module-item">
                      <div className="module-icon">{m.icon || '📋'}</div>
                      <div className="module-content">
                        <h4>{m.title}</h4>
                        <p>{m.description}</p>
                        <div className="module-metrics">
                          <span className="metric">Duration: {m.duration}</span>
                          <span className="metric">Complexity: {m.complexity}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="aidf-integration">
                <h3>AIDF Mathematical Foundation</h3>
                <div className="formula" style={{ textAlign: 'center', margin: '1rem 0' }}>
                  {svc.aidfFormula}
                </div>
                <p>Every assessment and recommendation is backed by mathematical proof from our AIDF framework.</p>
              </div>

              <div className="action-buttons">
                <button
                  className="button"
                  onClick={() => router.push(`/advisory/intake/${svc.id}`)}
                >
                  Start LEVEL-160 Intake
                </button>
                <button
                  className="button button-outline"
                  onClick={() => setSelected(null)}
                >
                  ← Back to Services
                </button>
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
