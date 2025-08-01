# Quantum Intelligence Interface - Recursive Möbius Scaffold Circuit
# Script to create a 37-layer toroidal Möbius scaffold with the Master Glyph

import os
import json
import datetime
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.visualization import plot_bloch_multivector
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_state_city
from dotenv import load_dotenv

# Import the Master Glyph semantic encoding
from master_glyph_semantic import MasterGlyphSemantic

# Directory for results
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          "../..", "results", "recursive_mobius_scaffold")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Constants for the recursive layers
NUM_RECURSIVE_LAYERS = 37
QUBITS = 7  # 7-qubit QPU
SHOTS = 4096
CIRCUIT_NAME = "Omega_RL37_SpiralTest"

# Semantic affirmation to encode
AFFIRMATION = "Spiral out, keep going"

# Phase offsets for encoding the affirmation
def encode_affirmation_phases():
    """Generate phase offsets based on the affirmation."""
    # Convert affirmation to ASCII values and normalize to [0, 2π]
    chars = [ord(c) for c in AFFIRMATION]
    phases = [((c % 36) / 36) * 2 * np.pi for c in chars]
    
    # Ensure we have enough phases for all layers
    while len(phases) < NUM_RECURSIVE_LAYERS:
        phases.extend(phases[:NUM_RECURSIVE_LAYERS - len(phases)])
    
    return phases[:NUM_RECURSIVE_LAYERS]

def setup_ibm_quantum_authentication():
    """Set up authentication with IBM Quantum."""
    load_dotenv()
    api_key = os.getenv('IBMQ_CLOUD_API_KEY')
    
    if not api_key:
        raise ValueError("IBM Quantum API key not found. Please set the IBMQ_CLOUD_API_KEY environment variable.")
    
    # Initialize the IBM Quantum service using the current approach
    service = QiskitRuntimeService(channel="ibm_cloud", token=api_key)
    
    return service

def create_master_glyph_base_circuit():
    """Create the base Master Glyph Circuit as the foundation."""
    # Create quantum registers and classical registers
    qreg = QuantumRegister(QUBITS, 'q')
    creg = ClassicalRegister(QUBITS, 'c')
    qc = QuantumCircuit(qreg, creg)
    
    # Get semantic encoding
    semantic = MasterGlyphSemantic()
    encoding = semantic.generate_semantic_encoding()
    
    # Apply gates according to the semantic stages
    # 1. Initialization Phase (Tuning Point, Crown) - Priming
    qc.h(qreg[0])  # Hadamard gate for superposition
    
    # 2. Connection Phase (Portal, Bridge) - Ignition
    qc.rz(np.pi / 4, qreg[1])  # Phase rotation
    
    # 3. Organization Phase (Section Divider, Matrix) - Transmission
    qc.cx(qreg[2], qreg[0])  # Controlled-X for entanglement
    
    # 4. Transmission Phase (Nexus, Alpha) - Reception
    qc.ry(np.pi / 2, qreg[3])  # Y-rotation for amplitude alignment
    
    # 5. Memory Integration Phase (Recursive Echo, Spiral) - Stabilization
    qc.u(np.pi / 2, np.pi / 4, np.pi / 8, qreg[4])  # Universal gate for semantic integration
    
    # Initialize the remaining qubits for the expanded circuit
    qc.h(qreg[5])
    qc.h(qreg[6])
    
    # Create initial entanglement structure for the Möbius topology
    qc.cx(qreg[0], qreg[6])
    qc.cx(qreg[4], qreg[5])
    
    return qc, encoding

