import React, { useState, useEffect } from "react";
import { BrandingSettings } from "../../api/types";

interface BrandingEditorProps {
  settings: BrandingSettings | null;
  onUpdate: (settings: Partial<BrandingSettings>) => Promise<any>;
  onReset: () => Promise<any>;
}

export function BrandingEditor({ settings, onUpdate, onReset }: BrandingEditorProps) {
  const [brandName, setBrandName] = useState("");
  const [logoUrl, setLogoUrl] = useState("");
  const [primaryColor, setPrimaryColor] = useState("#7c3aed");
  const [accentColor, setAccentColor] = useState("#22c55e");
  const [supportEmail, setSupportEmail] = useState("");
  const [customDomain, setCustomDomain] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    if (settings) {
      setBrandName(settings.brand_name || "");
      setLogoUrl(settings.logo_url || "");
      setPrimaryColor(settings.primary_color || "#7c3aed");
      setAccentColor(settings.accent_color || "#22c55e");
      setSupportEmail(settings.support_email || "");
      setCustomDomain(settings.custom_domain || "");
    }
  }, [settings]);

  // White-label custom fields escape/sanitize helper to prevent injection (HTML/JS)
  const sanitizeText = (text: string) => {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#x27;");
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setSuccessMsg(null);

    try {
      const sanitized = {
        brand_name: sanitizeText(brandName),
        logo_url: sanitizeText(logoUrl),
        primary_color: sanitizeText(primaryColor),
        accent_color: sanitizeText(accentColor),
        support_email: sanitizeText(supportEmail),
        custom_domain: sanitizeText(customDomain),
      };
      await onUpdate(sanitized);
      setSuccessMsg("White-label settings updated successfully.");
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      // Ignored for presentation
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = async () => {
    setSubmitting(true);
    setSuccessMsg(null);
    try {
      await onReset();
      setSuccessMsg("Branding reset to default configuration.");
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      // Ignored for presentation
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Editor Form */}
      <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 space-y-4">
        <h4 className="text-lg font-bold text-white mb-2">Custom Branding Customization</h4>

        {successMsg && (
          <div className="p-3 bg-green-500/10 border border-green-500/20 text-green-400 rounded-lg text-xs font-semibold">
            {successMsg}
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-neutral-400 mb-1">Brand Name</label>
              <input
                type="text"
                required
                value={brandName}
                onChange={(e) => setBrandName(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-neutral-900 border border-neutral-850 text-neutral-200 focus:outline-none focus:border-violet-500 text-sm font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-neutral-400 mb-1">Logo URL</label>
              <input
                type="text"
                placeholder="https://..."
                value={logoUrl}
                onChange={(e) => setLogoUrl(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-neutral-900 border border-neutral-850 text-neutral-200 focus:outline-none focus:border-violet-500 text-sm"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-neutral-400 mb-1">Primary Color</label>
              <div className="flex gap-2 items-center">
                <input
                  type="color"
                  value={primaryColor}
                  onChange={(e) => setPrimaryColor(e.target.value)}
                  className="bg-transparent border-0 w-8 h-8 cursor-pointer rounded overflow-hidden p-0"
                />
                <input
                  type="text"
                  value={primaryColor}
                  onChange={(e) => setPrimaryColor(e.target.value)}
                  className="w-full px-2 py-1 rounded bg-neutral-900 border border-neutral-850 text-neutral-200 text-xs font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-neutral-400 mb-1">Accent Color</label>
              <div className="flex gap-2 items-center">
                <input
                  type="color"
                  value={accentColor}
                  onChange={(e) => setAccentColor(e.target.value)}
                  className="bg-transparent border-0 w-8 h-8 cursor-pointer rounded overflow-hidden p-0"
                />
                <input
                  type="text"
                  value={accentColor}
                  onChange={(e) => setAccentColor(e.target.value)}
                  className="w-full px-2 py-1 rounded bg-neutral-900 border border-neutral-850 text-neutral-200 text-xs font-mono"
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-neutral-400 mb-1">Support Contact Email</label>
              <input
                type="email"
                value={supportEmail}
                onChange={(e) => setSupportEmail(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-neutral-900 border border-neutral-850 text-neutral-200 focus:outline-none focus:border-violet-500 text-sm font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-neutral-400 mb-1">Custom Portal Domain</label>
              <input
                type="text"
                placeholder="dash.yourdomain.com"
                value={customDomain}
                onChange={(e) => setCustomDomain(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-neutral-900 border border-neutral-850 text-neutral-200 focus:outline-none focus:border-violet-500 text-sm font-mono"
              />
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 py-2 px-4 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs border border-violet-500/20 transition duration-150"
            >
              {submitting ? "Updating..." : "Save Branding Settings"}
            </button>

            <button
              type="button"
              onClick={handleReset}
              disabled={submitting}
              className="py-2 px-4 rounded-lg bg-neutral-900 hover:bg-neutral-850 text-neutral-300 border border-neutral-800 hover:border-neutral-700 text-xs font-semibold transition duration-150"
            >
              Reset to Defaults
            </button>
          </div>
        </form>
      </div>

      {/* Live Preview Panel */}
      <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 flex flex-col justify-between">
        <div>
          <h4 className="text-lg font-bold text-white mb-1">White-Label Live Preview</h4>
          <p className="text-xs text-neutral-500 mb-6">See how your styling options apply to the Topbar console layout.</p>

          <div className="border border-neutral-800 rounded-lg overflow-hidden bg-neutral-950 shadow-inner">
            {/* Mock Topbar Navigation */}
            <div className="h-14 border-b border-neutral-900 px-4 flex items-center justify-between" style={{ borderTop: `3px solid ${primaryColor}` }}>
              <div className="flex items-center gap-3">
                {logoUrl ? (
                  <img src={logoUrl} alt="Logo preview" className="h-6 object-contain" />
                ) : (
                  <div className="w-6 h-6 rounded-full flex items-center justify-center font-black text-xs text-white" style={{ backgroundColor: primaryColor }}>
                    {brandName.substring(0, 1).toUpperCase() || "Z"}
                  </div>
                )}
                <span className="font-bold text-sm text-white">{brandName || "zDash"}</span>
                <span className="text-[9px] uppercase font-bold px-1.5 py-0.5 rounded text-neutral-400 bg-neutral-900 border border-neutral-800">
                  Preview
                </span>
              </div>

              <div className="flex items-center gap-3">
                <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: accentColor }} />
                <span className="text-[10px] font-mono text-neutral-500">Live feed connected</span>
              </div>
            </div>

            {/* Mock Dashboard Layout */}
            <div className="p-4 bg-neutral-950 space-y-4">
              <div className="grid grid-cols-3 gap-2">
                <div className="h-16 rounded border border-neutral-900 bg-neutral-900/10 p-2 flex flex-col justify-between">
                  <span className="text-[9px] text-neutral-500 font-bold uppercase tracking-wider">Signals</span>
                  <span className="text-base font-bold text-white" style={{ color: accentColor }}>14 Validated</span>
                </div>
                <div className="h-16 rounded border border-neutral-900 bg-neutral-900/10 p-2 flex flex-col justify-between">
                  <span className="text-[9px] text-neutral-500 font-bold uppercase tracking-wider">Guardians</span>
                  <span className="text-base font-bold text-white">0 Breaches</span>
                </div>
                <div className="h-16 rounded border border-neutral-900 bg-neutral-900/10 p-2 flex flex-col justify-between">
                  <span className="text-[9px] text-neutral-500 font-bold uppercase tracking-wider">Status</span>
                  <span className="text-xs font-semibold text-neutral-400 capitalize">Proactive</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="border-t border-neutral-900/80 pt-4 text-xs text-neutral-500 flex flex-col gap-1.5">
          <div>
            Support contact: <span className="font-mono text-neutral-400">{supportEmail || "N/A"}</span>
          </div>
          <div>
            Custom hostname: <span className="font-mono text-neutral-400">{customDomain || "N/A"}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
export default BrandingEditor;
