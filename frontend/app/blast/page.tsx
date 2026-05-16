"use client";

import { Target } from "lucide-react";
import EmptyState from "@/components/EmptyState";

export default function BlastPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Blast Radius</h1>
        <p className="text-gray-400">
          Analyze the potential impact of identified risks
        </p>
      </div>

      {/* Empty State */}
      <EmptyState
        icon={Target}
        title="No blast radius analyses yet"
        description="Blast radius analysis shows what would be affected if a risk becomes an incident. Run a scan first to identify risks."
      />
    </div>
  );
}

// Made with Bob
