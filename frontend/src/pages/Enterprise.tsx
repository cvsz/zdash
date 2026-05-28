import React from "react";
import { LicenseStatus } from "../components/enterprise/LicenseStatus";
import { BrandingEditor } from "../components/enterprise/BrandingEditor";
import { ExportManager } from "../components/enterprise/ExportManager";
import { OnboardingChecklist } from "../components/enterprise/OnboardingChecklist";

export default function Enterprise() {
  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-bold mb-2">Enterprise Hub</h2>
        <p className="text-neutral-400">Manage licenses, branding, compliance exports, and customer success.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-8">
          <LicenseStatus />
          <BrandingEditor />
        </div>
        
        <div className="space-y-8">
          <OnboardingChecklist />
          <ExportManager />
        </div>
      </div>
    </div>
  );
}
