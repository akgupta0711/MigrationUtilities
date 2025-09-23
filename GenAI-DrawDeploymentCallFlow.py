import csv
from graphviz import Digraph

def create_call_flow_from_csv(csv_file_path, output_file_path):
    """
    Creates a visual call flow diagram from a CSV file.
    
    Args:
        csv_file_path (str): The path to the input CSV file.
        output_file_path (str): The name for the output image file (e.g., 'call_flow').
    """
    csv_file_path = '/Users/akgupta/Downloads/AI/CallFlow.csv'
    output_file_path = '/Users/akgupta/Downloads/AI/call_flow_diagram'

    dot = Digraph(comment='Call Flow')
    
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        
        nodes = {}
        for row in reader:
            node_id = row['id']
            nodes[node_id] = row
            
            # Create a node based on the 'type' column
            node_type = row['type'].lower()
            if node_type == 'start' or node_type == 'end':
                dot.node(node_id, row['text'], shape='ellipse')
            elif node_type == 'decision':
                #dot.node(node_id, row['text'], shape='diamond')
                dot.node(node_id, "Press 1 for Sales" + '\n' + "2 for Support", shape='diamond')
            else:
                dot.node(node_id, row['text'], shape='box')

        # Create the edges (connections)
        for node_id, row in nodes.items():
            if row.get('next_step_id'):
                dot.edge(node_id, row['next_step_id'])
            
            # Handle decision-specific connections
            if row.get('decision_next_id'):
                dot.edge(node_id, row['decision_next_id'], label='2')
                dot.edge(node_id, row['next_step_id'], label='1')

    # Render the graph to a file
    dot.render(output_file_path, format='jpeg', view=True)

if __name__ == "__main__":
    create_call_flow_from_csv('call_flow.csv', 'call_flow_diagram')

