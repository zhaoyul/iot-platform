import React, { useEffect, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface PLCVisualizerProps {
  programId: string;
}

interface LadderRung {
  id: string;
  inputs: Array<{
    tag: string;
    normallyOpen: boolean;
    type: string;
  }>;
  outputs: Array<{
    tag: string;
    type: string;
  }>;
  logic: string;
}

export const PLCVisualizer: React.FC<PLCVisualizerProps> = ({ programId }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPLCProgram();
  }, [programId]);

  const fetchPLCProgram = async () => {
    try {
      setLoading(true);
      
      // 模拟梯形图数据
      const mockRungs: LadderRung[] = [
        {
          id: 'rung-1',
          inputs: [
            { tag: 'START_BTN', normallyOpen: true, type: 'contact' },
            { tag: 'EMERGENCY_STOP', normallyOpen: false, type: 'contact' },
          ],
          outputs: [
            { tag: 'MOTOR_RUN', type: 'coil' },
          ],
          logic: 'AND',
        },
        {
          id: 'rung-2',
          inputs: [
            { tag: 'SENSOR_1', normallyOpen: true, type: 'contact' },
            { tag: 'TIMER_1.DN', normallyOpen: true, type: 'contact' },
          ],
          outputs: [
            { tag: 'VALVE_OPEN', type: 'coil' },
          ],
          logic: 'AND',
        },
      ];

      const { nodes: ladderNodes, edges: ladderEdges } = renderLadderDiagram(mockRungs);
      setNodes(ladderNodes);
      setEdges(ladderEdges);
    } catch (error) {
      console.error('Failed to fetch PLC program:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderLadderDiagram = (rungs: LadderRung[]) => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];
    const rungHeight = 150;
    const elementWidth = 120;

    rungs.forEach((rung, rungIndex) => {
      const y = rungIndex * rungHeight + 50;
      
      // 左电源线
      nodes.push({
        id: `power-left-${rungIndex}`,
        type: 'default',
        position: { x: 50, y },
        data: { label: '|' },
        style: {
          background: '#333',
          color: 'white',
          border: 'none',
          width: '20px',
          height: '80px',
        },
      });

      let xOffset = 100;

      // 输入触点
      rung.inputs.forEach((input, inputIndex) => {
        const nodeId = `${rung.id}-input-${inputIndex}`;
        nodes.push({
          id: nodeId,
          type: 'default',
          position: { x: xOffset, y },
          data: {
            label: (
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                  {input.normallyOpen ? '| |' : '|/|'}
                </div>
                <div style={{ fontSize: '10px' }}>{input.tag}</div>
              </div>
            ),
          },
          style: {
            background: '#E8F5E9',
            border: '2px solid #4CAF50',
            borderRadius: '4px',
            padding: '8px',
            minWidth: `${elementWidth}px`,
          },
        });

        // 连接到前一个元素
        const sourceId = inputIndex === 0 
          ? `power-left-${rungIndex}` 
          : `${rung.id}-input-${inputIndex - 1}`;
        
        edges.push({
          id: `${sourceId}-${nodeId}`,
          source: sourceId,
          target: nodeId,
          type: 'smoothstep',
          style: { stroke: '#333', strokeWidth: 2 },
        });

        xOffset += elementWidth + 30;
      });

      // 输出线圈
      rung.outputs.forEach((output, outputIndex) => {
        const nodeId = `${rung.id}-output-${outputIndex}`;
        nodes.push({
          id: nodeId,
          type: 'default',
          position: { x: xOffset, y },
          data: {
            label: (
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '20px', fontWeight: 'bold' }}>( )</div>
                <div style={{ fontSize: '10px' }}>{output.tag}</div>
              </div>
            ),
          },
          style: {
            background: '#FFF3E0',
            border: '2px solid #FF9800',
            borderRadius: '4px',
            padding: '8px',
            minWidth: `${elementWidth}px`,
          },
        });

        // 连接到最后一个输入
        const sourceId = rung.inputs.length > 0
          ? `${rung.id}-input-${rung.inputs.length - 1}`
          : `power-left-${rungIndex}`;
        
        edges.push({
          id: `${sourceId}-${nodeId}`,
          source: sourceId,
          target: nodeId,
          type: 'smoothstep',
          style: { stroke: '#333', strokeWidth: 2 },
        });

        xOffset += elementWidth + 30;
      });

      // 右电源线
      nodes.push({
        id: `power-right-${rungIndex}`,
        type: 'default',
        position: { x: xOffset, y },
        data: { label: '|' },
        style: {
          background: '#333',
          color: 'white',
          border: 'none',
          width: '20px',
          height: '80px',
        },
      });

      // 连接到右电源线
      if (rung.outputs.length > 0) {
        edges.push({
          id: `${rung.id}-output-${rung.outputs.length - 1}-power-right-${rungIndex}`,
          source: `${rung.id}-output-${rung.outputs.length - 1}`,
          target: `power-right-${rungIndex}`,
          type: 'smoothstep',
          style: { stroke: '#333', strokeWidth: 2 },
        });
      }
    });

    return { nodes, edges };
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading PLC program...</div>;
  }

  return (
    <div style={{ width: '100%', height: '600px', background: '#fafafa' }}>
      <div style={{ padding: '10px', background: '#333', color: 'white' }}>
        <h3 style={{ margin: 0 }}>PLC Ladder Logic Diagram</h3>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={true}
      >
        <Controls />
        <Background color="#ddd" gap={16} />
      </ReactFlow>
    </div>
  );
};

export default PLCVisualizer;