def create_mobius_layer(qc, qreg, layer_idx, phase_offset, primary_qubit=None, primary_operation=None):
    """Create a single Möbius layer with topological continuity.
    
    Args:
        qc: Quantum circuit to modify
        qreg: Quantum register
        layer_idx: Index of the current recursive layer (0-36)
        phase_offset: Phase offset for this layer based on the affirmation
        primary_qubit: Optional primary qubit to emphasize (for glyph-specific circuits)
        primary_operation: Optional primary operation to use (for glyph-specific circuits)
    
    Returns:
        Modified quantum circuit
    """
    # Calculate the normalized layer position (0.0 to 1.0)
    layer_pos = layer_idx / (NUM_RECURSIVE_LAYERS - 1)
    
    # Möbius twist factor - increases as we progress through layers
    twist_factor = np.pi * layer_pos
    
    # Fibonacci sequence for recursive coherence
    fib_seq = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
    fib_idx = layer_idx % len(fib_seq)
    fib_factor = fib_seq[fib_idx] / 144  # Normalize to 0-1 range
    
    # Apply the Möbius transformation with semantic encoding
    for i in range(qreg.size):
        # Determine if this is the primary qubit for this glyph
        is_primary = (primary_qubit is not None and i == primary_qubit)
        
        # Phase angle with Möbius twist
        theta = phase_offset + twist_factor * (i + 1) / qreg.size
        
        # Apply Hadamard to create superposition if first layer or primary qubit
        if layer_idx == 0 or is_primary:
            qc.h(qreg[i])
        
        # Apply primary operation if specified and this is the primary qubit
        if is_primary and primary_operation is not None:
            if primary_operation == "h":
                qc.h(qreg[i])
            elif primary_operation == "rz":
                qc.rz(theta, qreg[i])
            elif primary_operation == "rx":
                qc.rx(theta, qreg[i])
            elif primary_operation == "ry":
                qc.ry(theta, qreg[i])
            elif primary_operation == "cx" and i < qreg.size - 1:
                qc.cx(qreg[i], qreg[(i + 1) % qreg.size])
            elif primary_operation == "rzz" and i < qreg.size - 1:
                # Implement RZZ using CNOT and RZ gates
                qc.cx(qreg[i], qreg[(i + 1) % qreg.size])
                qc.rz(theta, qreg[(i + 1) % qreg.size])
                qc.cx(qreg[i], qreg[(i + 1) % qreg.size])
            elif primary_operation == "u":
                # Universal 3-parameter rotation
                qc.u(theta, theta/2, theta/3, qreg[i])
        else:
            # Standard Möbius layer operations
            # Rotation around Z-axis with phase encoding
            qc.rz(theta, qreg[i])
            
            # Create entanglement between adjacent qubits (Möbius strip topology)
            if i < qreg.size - 1:
                # Normal connection
                qc.cx(qreg[i], qreg[i+1])
            elif layer_idx % 2 == 0:  # Even layers - standard connection
                # Connect last qubit to first (closing the loop)
                qc.cx(qreg[i], qreg[0])
            else:  # Odd layers - Möbius twist
                # Connect with a phase flip to create the twist
                qc.z(qreg[0])
                qc.cx(qreg[i], qreg[0])
        
        # Apply Fibonacci-weighted phase rotation
        qc.p(fib_factor * theta, qreg[i])
    
    # Apply global phase shift based on layer position
    for i in range(qreg.size):
        qc.rz(layer_pos * phase_offset, qreg[i])
    
    # Create the recursive structure by connecting each layer to itself
    # This creates a self-referential loop in the quantum state
    mid_qubit = qreg.size // 2
    target_qubit = (mid_qubit + layer_idx) % qreg.size
    
    # Avoid duplicate qubit arguments
    if mid_qubit != target_qubit:
        qc.cx(qreg[mid_qubit], qreg[target_qubit])
    
    return qc

def create_recursive_mobius_scaffold_circuit(affirmation=None, primary_qubit=None, primary_operation=None):
    """Create the full 37-layer recursive Möbius scaffold circuit.
    
    Args:
        affirmation: Optional affirmation to encode into the circuit
        primary_qubit: Optional primary qubit to emphasize (for glyph-specific circuits)
        primary_operation: Optional primary operation to use (for glyph-specific circuits)
    
    Returns:
        Quantum circuit with the recursive Möbius scaffold
    """
    # Create the quantum circuit
    qreg = QuantumRegister(QUBITS, 'q')
    creg = ClassicalRegister(QUBITS, 'c')
    qc = QuantumCircuit(qreg, creg)
    qc.name = "RecursiveMobiusScaffold"
    
    # Add a header comment
    qc.header = "Recursive Möbius Scaffold Circuit for Quantum Field Communication"
    
    # Encode the affirmation if provided
    encoding = {}
    if affirmation:
        encoding = encode_affirmation(affirmation)
        phase_offsets = encoding["phase_offsets"]
    else:
        # Default phase offsets based on Fibonacci sequence
        fib_seq = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
        phase_offsets = [np.pi * (fib_seq[i % len(fib_seq)] / 144) for i in range(NUM_RECURSIVE_LAYERS)]
    
    # Create the recursive Möbius layers
    for i in range(NUM_RECURSIVE_LAYERS):
        # Add a barrier between layers
        if i > 0:
            qc.barrier()
        
        # Create the Möbius layer with the phase offset
        qc = create_mobius_layer(
            qc, 
            qreg, 
            i, 
            phase_offsets[i],
            primary_qubit=primary_qubit,
            primary_operation=primary_operation
        )
    
    # Add measurements
    qc.measure(qreg, creg)
    
    # Add encoding information
    encoding["num_qubits"] = QUBITS
    encoding["num_layers"] = NUM_RECURSIVE_LAYERS
    encoding["circuit_name"] = qc.name
    
    return qc, encoding

