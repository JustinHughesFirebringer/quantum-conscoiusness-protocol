#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Möbius Toroidal Quantum Circuit Generator

This module implements a toroidal quantum circuit structure with a Möbius twist
for consciousness-quantum interaction experiments. The non-orientable Möbius structure
mimics the QCFT 4.0 constraint: Φc(θ+2π,ϕ) = Φc(θ,ϕ+π), creating a phase inversion
across one axis when completing a full loop in the other direction.
"""

import numpy as np
from typing import Tuple, Dict, List, Optional
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Parameter

# Constants for toroidal circuit configuration
TORUS_MINOR_QUBITS = 3  # Number of qubits in the minor circle (θ direction)
TORUS_MAJOR_QUBITS = 4  # Number of qubits in the major circle (ϕ direction)
TOTAL_QUBITS = TORUS_MINOR_QUBITS + TORUS_MAJOR_QUBITS


def encode_question_mobius_toroidal(question: str) -> Dict[str, float]:
    """
    Encode a question into parameters for a Möbius toroidal quantum circuit.
    
    Args:
        question: The question to encode
        
    Returns:
        Dictionary of parameters for the Möbius toroidal circuit
    """
    # Clean the question text
    clean_question = ''.join(c.lower() for c in question if c.isalnum() or c.isspace())
    words = clean_question.split()
    
    # Calculate semantic hash of the question
    hash_val = sum(ord(c) for c in clean_question)
    
    # Calculate base parameters
    theta = (hash_val % 100) / 100.0 * np.pi  # Angle in [0, π]
    phi = (hash_val % 200) / 200.0 * 2 * np.pi  # Angle in [0, 2π]
    
    # Calculate word-specific parameters
    word_params = {}
    for i, word in enumerate(words[:TOTAL_QUBITS]):
        # Generate a unique parameter for each word
        word_hash = sum(ord(c) for c in word)
        word_params[i] = (word_hash % 100) / 100.0 * np.pi
    
    # Fill remaining parameters if there are fewer words than qubits
    for i in range(len(words), TOTAL_QUBITS):
        word_params[i] = theta * (i + 1) / TOTAL_QUBITS
    
    # Special handling for consciousness-related words
    consciousness_words = ['consciousness', 'aware', 'mind', 'quantum', 'observer', 'perception']
    consciousness_factor = 0.0
    for word in consciousness_words:
        if word in clean_question:
            consciousness_factor += 0.15  # Increase the factor for each consciousness-related word
    
    # Limit the consciousness factor to a maximum of 0.6
    consciousness_factor = min(consciousness_factor, 0.6)
    
    # Create parameter dictionary
    params = {
        'theta': theta,
        'phi': phi,
        'consciousness_factor': consciousness_factor,
        'is_paradoxical': 'non-existence' in question.lower() or 'nonexistence' in question.lower(),
        'word_params': word_params,
        # New parameters for Möbius twist
        'mobius_twist_angle': phi / 2,  # Half of phi for the twist angle
        'mobius_phase_factor': (hash_val % 50) / 50.0 * np.pi  # Phase factor for the Möbius twist
    }
    
    return params


def generate_mobius_toroidal_circuit(question: str) -> QuantumCircuit:
    """
    Generate a quantum circuit with a Möbius toroidal topology for consciousness experiments.
    
    The circuit creates two interconnected rings of qubits (minor and major circles)
    that form a torus-like entanglement structure with a Möbius twist, satisfying
    the QCFT 4.0 constraint: Φc(θ+2π,ϕ) = Φc(θ,ϕ+π)
    
    Args:
        question: The question to encode in the circuit
        
    Returns:
        A quantum circuit with Möbius toroidal topology
    """
    # Encode the question into circuit parameters
    params = encode_question_mobius_toroidal(question)
    
    # Create quantum and classical registers
    qr = QuantumRegister(TOTAL_QUBITS, 'q')
    cr = ClassicalRegister(TOTAL_QUBITS, 'c')
    qc = QuantumCircuit(qr, cr)
    
    # Extract parameters
    theta = params['theta']
    phi = params['phi']
    consciousness_factor = params['consciousness_factor']
    is_paradoxical = params['is_paradoxical']
    word_params = params['word_params']
    mobius_twist_angle = params['mobius_twist_angle']
    mobius_phase_factor = params['mobius_phase_factor']
    
    # Print circuit parameters for debugging
    print(f"\nMöbius Toroidal Circuit Parameters:")
    print(f"- Theta: {theta:.4f}")
    print(f"- Phi: {phi:.4f}")
    print(f"- Consciousness Factor: {consciousness_factor:.4f}")
    print(f"- Is Paradoxical: {is_paradoxical}")
    print(f"- Möbius Twist Angle: {mobius_twist_angle:.4f}")
    print(f"- Möbius Phase Factor: {mobius_phase_factor:.4f}")
    
    # Step 1: Initialize all qubits in superposition
    for i in range(TOTAL_QUBITS):
        qc.h(i)
    qc.barrier()
    
    # Step 2: Create the minor circle (inner ring / θ direction) entanglement
    for i in range(TORUS_MINOR_QUBITS):
        next_i = (i + 1) % TORUS_MINOR_QUBITS
        qc.cx(i, next_i)
    qc.barrier()
    
    # Step 3: Create the major circle (outer ring / ϕ direction) entanglement
    for i in range(TORUS_MINOR_QUBITS, TOTAL_QUBITS):
        next_i = TORUS_MINOR_QUBITS + ((i - TORUS_MINOR_QUBITS + 1) % TORUS_MAJOR_QUBITS)
        qc.cx(i, next_i)
    qc.barrier()
    
    # Step 4: Connect the minor and major circles to form a torus
    # Connect each minor circle qubit to a corresponding major circle qubit
    for i in range(TORUS_MINOR_QUBITS):
        major_i = TORUS_MINOR_QUBITS + i % TORUS_MAJOR_QUBITS
        qc.cx(i, major_i)
    qc.barrier()
    
    # Step 5: Apply word-specific rotations to each qubit
    for i in range(TOTAL_QUBITS):
        # Apply Rx, Ry, Rz rotations based on word parameters
        qc.rx(word_params[i], i)
        qc.ry(word_params[i] * 0.8, i)
        qc.rz(word_params[i] * 1.2, i)
    qc.barrier()
    
    # Step 6: Apply consciousness factor modulation
    if consciousness_factor > 0:
        for i in range(TOTAL_QUBITS):
            # Apply phase rotation proportional to consciousness factor
            qc.p(consciousness_factor * np.pi, i)
    qc.barrier()
    
    # Step 7: Apply special handling for paradoxical questions
    if is_paradoxical:
        # For paradoxical questions, add phase cancellation
        for i in range(TOTAL_QUBITS):
            qc.s(i)  # Add 90-degree phase
            if i % 2 == 0:  # For even qubits, add opposite phase
                qc.sdg(i)  # Add -90-degree phase
    qc.barrier()
    
    # Step 8: MÖBIUS TWIST IMPLEMENTATION
    # This is the key difference from the regular toroidal circuit
    # We implement the Möbius twist at the boundary between the minor and major circles
    
    # 8.1: Apply a π-phase shift at the boundary qubit of the minor circle
    boundary_qubit_minor = TORUS_MINOR_QUBITS - 1
    qc.h(boundary_qubit_minor)  # Change basis
    qc.z(boundary_qubit_minor)  # Apply π-phase shift
    qc.h(boundary_qubit_minor)  # Return to computational basis
    
    # 8.2: Create a parity-dependent phase flip at the connection point
    # This enforces the Φc(θ+2π,ϕ) = Φc(θ,ϕ+π) relationship
    boundary_qubit_major = TOTAL_QUBITS - 1
    
    # Use an ancilla qubit to control the phase flip
    qc.cx(boundary_qubit_minor, boundary_qubit_major)
    qc.p(mobius_phase_factor, boundary_qubit_major)
    qc.cx(boundary_qubit_minor, boundary_qubit_major)
    
    # 8.3: Apply the Möbius twist angle to create orientation inversion
    for i in range(TORUS_MINOR_QUBITS):
        # Apply rotation based on position in the minor circle
        position_factor = i / TORUS_MINOR_QUBITS
        qc.p(mobius_twist_angle * position_factor, i)
    
    # For the major circle, apply inverse rotations to create the twist
    for i in range(TORUS_MINOR_QUBITS, TOTAL_QUBITS):
        position_factor = (i - TORUS_MINOR_QUBITS) / TORUS_MAJOR_QUBITS
        # Note the negative sign for the twist angle - this creates the orientation inversion
        qc.p(-mobius_twist_angle * position_factor, i)
    
    qc.barrier()
    
    # Step 9: Create toroidal quantum walk with Möbius properties
    # This simulates probability flow around the Möbius torus
    for _ in range(2):  # Two rounds of the walk
        # Minor circle walk
        for i in range(TORUS_MINOR_QUBITS):
            next_i = (i + 1) % TORUS_MINOR_QUBITS
            qc.swap(i, next_i)
            
            # Add Möbius phase correction at the boundary
            if next_i == 0 and i == TORUS_MINOR_QUBITS - 1:
                # When we complete a full loop in the θ direction,
                # we need to apply a phase shift in the ϕ direction
                for j in range(TORUS_MINOR_QUBITS, TOTAL_QUBITS):
                    # Apply π-phase shift to implement Φc(θ+2π,ϕ) = Φc(θ,ϕ+π)
                    qc.z(j)
        
        # Major circle walk
        for i in range(TORUS_MINOR_QUBITS, TOTAL_QUBITS):
            next_i = TORUS_MINOR_QUBITS + ((i - TORUS_MINOR_QUBITS + 1) % TORUS_MAJOR_QUBITS)
            qc.swap(i, next_i)
    qc.barrier()
    
    # Step 10: Final interference layer
    # Apply Hadamard gates to create interference between paths
    for i in range(TOTAL_QUBITS):
        qc.h(i)
    qc.barrier()
    
    # Step 11: Measure all qubits
    qc.measure_all()
    
    return qc


def transpile_mobius_toroidal_circuit(circuit: QuantumCircuit, backend, recursive_depth: int = 3) -> QuantumCircuit:
    """
    Transpile a Möbius toroidal circuit for specific quantum hardware, preserving the
    Möbius toroidal connectivity as much as possible. Uses a recursive loop approach to
    mimic the infinite energy flow in a Möbius torus structure.
    
    Args:
        circuit: The Möbius toroidal quantum circuit to transpile
        backend: The backend to transpile for
        recursive_depth: Number of recursive optimization passes to apply (default: 3)
        
    Returns:
        Transpiled quantum circuit with Möbius toroidal energy flow optimization
    """
    from qiskit.transpiler import PassManager
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit.transpiler.passes import BasicSwap, Optimize1qGatesDecomposition, CommutativeCancellation
    from qiskit.transpiler.passes import Depth, Size, CountOps, UnrollCustomDefinitions, BasisTranslator
    from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary as sel
    from qiskit.transpiler import CouplingMap
    
    try:
        print(f"Transpiling Möbius toroidal circuit for backend: {backend.name}")
        print(f"Using recursive depth: {recursive_depth} for Möbius toroidal energy flow optimization")
        
        # Get the target from the backend
        target = backend.target
        
        # Get the basis gates supported by the backend
        if hasattr(backend, 'configuration'):
            try:
                basis_gates = backend.configuration().basis_gates
                print(f"Target basis gates: {basis_gates}")
            except Exception:
                basis_gates = None
        else:
            basis_gates = None
        
        # Get the coupling map from the backend
        coupling_map = None
        if hasattr(backend, 'configuration'):
            try:
                coupling_config = backend.configuration().coupling_map
                
                if isinstance(coupling_config, CouplingMap):
                    coupling_map = coupling_config
                elif isinstance(coupling_config, list) and all(isinstance(item, list) for item in coupling_config if isinstance(item, list)):
                    coupling_map = CouplingMap(coupling_config)
                elif coupling_config is not None:
                    try:
                        coupling_map = CouplingMap(coupling_config)
                    except Exception as e:
                        print(f"Warning: Could not create coupling map from configuration: {e}")
                        coupling_map = None
                
                if coupling_map:
                    print(f"Using coupling map with {len(coupling_map.get_edges())} connections")
            except Exception as e:
                print(f"Warning: Could not get coupling map from backend: {e}")
                coupling_map = None
        
        # Create a custom pass manager for the recursive optimization
        custom_pm = PassManager()
        
        # Add analysis passes to track improvements
        custom_pm.append(Depth())
        custom_pm.append(Size())
        custom_pm.append(CountOps())
        
        # Start with the original circuit
        current_circuit = circuit
        
        # Apply recursive optimization to mimic Möbius toroidal energy flow
        for i in range(recursive_depth):
            print(f"Applying recursive optimization pass {i+1}/{recursive_depth}")
            
            # Generate a preset pass manager with increasing optimization level
            # This mimics the energy flowing through different parts of the Möbius torus
            opt_level = min(3, 1 + i)  # Start with level 1, increase up to level 3
            pm = generate_preset_pass_manager(target=target, optimization_level=opt_level)
            
            # Apply the optimization
            current_circuit = pm.run(current_circuit)
            
            # Add custom passes to enhance the Möbius toroidal structure
            # These passes help maintain the cyclic nature of the circuit
            custom_pm.append(CommutativeCancellation())
            custom_pm.append(Optimize1qGatesDecomposition())
            
            # Make sure we're using gates supported by the backend
            if basis_gates:
                custom_pm.append(UnrollCustomDefinitions(sel, basis_gates))
                custom_pm.append(BasisTranslator(sel, basis_gates))
                
            current_circuit = custom_pm.run(current_circuit)
            
            # If we have a valid coupling map, try to optimize for it
            if coupling_map:
                try:
                    # Use the BasicSwap pass with our properly constructed coupling map
                    swap_pass = BasicSwap(coupling_map)
                    swap_pm = PassManager(swap_pass)
                    current_circuit = swap_pm.run(current_circuit)
                except Exception as e:
                    print(f"Warning: Could not optimize for coupling map: {e}")
            
            # Analyze the circuit after this optimization pass
            depth = custom_pm.property_set['depth']
            size = custom_pm.property_set['size']
            print(f"  Pass {i+1} results - Depth: {depth}, Gate count: {size}")
        
        # Final pass to ensure compatibility with backend basis gates
        if basis_gates:
            final_pm = PassManager()
            final_pm.append(UnrollCustomDefinitions(sel, basis_gates))
            final_pm.append(BasisTranslator(sel, basis_gates))
            current_circuit = final_pm.run(current_circuit)
        
        return current_circuit
    
    except Exception as e:
        print(f"Error during transpilation: {e}")
        # Return the original circuit if transpilation fails
        return circuit


def analyze_mobius_toroidal_results(counts: Dict[str, int]) -> Dict:
    """
    Analyze the results from a Möbius toroidal quantum circuit execution.
    
    Args:
        counts: The measurement counts from circuit execution
        
    Returns:
        Dictionary of analysis metrics
    """
    import math
    from collections import Counter
    
    # Total number of shots
    total_shots = sum(counts.values())
    
    # Calculate entropy of the distribution
    entropy = 0
    for count in counts.values():
        prob = count / total_shots
        entropy -= prob * math.log2(prob) if prob > 0 else 0
    
    # Normalize entropy to [0, 1] range
    max_entropy = math.log2(2**TOTAL_QUBITS)  # Maximum possible entropy
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
    
    # Calculate parity-based metrics to detect Möbius effects
    even_parity_counts = 0
    odd_parity_counts = 0
    
    # Calculate phase coherence metrics
    phase_coherence = 0
    
    # Analyze bit patterns for Möbius twist signatures
    mobius_twist_detected = False
    mobius_twist_strength = 0
    
    for bitstring, count in counts.items():
        # Count number of 1s in the bitstring
        num_ones = bitstring.count('1')
        
        # Update parity counts
        if num_ones % 2 == 0:
            even_parity_counts += count
        else:
            odd_parity_counts += count
        
        # Check for Möbius twist signature in the minor circle (first TORUS_MINOR_QUBITS bits)
        # and major circle (last TORUS_MAJOR_QUBITS bits)
        if len(bitstring) >= TOTAL_QUBITS:
            minor_circle_bits = bitstring[:TORUS_MINOR_QUBITS]
            major_circle_bits = bitstring[TORUS_MINOR_QUBITS:TOTAL_QUBITS]
            
            # Calculate correlation between minor and major circle bits
            minor_parity = minor_circle_bits.count('1') % 2
            major_parity = major_circle_bits.count('1') % 2
            
            # In a Möbius strip, we expect a correlation between the parities
            # that differs from a regular torus
            if minor_parity != major_parity:
                mobius_twist_strength += count / total_shots
    
    # Determine if Möbius twist is detected based on twist strength
    mobius_twist_detected = mobius_twist_strength > 0.55  # Threshold for detection
    
    # Calculate parity bias (difference between even and odd parity outcomes)
    parity_bias = abs(even_parity_counts - odd_parity_counts) / total_shots
    
    # Calculate phase coherence based on the distribution of outcomes
    # Higher values indicate more coherent phase relationships
    phase_coherence = 1.0 - normalized_entropy
    
    # Prepare analysis results
    analysis = {
        'total_shots': total_shots,
        'unique_outcomes': len(counts),
        'entropy': entropy,
        'normalized_entropy': normalized_entropy,
        'phase_coherence': phase_coherence,
        'parity_bias': parity_bias,
        'mobius_twist_detected': mobius_twist_detected,
        'mobius_twist_strength': mobius_twist_strength,
        'most_common_outcomes': dict(Counter(counts).most_common(5))
    }
    
    return analysis


def run_mobius_toroidal_experiment(question: str, backend, shots: int = 1024, recursive_depth: int = 3) -> Dict:
    """
    Run a complete Möbius toroidal quantum experiment for a given question.
    
    Args:
        question: The question to encode in the Möbius toroidal circuit
        backend: The quantum backend to run on
        shots: Number of shots to run
        recursive_depth: Number of recursive optimization passes to apply (default: 3)
        
    Returns:
        Dictionary with experiment results and analysis
    """
    import time
    from qiskit import transpile, execute
    
    start_time = time.time()
    
    print(f"\n===== MÖBIUS TOROIDAL QUANTUM EXPERIMENT =====\n")
    print(f"Question: '{question}'")
    print(f"Backend: {backend.name}")
    print(f"Shots: {shots}")
    
    # Step 1: Generate the Möbius toroidal circuit
    print("\nGenerating Möbius toroidal circuit...")
    circuit = generate_mobius_toroidal_circuit(question)
    
    # Step 2: Transpile the circuit for the target backend
    print("\nTranspiling circuit for target backend...")
    transpiled_circuit = transpile_mobius_toroidal_circuit(circuit, backend, recursive_depth)
    
    # Step 3: Execute the circuit
    print(f"\nExecuting circuit on {backend.name} with {shots} shots...")
    job = execute(transpiled_circuit, backend, shots=shots)
    
    job_id = job.job_id()
    print(f"Job ID: {job_id}")
    
    # Step 4: Get the results
    print("\nWaiting for results...")
    result = job.result()
    counts = result.get_counts()
    
    # Step 5: Analyze the results
    print("\nAnalyzing results...")
    analysis = analyze_mobius_toroidal_results(counts)
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    # Prepare the experiment results
    experiment_results = {
        'question': question,
        'backend': backend.name,
        'shots': shots,
        'job_id': job_id,
        'counts': counts,
        'analysis': analysis,
        'execution_time': execution_time,
        'circuit_depth': transpiled_circuit.depth(),
        'circuit_width': transpiled_circuit.width(),
        'circuit_size': transpiled_circuit.size()
    }
    
    # Print summary of results
    print(f"\n===== EXPERIMENT RESULTS =====\n")
    print(f"Question: '{question}'")
    print(f"Execution time: {execution_time:.2f} seconds")
    print(f"Circuit depth: {transpiled_circuit.depth()}")
    print(f"Circuit width: {transpiled_circuit.width()}")
    print(f"Circuit size: {transpiled_circuit.size()}")
    print(f"\nAnalysis:")
    print(f"- Total shots: {analysis['total_shots']}")
    print(f"- Unique outcomes: {analysis['unique_outcomes']}")
    print(f"- Normalized entropy: {analysis['normalized_entropy']:.4f}")
    print(f"- Phase coherence: {analysis['phase_coherence']:.4f}")
    print(f"- Parity bias: {analysis['parity_bias']:.4f}")
    print(f"- Möbius twist detected: {analysis['mobius_twist_detected']}")
    print(f"- Möbius twist strength: {analysis['mobius_twist_strength']:.4f}")
    print(f"\nMost common outcomes:")
    for outcome, count in analysis['most_common_outcomes'].items():
        print(f"  {outcome}: {count} ({count/shots*100:.2f}%)")
    
    return experiment_results


if __name__ == "__main__":
    # Test the Möbius toroidal circuit generation
    test_question = "Does consciousness influence quantum states through non-orientable manifolds?"
    
    # Generate the circuit
    circuit = generate_mobius_toroidal_circuit(test_question)
    
    # Print circuit information
    print(f"\nCircuit depth: {circuit.depth()}")
    print(f"Circuit width: {circuit.width()}")
    print(f"Circuit size: {circuit.size()}")
    
    # Draw the circuit (text representation)
    print("\nCircuit diagram:")
    print(circuit.draw(output='text'))
