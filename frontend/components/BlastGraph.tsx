"use client";

import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

interface GraphNode {
  id: string;
  label: string;
  status: "healthy" | "affected" | "failed";
  criticality: string;
}

interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

interface BlastGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  className?: string;
}

export default function BlastGraph({ nodes, edges, className = "" }: BlastGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    // Update dimensions on mount and resize
    const updateDimensions = () => {
      if (svgRef.current) {
        const container = svgRef.current.parentElement;
        if (container) {
          setDimensions({
            width: container.clientWidth,
            height: Math.max(500, container.clientHeight),
          });
        }
      }
    };

    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    return () => window.removeEventListener("resize", updateDimensions);
  }, []);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    // Clear previous content
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3.select(svgRef.current);
    const width = dimensions.width;
    const height = dimensions.height;

    // Create container group for zoom/pan
    const g = svg.append("g");

    // Add zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 3])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    svg.call(zoom);

    // Create arrow markers for edges
    svg.append("defs").selectAll("marker")
      .data(["dependency"])
      .enter().append("marker")
      .attr("id", (d) => `arrow-${d}`)
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 25)
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#64748b");

    // Create force simulation
    const simulation = d3.forceSimulation(nodes as any)
      .force("link", d3.forceLink(edges)
        .id((d: any) => d.id)
        .distance(150))
      .force("charge", d3.forceManyBody().strength(-500))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(60));

    // Create edges
    const link = g.append("g")
      .selectAll("line")
      .data(edges)
      .enter().append("line")
      .attr("stroke", "#64748b")
      .attr("stroke-width", 2)
      .attr("stroke-opacity", 0.6)
      .attr("marker-end", "url(#arrow-dependency)");

    // Create node groups
    const node = g.append("g")
      .selectAll("g")
      .data(nodes)
      .enter().append("g")
      .attr("cursor", "pointer")
      .call(d3.drag<any, any>()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // Add circles for nodes
    node.append("circle")
      .attr("r", 40)
      .attr("fill", (d) => getNodeColor(d.status))
      .attr("stroke", (d) => getNodeStroke(d.status))
      .attr("stroke-width", 3)
      .attr("filter", (d) => d.status === "failed" ? "url(#glow)" : "none");

    // Add glow filter for failed nodes
    const defs = svg.select("defs");
    const filter = defs.append("filter")
      .attr("id", "glow");
    filter.append("feGaussianBlur")
      .attr("stdDeviation", "4")
      .attr("result", "coloredBlur");
    const feMerge = filter.append("feMerge");
    feMerge.append("feMergeNode").attr("in", "coloredBlur");
    feMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // Add pulsing animation for critical nodes
    node.filter((d) => d.status === "failed")
      .append("circle")
      .attr("r", 40)
      .attr("fill", "none")
      .attr("stroke", "#ef4444")
      .attr("stroke-width", 2)
      .attr("opacity", 0)
      .transition()
      .duration(1500)
      .ease(d3.easeLinear)
      .attr("r", 60)
      .attr("opacity", 0.5)
      .transition()
      .duration(0)
      .attr("r", 40)
      .attr("opacity", 0)
      .on("end", function repeat() {
        d3.select(this)
          .transition()
          .duration(1500)
          .ease(d3.easeLinear)
          .attr("r", 60)
          .attr("opacity", 0.5)
          .transition()
          .duration(0)
          .attr("r", 40)
          .attr("opacity", 0)
          .on("end", repeat);
      });

    // Add labels
    node.append("text")
      .text((d) => d.label)
      .attr("text-anchor", "middle")
      .attr("dy", "0.35em")
      .attr("fill", "#ffffff")
      .attr("font-size", "12px")
      .attr("font-weight", "600")
      .attr("pointer-events", "none");

    // Add criticality badge
    node.append("circle")
      .attr("cx", 25)
      .attr("cy", -25)
      .attr("r", 8)
      .attr("fill", (d) => getCriticalityColor(d.criticality))
      .attr("stroke", "#0a0a0f")
      .attr("stroke-width", 2);

    // Add tooltips
    const tooltip = d3.select("body").append("div")
      .attr("class", "blast-graph-tooltip")
      .style("position", "absolute")
      .style("visibility", "hidden")
      .style("background-color", "rgba(15, 23, 42, 0.95)")
      .style("color", "#ffffff")
      .style("padding", "12px")
      .style("border-radius", "8px")
      .style("border", "1px solid #334155")
      .style("font-size", "14px")
      .style("pointer-events", "none")
      .style("z-index", "1000")
      .style("box-shadow", "0 4px 6px -1px rgba(0, 0, 0, 0.3)");

    node.on("mouseover", function(event, d) {
      tooltip.style("visibility", "visible")
        .html(`
          <div style="font-weight: 600; margin-bottom: 4px;">${d.label}</div>
          <div style="font-size: 12px; color: #94a3b8;">Status: <span style="color: ${getNodeColor(d.status)}">${d.status}</span></div>
          <div style="font-size: 12px; color: #94a3b8;">Criticality: ${d.criticality}</div>
        `);
    })
    .on("mousemove", function(event) {
      tooltip.style("top", (event.pageY - 10) + "px")
        .style("left", (event.pageX + 10) + "px");
    })
    .on("mouseout", function() {
      tooltip.style("visibility", "hidden");
    });

    // Update positions on simulation tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event: any) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event: any) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    // Cleanup
    return () => {
      simulation.stop();
      tooltip.remove();
    };
  }, [nodes, edges, dimensions]);

  return (
    <div className={`relative w-full h-full bg-[#0a0a0f] rounded-lg border border-gray-800 overflow-hidden ${className}`}>
      <svg
        ref={svgRef}
        width={dimensions.width}
        height={dimensions.height}
        className="w-full h-full"
      />
      <div className="absolute bottom-4 right-4 bg-gray-900/80 backdrop-blur-sm border border-gray-700 rounded-lg p-3 text-xs">
        <div className="font-semibold text-gray-300 mb-2">Legend</div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#3b82f6]"></div>
            <span className="text-gray-400">Healthy</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#f59e0b]"></div>
            <span className="text-gray-400">Affected</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#ef4444]"></div>
            <span className="text-gray-400">Failed</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function getNodeColor(status: string): string {
  switch (status) {
    case "healthy":
      return "#3b82f6"; // blue
    case "affected":
      return "#f59e0b"; // orange
    case "failed":
      return "#ef4444"; // red
    default:
      return "#64748b"; // gray
  }
}

function getNodeStroke(status: string): string {
  switch (status) {
    case "healthy":
      return "#60a5fa";
    case "affected":
      return "#fbbf24";
    case "failed":
      return "#f87171";
    default:
      return "#94a3b8";
  }
}

function getCriticalityColor(criticality: string): string {
  switch (criticality) {
    case "critical":
      return "#ef4444";
    case "high":
      return "#f59e0b";
    case "medium":
      return "#eab308";
    case "low":
      return "#22c55e";
    default:
      return "#64748b";
  }
}

// Made with Bob