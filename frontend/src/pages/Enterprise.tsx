import React from "react";
import { useEnterprise } from "../hooks/useEnterprise";
import { LicenseStatusCard } from "../components/enterprise/LicenseStatusCard";
import { BrandingEditor } from "../components/enterprise/BrandingEditor";
import { ExportImportPanel } from "../components/enterprise/ExportImportPanel";
import { OnboardingChecklist } from "../components/enterprise/OnboardingChecklist";
import { CustomerHealthCard } from "../components/enterprise/CustomerHealthCard";

export default function Enterprise() {
  const {
    license,
    branding,
    exportsList,
    onboarding,
    health,
    loading,
    error,
    applyLicense,
    revokeLicense,
    updateBranding,
    resetBranding,
    createExport,
    completeStep,
    resetOnboarding,
  } = useEnterprise();

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8 text-white">
      <div>
        <h2 className="text-3xl font-extrabold mb-2 tracking-tight">Enterprise Operations</h2>
        <p className="text-neutral-400">Manage operator licensing, system exports, onboarding steps, and white-label branding configurations.</p>
      </div>

      {error && (
        <div className="p-4 bg-state-danger/10 border border-state-danger/20 text-state-danger rounded-xl text-sm font-semibold">
          Error: {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-6">
          <div className="h-40 bg-neutral-900/50 rounded-xl animate-pulse" />
          <div className="h-60 bg-neutral-900/50 rounded-xl animate-pulse" />
        </div>
      ) : (
        <>
          {/* Customer Health Score */}
          <section className="space-y-4">
            <h3 className="text-lg font-bold text-neutral-300">Operational Engagement</h3>
            <CustomerHealthCard health={health} />
          </section>

          {/* Licensing Status */}
          <section className="space-y-4">
            <h3 className="text-lg font-bold text-neutral-300">Software License</h3>
            <LicenseStatusCard
              license={license}
              onApply={applyLicense}
              onRevoke={revokeLicense}
            />
          </section>

          {/* White-Label Customizer */}
          <section className="space-y-4">
            <h3 className="text-lg font-bold text-neutral-300 font-semibold">Tenant Whitelabeling Settings</h3>
            <BrandingEditor
              settings={branding}
              onUpdate={updateBranding}
              onReset={resetBranding}
            />
          </section>

          {/* Export Panel with Secret confirmation check */}
          <section className="space-y-4">
            <h3 className="text-lg font-bold text-neutral-300">System Backups & Configuration Exports</h3>
            <ExportImportPanel
              exportsList={exportsList}
              onCreateExport={createExport}
            />
          </section>

          {/* Onboarding checklist */}
          <section className="space-y-4">
            <h3 className="text-lg font-bold text-neutral-300">Organization Readiness Onboarding Checklist</h3>
            <OnboardingChecklist
              onboarding={onboarding}
              onCompleteStep={completeStep}
              onReset={resetOnboarding}
            />
          </section>
        </>
      )}
    </div>
  );
}
export { Enterprise };
