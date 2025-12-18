import React, { useEffect, useState, useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface DependencyGraphProps {
  repository: string;
  branch?: string;
}

interface Module {
  id: string;
  name: string;
  type: string;
  dependencies: string[];
  metrics?: {
    lines: number;
    complexity: number;
  };
}

export const DependencyGraph: React.FC<DependencyGraphProps> = ({
  repository,
  branch = 'main'
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDependencyData();
  }, [repository, branch]);

  const fetchDependencyData = async () => {
    try {
      setLoading(true);
      // 实际应该从API获取数据
      // const response = await fetch(`/api/v1/repos/${repository}/dependencies?branch=${branch}`);
      // const data = await response.json();
      
      // 模拟数据
      const mockData = {
        modules: [
          { id: '1', name: 'core', type: 'module', dependencies: [] },
          { id: '2', name: 'api', type: 'module', dependencies: ['1'] },
          { id: '3', name: 'ui', type: 'module', dependencies: ['2'] },
          { id: '4', name: 'plc-parser', type: 'module', dependencies: ['1'] },
          { id: '5', name: 'eda-viewer', type: 'module', dependencies: ['1', '3'] },
        ]
      };

      const graphNodes: Node[] = mockData.modules.map((module, index) => ({
        id: module.id,
        type: 'default',
        position: calculateNodePosition(index, mockData.modules.length),
        data: {
          label: (
            <div style={{ padding: '10px' }}>
              <strong>{module.name}</strong>
              <div style={{ fontSize: '12px', color: '#666' }}>{module.type}</div>
            </div>
          ),
        },
        style: {
          background: getNodeColor(module.type),
          border: '2px solid #222',
          borderRadius: '8px',
          padding: '10px',
        },
      }));

      const graphEdges: Edge[] = [];
      mockData.modules.forEach(module => {
        module.dependencies.forEach(depId => {
          graphEdges.push({
            id: `${module.id}-${depId}`,
            source: depId,
            target: module.id,
            type: 'smoothstep',
            animated: true,
            markerEnd: {
              type: MarkerType.ArrowClosed,
            },
          });
        });
      });

      setNodes(graphNodes);
      setEdges(graphEdges);
    } catch (error) {
      console.error('Failed to fetch dependency data:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateNodePosition = (index: number, total: number) => {
    const radius = 300;
    const angle = (index / total) * 2 * Math.PI;
    return {
      x: 400 + radius * Math.cos(angle),
      y: 300 + radius * Math.sin(angle),
    };
  };

  const getNodeColor = (type: string) => {
    const colors: Record<string, string> = {
      module: '#4A90E2',
      service: '#50C878',
      library: '#F5A623',
      component: '#BD10E0',
    };
    return colors[type] || '#9013FE';
  };

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading dependency graph...</div>;
  }

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Controls />
        <Background color="#aaa" gap={16} />
      </ReactFlow>
    </div>
  );
};

export default DependencyGraph;
