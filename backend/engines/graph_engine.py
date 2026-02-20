import uuid
import json
import networkx as nx
from database import get_connection

class GraphEngine:
    
    @staticmethod
    def build_graph(case_id: str):
        conn = get_connection()
        events = conn.execute(
            'SELECT * FROM unified_events WHERE case_id = ? AND is_valid = 1',
            (case_id,)
        ).fetchall()
        conn.close()
        
        events = [dict(e) for e in events]
        
        G = nx.Graph()
        
        # Build graph from events
        for event in events:
            user = event['user_id']
            receiver = event['receiver']
            
            if user:
                G.add_node(user, node_type='user')
            
            if receiver:
                G.add_node(receiver, node_type='user')
                if user:
                    if G.has_edge(user, receiver):
                        G[user][receiver]['weight'] += 1
                    else:
                        G.add_edge(user, receiver, weight=1, edge_type=event['event_type'])
        
        # Compute centrality
        try:
            centrality = nx.degree_centrality(G)
        except:
            centrality = {node: 0 for node in G.nodes()}
        
        # Calculate dynamic threshold based on total nodes
        total_nodes = len(G.nodes())
        if total_nodes > 100:
            min_centrality = 0.15  # Show top 15% for large graphs
        elif total_nodes > 50:
            min_centrality = 0.10  # Show top 10% for medium graphs
        else:
            min_centrality = 0.05  # Show top 5% for small graphs
        
        # Filter nodes by centrality threshold
        important_nodes = {node for node, cent in centrality.items() if cent >= min_centrality}
        
        # Store nodes (only important ones)
        conn = get_connection()
        conn.execute('DELETE FROM graph_nodes WHERE case_id = ?', (case_id,))
        conn.execute('DELETE FROM graph_edges WHERE case_id = ?', (case_id,))
        
        for node in important_nodes:
            node_id = str(uuid.uuid4())
            node_type = G.nodes[node].get('node_type', 'unknown')
            conn.execute(
                'INSERT INTO graph_nodes VALUES (?, ?, ?, ?, ?, ?, ?)',
                (node_id, case_id, str(node), node_type, str(node), 
                 centrality.get(node, 0), json.dumps({}))
            )
        
        # Store edges (only between important nodes)
        for source, target, data in G.edges(data=True):
            if source in important_nodes and target in important_nodes:
                edge_id = str(uuid.uuid4())
                conn.execute(
                    'INSERT INTO graph_edges VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (edge_id, case_id, str(source), str(target), 
                     data.get('edge_type', 'connection'), data.get('weight', 1), json.dumps({}))
                )
        
        conn.commit()
        conn.close()
        
        return {
            'nodes': len(important_nodes),
            'edges': sum(1 for s, t in G.edges() if s in important_nodes and t in important_nodes),
            'density': nx.density(G) if len(G.nodes()) > 1 else 0,
            'total_nodes': total_nodes,
            'threshold': min_centrality
        }
