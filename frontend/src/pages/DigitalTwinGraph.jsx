import React, { useState, useEffect, useCallback, useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Handle,
  Position
} from 'reactflow';
import 'reactflow/dist/style.css';
import { apiFetch } from '../services/api';
import {
  Network,
  RefreshCw,
  Search,
  Filter,
  Layers,
  Database,
  Info,
  ArrowRight,
  ShieldAlert,
  CheckCircle2,
  Clock
} from 'lucide-react';

// Custom Node Renderer for React Flow
const CustomNode = ({ data }) => {
  const isSelected = data.isSelected;
  return (
    <div
      className={`px-3.5 py-2.5 rounded-xl border backdrop-blur-md transition-all shadow-xl max-w-[220px] ${
        data.style_color || 'bg-slate-900/90 border-slate-700 text-white'
      } ${isSelected ? 'ring-2 ring-indigo-400 border-indigo-400 scale-105' : ''}`}
    >
      <Handle type="target" position={Position.Top} className="w-2 h-2 !bg-indigo-400" />
      <div className="flex items-center justify-between gap-2 mb-1">
        <span className="text-[10px] font-bold uppercase tracking-wider opacity-80">
          {data.entity_type}
        </span>
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
      </div>
      <div className="text-xs font-bold truncate text-white mb-0.5">
        {data.label}
      </div>
      <div className="font-mono text-[10px] text-slate-400 truncate">
        {data.global_id}
      </div>
      <Handle type="source" position={Position.Bottom} className="w-2 h-2 !bg-indigo-400" />
    </div>
  );
};

