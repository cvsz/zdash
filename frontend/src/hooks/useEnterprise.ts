import { useState, useEffect } from "react";
import {
  getEnterpriseStatus,
  getLicenseStatus,
  applyLicense as apiApplyLicense,
  revokeLicense as apiRevokeLicense,
  getBrandingSettings,
  updateBrandingSettings as apiUpdateBrandingSettings,
  resetBrandingSettings as apiResetBrandingSettings,
  listExportBundles,
  createExportBundle as apiCreateExportBundle,
  getOnboardingChecklist,
  completeOnboardingStep as apiCompleteOnboardingStep,
  resetOnboardingChecklist as apiResetOnboardingChecklist,
  getCustomerHealth,
} from "../api/endpoints";
import {
  EnterpriseLicense,
  BrandingSettings,
  ExportBundle,
  OnboardingChecklist,
  CustomerHealth,
} from "../api/types";

export function useEnterprise() {
  const [license, setLicense] = useState<EnterpriseLicense | null>(null);
  const [branding, setBranding] = useState<BrandingSettings | null>(null);
  const [exportsList, setExportsList] = useState<ExportBundle[]>([]);
  const [onboarding, setOnboarding] = useState<OnboardingChecklist | null>(null);
  const [health, setHealth] = useState<CustomerHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEnterpriseData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [statusRes, exportsRes, onboardingRes, healthRes] = await Promise.all([
        getEnterpriseStatus(),
        listExportBundles(),
        getOnboardingChecklist(),
        getCustomerHealth(),
      ]);
      setLicense(statusRes.license);
      setBranding(statusRes.branding);
      setExportsList(exportsRes);
      setOnboarding(onboardingRes);
      setHealth(healthRes);
    } catch (err: any) {
      setError(err.message || "Failed to load enterprise details");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEnterpriseData();
  }, []);

  const applyLicense = async (licenseKey: string) => {
    setError(null);
    try {
      const res = await apiApplyLicense(licenseKey);
      const licRes = await getLicenseStatus();
      setLicense(licRes);
      return res;
    } catch (err: any) {
      setError(err.message || "Failed to apply license");
      throw err;
    }
  };

  const revokeLicense = async () => {
    setError(null);
    try {
      const res = await apiRevokeLicense();
      const licRes = await getLicenseStatus();
      setLicense(licRes);
      return res;
    } catch (err: any) {
      setError(err.message || "Failed to revoke license");
      throw err;
    }
  };

  const updateBranding = async (settings: Partial<BrandingSettings>) => {
    setError(null);
    try {
      const res = await apiUpdateBrandingSettings(settings);
      setBranding(res);
      return res;
    } catch (err: any) {
      setError(err.message || "Failed to update branding settings");
      throw err;
    }
  };

  const resetBranding = async () => {
    setError(null);
    try {
      const res = await apiResetBrandingSettings();
      setBranding(res);
      return res;
    } catch (err: any) {
      setError(err.message || "Failed to reset branding settings");
      throw err;
    }
  };

  const createExport = async (req: {
    export_type: string;
    include_audit_logs: boolean;
    include_content: boolean;
    include_backtests: boolean;
    include_scheduler: boolean;
    include_secrets: boolean;
  }) => {
    setError(null);
    try {
      const res = await apiCreateExportBundle(req);
      const list = await listExportBundles();
      setExportsList(list);
      return res;
    } catch (err: any) {
      setError(err.message || "Failed to create export bundle");
      throw err;
    }
  };

  const completeStep = async (step: string) => {
    setError(null);
    try {
      const res = await apiCompleteOnboardingStep(step);
      const chk = await getOnboardingChecklist();
      setOnboarding(chk);
      const h = await getCustomerHealth();
      setHealth(h);
      return res;
    } catch (err: any) {
      setError(err.message || "Failed to mark step complete");
      throw err;
    }
  };

  const resetOnboarding = async () => {
    setError(null);
    try {
      const res = await apiResetOnboardingChecklist();
      const chk = await getOnboardingChecklist();
      setOnboarding(chk);
      const h = await getCustomerHealth();
      setHealth(h);
      return res;
    } catch (err: any) {
      setError(err.message || "Failed to reset onboarding");
      throw err;
    }
  };

  return {
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
    refetch: fetchEnterpriseData,
  };
}