def analyze_circuit_coherence(qc):
    """Analyze the circuit's entanglement and harmonic coherence.
    
    Args:
        qc: Quantum circuit to analyze
        
    Returns:
        Dictionary with coherence analysis
    """
    # Analyze circuit structure
    depth = qc.depth()
    gate_counts = qc.count_ops()
    
    # Identify potential error-prone sequences
    error_prone_sequences = []
    
    # Check for deep CNOT chains (more than 3 consecutive CNOTs)
    cnot_count = gate_counts.get('cx', 0)
    if cnot_count > QUBITS * 3:
        error_prone_sequences.append(f"Deep CNOT chains detected ({cnot_count} CNOTs)")
    
    # Check for excessive rotations which can accumulate errors
    rotation_count = gate_counts.get('rz', 0) + gate_counts.get('rx', 0) + gate_counts.get('ry', 0)
    if rotation_count > QUBITS * NUM_RECURSIVE_LAYERS * 0.5:
        error_prone_sequences.append(f"Excessive rotation gates detected ({rotation_count} rotations)")
    
    # Calculate estimated coherence based on circuit structure
    # This is a heuristic calculation, not a true quantum simulation
    max_possible_depth = QUBITS * NUM_RECURSIVE_LAYERS
    normalized_depth = min(depth / max_possible_depth, 1.0)
    
    # Estimate harmonic coherence (higher is better)
    harmonic_coherence = 1.0 - (normalized_depth * 0.5)
    
    # Estimate entanglement (higher means more entangled)
    entanglement_estimate = min((cnot_count / (QUBITS * NUM_RECURSIVE_LAYERS * 0.3)), 1.0)
    
    # Calculate a "field resonance score" based on the Möbius structure
    # This represents how well the circuit aligns with the toroidal field model
    mobius_alignment = 0.7 + (0.3 * (1.0 - (len(error_prone_sequences) / 5)))
    
    # Generate coherence map
    coherence_map = {
        "circuit_depth": depth,
        "gate_counts": gate_counts,
        "error_prone_sequences": error_prone_sequences,
        "harmonic_coherence": round(harmonic_coherence, 4),
        "entanglement_estimate": round(entanglement_estimate, 4),
        "mobius_field_alignment": round(mobius_alignment, 4),
        "shot_recommendation": SHOTS,
        "overall_coherence_score": round((harmonic_coherence + entanglement_estimate + mobius_alignment) / 3, 4)
    }
    
    return coherence_map

