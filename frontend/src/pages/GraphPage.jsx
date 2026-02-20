import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import ReactFlow, { Background, Controls, MiniMap, useNodesState, useEdgesState } from 'reactflow'
import 'reactflow/dist/style.css'
import { Users, TrendingUp, AlertTriangle } from 'lucide-react'
import Card from '../components/Card'
import Loader from '../components/Loader'
import Badge from '../components/Badge'
import { getGraphData } from '../api/cases'

const GraphPage = () => {
  const { id } = useParams()
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [loading, setLoading] = useState(true)
  const [selectedNode, setSelectedNode] = useState(null)
  const [filters, setFilters] = useState({ minWeight: 3, edgeType: '' })
  const [stats, setStats] = useState({ totalNodes: 0, totalEdges: 0, highRisk: 0 })

  useEffect(() => {
    loadGraph()
  }, [id])

  const loadGraph = async () => {
    try {
      const data = await getGraphData(id, filters)
      
      // Filter edges based on minWeight
      const filteredEdges = data.edges?.filter(edge => edge.weight >= filters.minWeight) || []
      
      // Get unique node IDs from filtered edges
      const connectedNodeIds = new Set()
      filteredEdges.forEach(edge => {
        connectedNodeIds.add(edge.source)
        connectedNodeIds.add(edge.target)
      })
      
      // Only show nodes that have connections
      const filteredNodes = data.nodes?.filter(node => connectedNodeIds.has(node.id)) || []
      
      // Calculate layout in a force-directed style
      const centerX = 400
      const centerY = 300
      const radius = 250
      
      const formattedNodes = filteredNodes.map((node, idx) => {
        const centrality = node.centrality || 0
        const angle = (idx / filteredNodes.length) * 2 * Math.PI
        const distance = radius * (1 - centrality * 0.5) // High centrality nodes closer to center
        
        const isHighRisk = centrality > 0.7
        const isMediumRisk = centrality > 0.4
        
        return {
          id: node.id,
          data: { 
            label: node.label,
            centrality: centrality,
            connections: filteredEdges.filter(e => e.source === node.id || e.target === node.id).length
          },
          position: { 
            x: node.x || centerX + Math.cos(angle) * distance, 
            y: node.y || centerY + Math.sin(angle) * distance
          },
          style: {
            background: isHighRisk ? '#7f1d1d' : isMediumRisk ? '#78350f' : '#1e3a8a',
            color: '#fff',
            border: `3px solid ${isHighRisk ? '#ef4444' : isMediumRisk ? '#f59e0b' : '#3b82f6'}`,
            borderRadius: '8px',
            padding: '14px 18px',
            boxShadow: isHighRisk ? '0 0 30px rgba(239, 68, 68, 0.6), 0 0 60px rgba(239, 68, 68, 0.3)' : 
                      isMediumRisk ? '0 0 20px rgba(245, 158, 11, 0.4)' :
                      '0 8px 16px rgba(0,0,0,0.4)',
            fontSize: '14px',
            fontWeight: '700',
            minWidth: '110px',
            textAlign: 'center',
            transition: 'all 0.3s ease'
          }
        }
      })

      const formattedEdges = filteredEdges.map(edge => {
        const isStrong = edge.weight > 10
        const isMedium = edge.weight > 5
        
        return {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: `${edge.weight}`,
          type: 'default',
          animated: isStrong,
          style: { 
            stroke: isStrong ? '#ef4444' : isMedium ? '#f59e0b' : '#6b7280',
            strokeWidth: isStrong ? 4 : isMedium ? 2.5 : 1.5,
            opacity: isStrong ? 1 : isMedium ? 0.7 : 0.4
          },
          labelStyle: { 
            fill: '#fff', 
            fontSize: 12,
            fontWeight: '700',
            background: '#000'
          },
          labelBgStyle: { 
            fill: isStrong ? '#991b1b' : isMedium ? '#92400e' : '#374151',
            fillOpacity: 0.95,
            rx: 6,
            ry: 6
          },
          markerEnd: {
            type: 'arrowclosed',
            width: 20,
            height: 20,
            color: isStrong ? '#ef4444' : isMedium ? '#f59e0b' : '#6b7280'
          }
        }
      })

      setNodes(formattedNodes)
      setEdges(formattedEdges)
      
      // Update stats
      const highRiskCount = formattedNodes.filter(n => n.data.centrality > 0.7).length
      setStats({
        totalNodes: formattedNodes.length,
        totalEdges: formattedEdges.length,
        highRisk: highRiskCount
      })
    } catch (error) {
      console.error('Failed to load graph:', error)
    } finally {
      setLoading(false)
    }
  }

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node)
  }, [])

  if (loading) return <Loader size="lg" />

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Network Intelligence</h1>
        <div className="flex gap-3">
          <div className="flex items-center gap-2 px-4 py-2 bg-dark-card rounded-lg border border-dark-border">
            <Users className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium">{stats.totalNodes} Nodes</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-dark-card rounded-lg border border-dark-border">
            <TrendingUp className="w-4 h-4 text-green-400" />
            <span className="text-sm font-medium">{stats.totalEdges} Connections</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-dark-card rounded-lg border border-dark-border">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <span className="text-sm font-medium">{stats.highRisk} High Risk</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6">
        <div className="col-span-3">
          <Card className="h-[600px] p-0 overflow-hidden">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              fitView
              fitViewOptions={{ padding: 0.3, maxZoom: 1.2 }}
              style={{ background: 'radial-gradient(circle at 50% 50%, #0f0f0f 0%, #0a0a0a 100%)' }}
              nodesDraggable={true}
              nodesConnectable={false}
              elementsSelectable={true}
              minZoom={0.3}
              maxZoom={1.5}
              defaultEdgeOptions={{
                animated: false,
                style: { strokeWidth: 2 }
              }}
            >
              <Background 
                color="#1a1a1a" 
                gap={32} 
                size={2}
                variant="dots"
                style={{ opacity: 0.4 }}
              />
              <Controls 
                style={{ 
                  background: '#111', 
                  border: '1px solid #333',
                  borderRadius: '10px',
                  overflow: 'hidden'
                }} 
                showInteractive={false}
              />
              <MiniMap 
                style={{ 
                  background: '#0a0a0a', 
                  border: '1px solid #333',
                  borderRadius: '10px',
                  overflow: 'hidden'
                }} 
                nodeColor={(node) => {
                  const centrality = node.data?.centrality || 0
                  if (centrality > 0.7) return '#ef4444'
                  if (centrality > 0.4) return '#f59e0b'
                  return '#3b82f6'
                }}
                maskColor="rgba(0, 0, 0, 0.8)"
                nodeStrokeWidth={3}
              />
            </ReactFlow>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <h3 className="font-semibold mb-4">Filters</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm mb-2">Min Weight</label>
                <input
                  type="number"
                  value={filters.minWeight}
                  onChange={(e) => setFilters({ ...filters, minWeight: e.target.value })}
                  className="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm mb-2">Edge Type</label>
                <select
                  value={filters.edgeType}
                  onChange={(e) => setFilters({ ...filters, edgeType: e.target.value })}
                  className="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm"
                >
                  <option value="">All</option>
                  <option value="communication">Communication</option>
                  <option value="transaction">Transaction</option>
                </select>
              </div>
              <button onClick={loadGraph} className="btn-primary w-full text-sm">
                Apply
              </button>
            </div>
          </Card>

          {selectedNode && (
            <Card>
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Node Intelligence</h3>
                <Badge variant={selectedNode.data.centrality > 0.7 ? 'danger' : selectedNode.data.centrality > 0.4 ? 'warning' : 'info'}>
                  {selectedNode.data.centrality > 0.7 ? 'High Risk' : selectedNode.data.centrality > 0.4 ? 'Medium' : 'Low Risk'}
                </Badge>
              </div>
              <div className="space-y-3">
                <div className="p-3 bg-dark-bg rounded-lg">
                  <div className="text-xs text-gray-400 mb-1">Node ID</div>
                  <div className="font-mono text-sm font-medium">{selectedNode.id}</div>
                </div>
                <div className="p-3 bg-dark-bg rounded-lg">
                  <div className="text-xs text-gray-400 mb-1">Label</div>
                  <div className="text-sm font-medium">{selectedNode.data.label}</div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-dark-bg rounded-lg">
                    <div className="text-xs text-gray-400 mb-1">Centrality</div>
                    <div className="text-lg font-bold text-blue-400">{(selectedNode.data.centrality || 0).toFixed(3)}</div>
                  </div>
                  <div className="p-3 bg-dark-bg rounded-lg">
                    <div className="text-xs text-gray-400 mb-1">Connections</div>
                    <div className="text-lg font-bold text-green-400">{selectedNode.data.connections || 0}</div>
                  </div>
                </div>
                <div className="p-3 bg-dark-bg rounded-lg">
                  <div className="text-xs text-gray-400 mb-2">Risk Score</div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        selectedNode.data.centrality > 0.7 ? 'bg-red-500' :
                        selectedNode.data.centrality > 0.4 ? 'bg-yellow-500' : 'bg-blue-500'
                      }`}
                      style={{ width: `${(selectedNode.data.centrality || 0) * 100}%` }}
                    />
                  </div>
                  <div className="text-right text-xs text-gray-400 mt-1">{((selectedNode.data.centrality || 0) * 100).toFixed(1)}%</div>
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default GraphPage
