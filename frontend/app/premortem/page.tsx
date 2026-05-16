"use client";

import { FileText } from "lucide-react";
import EmptyState from "@/components/EmptyState";

export default function PreMortemPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Pre-Mortem Reports</h1>
        <p className="text-gray-400">
          Detailed analysis of what could go wrong before it happens
        </p>
      </div>

      {/* Empty State */}
      <EmptyState
        icon={FileText}
        title="No pre-mortem reports yet"
        description="Pre-mortem reports provide detailed failure scenarios and recommendations. Generate blast radius analyses first to create pre-mortem reports."
      />
    </div>
  );
}

// Made with Bob
