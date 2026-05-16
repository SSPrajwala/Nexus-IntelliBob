"use client";

import React, { useEffect, useState } from "react";
import { AlertTriangle, Clock, TrendingDown, Zap } from "lucide-react";

interface TimelineEvent {
  service: string;
  time_offset: number;
  impact_type: string;
  description: string;
}

interface FailureTimelineProps {
  events: TimelineEvent[];
  className?: string;
}

export default function FailureTimeline({ events, className = "" }: FailureTimelineProps) {
  const [visibleEvents, setVisibleEvents] = useState<number>(0);

  useEffect(() => {
    // Animate events appearing one by one
    if (events.length === 0) return;

    setVisibleEvents(0);
    const interval = setInterval(() => {
      setVisibleEvents((prev) => {
        if (prev >= events.length) {
          clearInterval(interval);
          return prev;
        }
        return prev + 1;
      });
    }, 300);

    return () => clearInterval(interval);
  }, [events]);

  if (events.length === 0) {
    return (
      <div className={`bg-gray-900/50 border border-gray-800 rounded-lg p-8 text-center ${className}`}>
        <Clock className="w-12 h-12 text-gray-600 mx-auto mb-3" />
        <p className="text-gray-400">No timeline data available</p>
      </div>
    );
  }

  return (
    <div className={`bg-gray-900/50 border border-gray-800 rounded-lg p-6 ${className}`}>
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-red-500/10 rounded-lg">
          <Zap className="w-5 h-5 text-red-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">Cascading Failure Timeline</h3>
          <p className="text-sm text-gray-400">Propagation sequence and impact analysis</p>
        </div>
      </div>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-red-500 via-orange-500 to-yellow-500"></div>

        {/* Timeline events */}
        <div className="space-y-6">
          {events.map((event, index) => (
            <div
              key={index}
              className={`relative pl-20 transition-all duration-500 ${
                index < visibleEvents
                  ? "opacity-100 translate-x-0"
                  : "opacity-0 -translate-x-4"
              }`}
              style={{ transitionDelay: `${index * 100}ms` }}
            >
              {/* Time marker */}
              <div className="absolute left-0 flex items-center gap-3">
                <div
                  className={`w-16 h-16 rounded-full flex items-center justify-center border-2 ${
                    getImpactStyles(event.impact_type).border
                  } ${getImpactStyles(event.impact_type).bg} backdrop-blur-sm`}
                >
                  {getImpactIcon(event.impact_type)}
                </div>
              </div>

              {/* Event card */}
              <div
                className={`bg-gray-800/50 border ${
                  getImpactStyles(event.impact_type).cardBorder
                } rounded-lg p-4 hover:bg-gray-800/70 transition-colors`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-gray-400">
                      T+{event.time_offset}s
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium ${
                        getImpactStyles(event.impact_type).badge
                      }`}
                    >
                      {formatImpactType(event.impact_type)}
                    </span>
                  </div>
                </div>

                <h4 className="text-white font-semibold mb-1">{event.service}</h4>
                <p className="text-sm text-gray-400">{event.description}</p>

                {/* Progress indicator */}
                {index < visibleEvents && (
                  <div className="mt-3 h-1 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        getImpactStyles(event.impact_type).progress
                      } animate-pulse`}
                      style={{
                        width: "100%",
                        animation: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                      }}
                    ></div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Summary footer */}
        {visibleEvents >= events.length && (
          <div className="mt-8 pt-6 border-t border-gray-800 animate-fade-in">
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-800/30 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-red-400">{events.length}</div>
                <div className="text-xs text-gray-400 mt-1">Services Affected</div>
              </div>
              <div className="bg-gray-800/30 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-orange-400">
                  {events[events.length - 1]?.time_offset || 0}s
                </div>
                <div className="text-xs text-gray-400 mt-1">Total Cascade Time</div>
              </div>
              <div className="bg-gray-800/30 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-yellow-400">
                  {Math.round((events.length / (events[events.length - 1]?.time_offset || 1)) * 60)}
                </div>
                <div className="text-xs text-gray-400 mt-1">Failures/Min</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function getImpactIcon(impactType: string) {
  switch (impactType) {
    case "complete_failure":
      return <AlertTriangle className="w-6 h-6 text-red-400" />;
    case "degraded_performance":
      return <TrendingDown className="w-6 h-6 text-orange-400" />;
    case "partial_degradation":
      return <Clock className="w-6 h-6 text-yellow-400" />;
    default:
      return <AlertTriangle className="w-6 h-6 text-gray-400" />;
  }
}

function getImpactStyles(impactType: string) {
  switch (impactType) {
    case "complete_failure":
      return {
        border: "border-red-500",
        bg: "bg-red-500/10",
        cardBorder: "border-red-500/30",
        badge: "bg-red-500/20 text-red-300",
        progress: "bg-red-500",
      };
    case "degraded_performance":
      return {
        border: "border-orange-500",
        bg: "bg-orange-500/10",
        cardBorder: "border-orange-500/30",
        badge: "bg-orange-500/20 text-orange-300",
        progress: "bg-orange-500",
      };
    case "partial_degradation":
      return {
        border: "border-yellow-500",
        bg: "bg-yellow-500/10",
        cardBorder: "border-yellow-500/30",
        badge: "bg-yellow-500/20 text-yellow-300",
        progress: "bg-yellow-500",
      };
    default:
      return {
        border: "border-gray-500",
        bg: "bg-gray-500/10",
        cardBorder: "border-gray-500/30",
        badge: "bg-gray-500/20 text-gray-300",
        progress: "bg-gray-500",
      };
  }
}

function formatImpactType(impactType: string): string {
  return impactType
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

// Made with Bob