export default function DigitalTwinGraph() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncLatency, setSyncLatency] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [impactChain, setImpactChain] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');

  const nodeTypes = useMemo(() => ({ customNode: CustomNode }), []);

  const fetchGraph = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiFetch('/graph/subgraph?limit=150');
      if (response.data) {
        setNodes(response.data.nodes || []);
        setEdges(response.data.edges || []);
      }
    } catch (err) {
      console.error('Error fetching Knowledge Graph:', err);
    } finally {
      setLoading(false);
    }
  }, [setNodes, setEdges]);

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  const handleSyncGraph = async () => {
    setSyncing(true);
    const startTime = performance.now();
    try {
      const res = await apiFetch('/graph/sync?limit=500', { method: 'POST' });
      const duration = ((performance.now() - startTime) / 1000).toFixed(2);
      setSyncLatency(res.result?.sync_duration_seconds || duration);
      await fetchGraph();
    } catch (err) {
      console.error('Graph sync error:', err);
    } finally {
      setSyncing(false);
    }
  };

  const onNodeClick = async (_, node) => {
    setSelectedNode(node.data);
    try {
      const res = await apiFetch(`/graph/impact?global_id=${node.data.global_id}`);
      if (res.data) {
        setImpactChain(res.data);
      }
    } catch (err) {
      console.error('Error fetching impact chain:', err);
      setImpactChain(null);
    }
  };

  // Filter nodes by category and search term
  const filteredNodes = useMemo(() => {
    return nodes.filter((n) => {
      const matchesCategory =
        categoryFilter === 'ALL' || n.data.entity_type?.toUpperCase() === categoryFilter.toUpperCase();
      const matchesSearch =
        !searchQuery ||
        n.data.global_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        n.data.label.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }, [nodes, categoryFilter, searchQuery]);

  return (
    <div className="h-[calc(100vh-6.5rem)] flex flex-col space-y-4">
      {/* Top Controls Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-card rounded-xl p-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-indigo-950/80 border border-indigo-800 rounded-xl text-indigo-400">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight">Digital Twin Knowledge Graph</h1>
            <p className="text-xs text-slate-400">
              Neo4j multi-hop entity topology & 3+ hop disruption propagation chains (§4.2 REQ-1 to REQ-4)
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Search Box */}
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs">
            <Search className="w-3.5 h-3.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search global_id or name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent text-white placeholder-slate-500 focus:outline-none w-44"
            />
          </div>

          {/* Category Filter */}
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="bg-transparent text-white font-medium focus:outline-none cursor-pointer"
            >
              <option value="ALL" className="bg-slate-900">All Entities</option>
              <option value="Supplier" className="bg-slate-900">Suppliers</option>
              <option value="Product" className="bg-slate-900">Products</option>
              <option value="Warehouse" className="bg-slate-900">Warehouses</option>
              <option value="Order" className="bg-slate-900">Orders</option>
              <option value="Shipment" className="bg-slate-900">Shipments</option>
              <option value="DisruptionEvent" className="bg-slate-900">Disruption Events</option>
            </select>
          </div>

          {/* Sync Engine Button */}
          <button
            onClick={handleSyncGraph}
            disabled={syncing}
            className="px-3.5 py-1.5 bg-indigo-600/90 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-lg shadow-indigo-900/30"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
            <span>{syncing ? 'Syncing Graph...' : 'Sync Graph'}</span>
          </button>

          {syncLatency && (
            <span className="text-[11px] font-mono text-emerald-400 bg-emerald-950/80 px-2 py-1 rounded border border-emerald-800">
              Sync: {syncLatency}s
            </span>
          )}
        </div>
      </div>

      {/* Main Graph Viewport & Inspector Panel */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4 relative overflow-hidden">
        {/* React Flow Graph Visualizer Container */}
        <div className="lg:col-span-3 glass-card rounded-xl overflow-hidden relative border border-slate-800 h-full min-h-[480px]">
          {loading ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center space-y-3 bg-slate-950/80 z-20">
              <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
              <p className="text-xs text-slate-400">Loading Neo4j Digital Twin Subgraph...</p>
            </div>
          ) : (
            <ReactFlow
              nodes={filteredNodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              nodeTypes={nodeTypes}
              fitView
              className="bg-slate-950/50"
            >
              <Background color="#334155" gap={16} size={1} />
              <Controls className="!bg-slate-900 !border-slate-800 !text-slate-300" />
              <MiniMap
                nodeColor={(node) => {
                  if (node.data?.entity_type === 'Supplier') return '#f59e0b';
                  if (node.data?.entity_type === 'Product') return '#6366f1';
                  if (node.data?.entity_type === 'Warehouse') return '#3b82f6';
                  if (node.data?.entity_type === 'DisruptionEvent') return '#f43f5e';
                  return '#10b981';
                }}
                className="!bg-slate-900/90 !border-slate-800"
              />
            </ReactFlow>
          )}
        </div>

        {/* Selected Node Multi-Hop Impact Chain Sidebar */}
        <div className="lg:col-span-1 glass-card rounded-xl p-4 flex flex-col overflow-y-auto border border-slate-800">
          <div className="flex items-center space-x-2 border-b border-slate-800 pb-3 mb-3">
            <Info className="w-4 h-4 text-indigo-400" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">Node & Impact Inspector</h3>
          </div>

          {selectedNode ? (
            <div className="space-y-4 text-xs">
              {/* Node Identity Card */}
              <div className="p-3 bg-slate-900/90 rounded-lg border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                    {selectedNode.entity_type}
                  </span>
                  <span className="font-mono text-[10px] text-slate-500">{selectedNode.global_id}</span>
                </div>
                <h4 className="font-bold text-sm text-white">{selectedNode.label}</h4>
              </div>

              {/* Entity Properties Table */}
              <div className="space-y-1.5">
                <span className="text-[11px] font-semibold text-slate-400">Entity Attributes:</span>
                <div className="p-2.5 bg-slate-900/60 rounded-lg border border-slate-800 space-y-1 font-mono text-[11px] text-slate-300">
                  {Object.entries(selectedNode.properties || {}).map(([k, v]) => (
                    <div key={k} className="flex justify-between border-b border-slate-800/50 py-0.5">
                      <span className="text-slate-500">{k}:</span>
                      <span className="text-slate-200 truncate max-w-[120px]">{String(v)}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* 3+ Hop Multi-Hop Downstream Impact Chain */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-semibold text-slate-400">Multi-Hop Impact Chain:</span>
                  {impactChain && (
                    <span className="text-[10px] font-mono text-indigo-300 bg-indigo-950/80 px-1.5 py-0.5 rounded border border-indigo-800">
                      Depth: {impactChain.multi_hop_depth} Hops
                    </span>
                  )}
                </div>

                {impactChain?.impact_chain && impactChain.impact_chain.length > 0 ? (
                  <div className="space-y-2">
                    {impactChain.impact_chain.map((item, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 bg-slate-900/90 rounded-lg border border-slate-800/80 flex items-center justify-between"
                      >
                        <div className="flex items-center space-x-2">
                          <span className="w-5 h-5 rounded-full bg-slate-800 text-[10px] font-mono flex items-center justify-center text-indigo-400 font-bold">
                            H{item.hop_depth}
                          </span>
                          <div>
                            <div className="font-mono text-[11px] font-bold text-white">{item.target_global_id}</div>
                            <div className="text-[10px] text-slate-400">{item.target_type}</div>
                          </div>
                        </div>
                        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-3 text-center text-[11px] text-slate-500 bg-slate-900/40 rounded-lg border border-slate-800/50">
                    No downstream multi-hop impacts detected.
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-6 text-slate-500 space-y-2">
              <Layers className="w-8 h-8 opacity-40 text-indigo-400" />
              <p className="text-xs">Click any node in the graph viewport to inspect properties and 3+ hop downstream impact chain.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
