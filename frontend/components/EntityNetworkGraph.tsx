'use client';

import React, { useState } from 'react';
import { Network, Eye, Layers, ShieldCheck } from 'lucide-react';
import { KnowledgeGraphData, GraphNode } from '../lib/api';

interface Props {
  data: KnowledgeGraphData;
  candidateName: string;
}

export default function EntityNetworkGraph({ data, candidateName }: Props) {
  const [activeNode, setActiveNode] = useState<GraphNode | null>(data.nodes[0] || null);

  const width = 680;
  const height = 340;

  // Calculate radial layout positions for nodes
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = 125;

  const nodePositions = data.nodes.map((node, index) => {
    if (node.type === 'POLITICIAN') {
      return { ...node, x: centerX, y: centerY, color: '#0f172a' };
    }
    const angle = ((index - 1) / (data.nodes.length - 1)) * 2 * Math.PI - Math.PI / 2;
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);
    
    // Assign clean institutional colors per entity type
    let color = '#475569';
    if (node.type === 'PARTY') color = '#2563eb';
    if (node.type === 'CONSTITUENCY') color = '#d97706';
    if (node.type === 'FINANCIAL') color = '#059669';
    if (node.type === 'LEGAL') color = '#dc2626';
    if (node.type === 'COMPETITOR') color = '#64748b';

    return { ...node, x, y, color };
  });

  const nodeMap = new Map(nodePositions.map((n) => [n.id, n]));

  return (
    <div
      style={{
        background: '#ffffff',
        borderRadius: '10px',
        border: '1px solid #cbd5e1',
        padding: '20px',
        marginTop: '20px',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '16px',
          paddingBottom: '12px',
          borderBottom: '1px solid #e2e8f0',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
            <span
              style={{
                width: '26px',
                height: '26px',
                borderRadius: '6px',
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                color: '#0f172a',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Network size={15} />
            </span>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
              Entity Relationship Topology Graph
            </h3>
          </div>
          <p style={{ fontSize: '0.82rem', color: '#64748b', margin: 0 }}>
            Structured Entity Links & Provenance Mapping for {candidateName}
          </p>
        </div>

        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: '#f8fafc',
            color: '#475569',
            padding: '4px 10px',
            borderRadius: '6px',
            border: '1px solid #cbd5e1',
            fontSize: '0.75rem',
            fontWeight: 600,
          }}
        >
          <Layers size={13} /> Nodes: {data.meta.total_nodes} | Links: {data.meta.total_links} | Density: {data.meta.graph_density}
        </div>
      </div>

      {/* SVG Canvas Container */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          overflowX: 'auto',
          display: 'flex',
          justifyContent: 'center',
          background: '#f8fafc',
          borderRadius: '8px',
          padding: '12px',
          border: '1px solid #e2e8f0',
        }}
      >
        <svg width={width} height={height} style={{ maxWidth: '100%', height: 'auto' }}>
          {/* Connection Lines */}
          {data.links.map((link, idx) => {
            const source = nodeMap.get(link.source);
            const target = nodeMap.get(link.target);
            if (!source || !target) return null;

            return (
              <g key={idx}>
                <line
                  x1={source.x}
                  y1={source.y}
                  x2={target.x}
                  y2={target.y}
                  stroke="#cbd5e1"
                  strokeWidth="1.5"
                />
                <circle
                  cx={(source.x + target.x) / 2}
                  cy={(source.y + target.y) / 2}
                  r="3"
                  fill="#94a3b8"
                />
              </g>
            );
          })}

          {/* Render Nodes */}
          {nodePositions.map((node) => {
            const isSelected = activeNode?.id === node.id;
            return (
              <g
                key={node.id}
                transform={`translate(${node.x}, ${node.y})`}
                onClick={() => setActiveNode(node)}
                style={{ cursor: 'pointer' }}
              >
                {/* Node Outer Ring on Selection */}
                {isSelected && (
                  <circle
                    r={node.size + 4}
                    fill="none"
                    stroke="#0f172a"
                    strokeWidth="2"
                  />
                )}
                
                {/* Core Node Circle */}
                <circle
                  r={node.size}
                  fill={node.color}
                  stroke="#ffffff"
                  strokeWidth="2"
                />

                {/* Node Text Label */}
                <text
                  y={node.size + 14}
                  textAnchor="middle"
                  fill="#0f172a"
                  fontSize={node.type === 'POLITICIAN' ? '12px' : '11px'}
                  fontWeight={node.type === 'POLITICIAN' ? '700' : '600'}
                >
                  {node.label.length > 20 ? node.label.substring(0, 18) + '...' : node.label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Selected Node Details Bar */}
      {activeNode && (
        <div
          style={{
            marginTop: '12px',
            background: '#f8fafc',
            padding: '10px 14px',
            borderRadius: '6px',
            border: '1px solid #e2e8f0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '8px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span
              style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                background: activeNode.color,
              }}
            />
            <div>
              <strong style={{ color: '#0f172a', fontSize: '0.85rem' }}>{activeNode.label}</strong>
              <span style={{ fontSize: '0.78rem', color: '#64748b', marginLeft: '8px' }}>
                Type: <strong>{activeNode.type}</strong> — {activeNode.subtitle}
              </span>
            </div>
          </div>
          <span
            style={{
              fontSize: '0.72rem',
              color: '#334155',
              background: '#ffffff',
              padding: '3px 8px',
              borderRadius: '4px',
              border: '1px solid #cbd5e1',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Eye size={12} /> SELECTED ENTITY
          </span>
        </div>
      )}
    </div>
  );
}