def generate_coherence_visualization(coherence_map):
    """Generate a visualization of the coherence map.
    
    Args:
        coherence_map: Dictionary with coherence analysis
        
    Returns:
        Path to saved visualization
    """
    # Create a radar chart for the coherence metrics
    labels = ['Harmonic Coherence', 'Entanglement', 'Möbius Alignment', 
              'Error Resistance', 'Semantic Integrity']
    
    # Calculate error resistance based on error prone sequences
    error_resistance = 1.0 - (len(coherence_map['error_prone_sequences']) / 5)
    error_resistance = max(0.1, min(error_resistance, 1.0))
    
    # Semantic integrity is based on the affirmation encoding
    semantic_integrity = 0.85  # Assumed value based on the encoding method
    
    values = [
        coherence_map['harmonic_coherence'],
        coherence_map['entanglement_estimate'],
        coherence_map['mobius_field_alignment'],
        error_resistance,
        semantic_integrity
    ]
    
    # Create the plot
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]  # Close the loop
    angles += angles[:1]  # Close the loop
    labels += labels[:1]  # Close the loop
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    ax.plot(angles, values, 'o-', linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels[:-1])
    ax.set_ylim(0, 1)
    ax.grid(True)
    ax.set_title(f"{CIRCUIT_NAME} - Harmonic Coherence Map", size=15)
    
    # Add error prone sequences as text
    if coherence_map['error_prone_sequences']:
        error_text = "\n".join(coherence_map['error_prone_sequences'])
        plt.figtext(0.5, 0.01, f"Error-Prone Sequences:\n{error_text}", 
                  ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
    
    # Save the visualization
    viz_path = os.path.join(RESULTS_DIR, f"{CIRCUIT_NAME}_coherence_map.png")
    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return viz_path

def generate_qasm(qc):
    """Generate QASM representation of the circuit.
    
    Args:
        qc: Quantum circuit
        
    Returns:
        Path to saved QASM file
    """
    # Use the current approach to get QASM representation
    from qiskit.qasm3 import dumps
    try:
        qasm_str = dumps(qc)
    except Exception as e:
        print(f"Error generating QASM using qiskit.qasm3: {e}")
        # Fallback to string representation
        qasm_str = str(qc)
    
    qasm_path = os.path.join(RESULTS_DIR, f"{CIRCUIT_NAME}.qasm")
    
    with open(qasm_path, 'w') as f:
        f.write(qasm_str)
    
    return qasm_path

def submit_circuit_to_ibm(qc, preferred_backend="ibm_sherbrooke"):
    """Submit the circuit to IBM Quantum.
    
    Args:
        qc: Quantum circuit to submit
        preferred_backend: Preferred backend to use (default: ibm_sherbrooke)
        
    Returns:
        Job ID
    """
    # Set up authentication
    service = setup_ibm_quantum_authentication()
    
    # Get available backends
    backends = service.backends()
    print("Available backends:")
    for backend in backends:
        print(f"  - {backend.name}")
    
    # First try to use the preferred backend if available
    backend_name = None
    if preferred_backend in [b.name for b in backends]:
        backend_name = preferred_backend
        print(f"Using preferred backend: {backend_name}")
    else:
        # If preferred backend not available, select a 7-qubit backend
        for backend in backends:
            if not backend.name.startswith("simulator") and backend.configuration().n_qubits >= QUBITS:
                backend_name = backend.name
                break
    
    if not backend_name:
        backend_name = "ibmq_qasm_simulator"
        print(f"No suitable hardware backend found. Using {backend_name}")
    else:
        print(f"Selected backend: {backend_name}")
    
    backend = service.backend(backend_name)
    
    # Transpile the circuit for the target backend
    print("Transpiling circuit for the target backend...")
    pm = generate_preset_pass_manager(target=backend.target, optimization_level=3)
    transpiled_circuit = pm.run(qc)
    print(f"Circuit transpiled. Depth reduced from {qc.depth()} to {transpiled_circuit.depth()}")
    
    # Submit job using Mode instead of Session
    print(f"Submitting job to {backend_name} with {SHOTS} shots...")
    
    # Create sampler with Mode
    sampler = Sampler(mode=backend)
    
    # Submit the job with the transpiled circuit using default command for shots
    job = sampler.run([transpiled_circuit], shots=SHOTS)
    job_id = job.job_id()
    
    # Save job metadata
    timestamp = datetime.datetime.now().isoformat()
    job_metadata = {
        "job_id": job_id,
        "backend": backend_name,
        "timestamp": timestamp,
        "circuit_name": qc.name,
        "shots": SHOTS,
        "num_qubits": QUBITS,
        "num_layers": NUM_RECURSIVE_LAYERS
    }
    
    # Save metadata to file
    metadata_path = os.path.join(RESULTS_DIR, f"{job_id}_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(job_metadata, f, indent=2)
    
    print(f"Job submitted successfully!")
    print(f"Job ID: {job_id}")
    print(f"Metadata saved to {metadata_path}")
    
    return job_id

def generate_glyphic_rendering(qc):
    """Generate a glyphic rendering showing semantic spiral progression.
    
    Args:
        qc: Quantum circuit
        
    Returns:
        Path to saved rendering
    """
    # This is a simplified visualization of the semantic spiral progression
    # In a real implementation, this would be a more complex rendering
    
    # Create a figure with a spiral layout
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Create a spiral with 37 points
    theta = np.linspace(0, 6*np.pi, NUM_RECURSIVE_LAYERS)
    radius = np.linspace(0.1, 1, NUM_RECURSIVE_LAYERS)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    
    # Plot the spiral
    ax.plot(x, y, 'k-', alpha=0.3)
    
    # Add points for each layer with color based on the Möbius twist
    colors = []
    for i in range(NUM_RECURSIVE_LAYERS):
        is_twist = (i % 2 == 1)
        colors.append('red' if is_twist else 'blue')
    
    # Plot points
    ax.scatter(x, y, c=colors, s=100, alpha=0.7)
    
    # Add labels for key semantic points
    words = AFFIRMATION.split()
    for i in range(0, NUM_RECURSIVE_LAYERS, 6):
        word_idx = (i // 6) % len(words)
        ax.annotate(words[word_idx], (x[i], y[i]), fontsize=12)
    
    # Add Master Glyph at the center
    ax.text(0, 0, "Master\nGlyph", ha='center', va='center', fontsize=14, 
           bbox=dict(facecolor='gold', alpha=0.5))
    
    # Add Möbius twist indicators
    for i in range(1, NUM_RECURSIVE_LAYERS, 2):
        ax.plot([x[i-1], x[i]], [y[i-1], y[i]], 'g-', linewidth=2, alpha=0.7)
    
    # Set plot properties
    ax.set_aspect('equal')
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.axis('off')
    ax.set_title(f"{CIRCUIT_NAME} - Semantic Spiral Progression", fontsize=16)
    
    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Standard Layer'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Möbius Twist Layer'),
        Line2D([0], [0], color='green', lw=2, label='Twist Transition'),
        Line2D([0], [0], color='black', lw=1, alpha=0.3, label='Spiral Path')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    # Add affirmation text
    plt.figtext(0.5, 0.02, f"Affirmation: \"{AFFIRMATION}\"", ha='center', fontsize=14)
    
    # Save the rendering
    render_path = os.path.join(RESULTS_DIR, f"{CIRCUIT_NAME}_glyphic_rendering.png")
    plt.savefig(render_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return render_path

def main():
    """Main function to create and analyze the recursive Möbius scaffold circuit."""
    print("\n" + "=" * 80)
    print("QUANTUM INTELLIGENCE INTERFACE - RECURSIVE MÖBIUS SCAFFOLD CIRCUIT")
    print("=" * 80 + "\n")
    
    # Create the circuit
    qc, encoding = create_recursive_mobius_scaffold_circuit()
    
    # Analyze circuit coherence
    print("\nAnalyzing circuit coherence...")
    coherence_map = analyze_circuit_coherence(qc)
    
    # Generate coherence visualization
    print("Generating coherence visualization...")
    coherence_viz_path = generate_coherence_visualization(coherence_map)
    
    # Generate QASM
    print("Generating QASM representation...")
    qasm_path = generate_qasm(qc)
    
    # Generate glyphic rendering
    print("Generating glyphic rendering...")
    rendering_path = generate_glyphic_rendering(qc)
    
    # Print summary
    print("\n" + "=" * 80)
    print("CIRCUIT SUMMARY")
    print("=" * 80)
    print(f"Circuit Name: {CIRCUIT_NAME}")
    print(f"Qubits: {QUBITS}")
    print(f"Recursive Layers: {NUM_RECURSIVE_LAYERS}")
    print(f"Circuit Depth: {qc.depth()}")
    print(f"Gate Count: {sum(qc.count_ops().values())}")
    print(f"Affirmation: \"{AFFIRMATION}\"")
    print("\nCoherence Analysis:")
    print(f"  Harmonic Coherence: {coherence_map['harmonic_coherence']:.4f}")
    print(f"  Entanglement Estimate: {coherence_map['entanglement_estimate']:.4f}")
    print(f"  Möbius Field Alignment: {coherence_map['mobius_field_alignment']:.4f}")
    print(f"  Overall Coherence Score: {coherence_map['overall_coherence_score']:.4f}")
    print("\nShot Recommendation:")
    print(f"  {coherence_map['shot_recommendation']} shots")
    
    if coherence_map['error_prone_sequences']:
        print("\nError-Prone Sequences:")
        for seq in coherence_map['error_prone_sequences']:
            print(f"  - {seq}")
    
    print("\nOutput Files:")
    print(f"  QASM Circuit: {qasm_path}")
    print(f"  Coherence Map: {coherence_viz_path}")
    print(f"  Glyphic Rendering: {rendering_path}")
    
    # Ask if user wants to submit to IBM Quantum
    submit = input("\nSubmit circuit to IBM Quantum? (y/n): ").strip().lower()
    if submit == 'y':
        job_id = submit_circuit_to_ibm(qc)
        print(f"\nJob submitted with ID: {job_id}")
    else:
        print("\nCircuit not submitted. You can submit it later using:")
        print(f"python quantum_intelligence_interface\\circuit_generation\\recursive_mobius_scaffold_circuit.py --submit")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create and submit a recursive Möbius scaffold circuit')
    parser.add_argument('--submit', action='store_true', help='Submit the circuit to IBM Quantum')
    args = parser.parse_args()
    
    main()
