import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  className?: string;
}

export default function MetricCard({
  title,
  value,
  icon: Icon,
  trend,
  className = "",
}: MetricCardProps) {
  return (
    <div
      className={`
        bg-[#18181b] border border-[#27272a] rounded-lg p-6
        hover:border-red-500/20 transition-all duration-200
        ${className}
      `}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-400 mb-1">{title}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
          {trend && (
            <p
              className={`text-sm mt-2 ${
                trend.isPositive ? "text-green-400" : "text-red-400"
              }`}
            >
              {trend.value}
            </p>
          )}
        </div>
        <div className="p-3 bg-red-500/10 rounded-lg">
          <Icon className="w-6 h-6 text-red-500" />
        </div>
      </div>
    </div>
  );
}

// Made with Bob
