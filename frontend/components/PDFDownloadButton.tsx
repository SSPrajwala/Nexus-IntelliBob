"use client";

import { useState } from "react";
import { Download, Loader2 } from "lucide-react";
import { exportToPDF } from "@/lib/pdfExport";

interface PDFDownloadButtonProps {
  elementId: string;
  filename?: string;
  title?: string;
  disabled?: boolean;
  className?: string;
  variant?: "primary" | "secondary";
}

export default function PDFDownloadButton({
  elementId,
  filename,
  title,
  disabled = false,
  className = "",
  variant = "primary",
}: PDFDownloadButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = async () => {
    setIsExporting(true);
    setError(null);

    try {
      await exportToPDF({
        elementId,
        filename,
        title,
        scale: 2,
      });
    } catch (err) {
      console.error("PDF export error:", err);
      setError("Failed to generate PDF. Please try again.");
      
      // Clear error after 3 seconds
      setTimeout(() => setError(null), 3000);
    } finally {
      setIsExporting(false);
    }
  };

  const baseClasses = "inline-flex items-center gap-2 px-4 py-2 rounded-md font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variantClasses = {
    primary: "bg-gradient-to-r from-red-500 to-orange-500 text-white hover:from-red-600 hover:to-orange-600 shadow-lg shadow-red-500/20",
    secondary: "glass-card text-white hover:bg-white/10 border border-white/10",
  };

  return (
    <div className="relative">
      <button
        onClick={handleDownload}
        disabled={disabled || isExporting}
        className={`${baseClasses} ${variantClasses[variant]} ${className}`}
        title={disabled ? "Generate a report first" : "Download report as PDF"}
      >
        {isExporting ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Generating PDF...
          </>
        ) : (
          <>
            <Download className="w-4 h-4" />
            Download PDF
          </>
        )}
      </button>

      {/* Error Toast */}
      {error && (
        <div className="absolute top-full mt-2 left-0 right-0 bg-red-500/10 border border-red-500/30 rounded-md p-2 text-xs text-red-400 animate-in fade-in slide-in-from-top-2">
          {error}
        </div>
      )}
    </div>
  );
}

// Made with Bob
