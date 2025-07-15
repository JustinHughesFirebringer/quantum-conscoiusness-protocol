"""
Focused metrics extraction for quantum registers based on statistical analysis.
Prioritizes the most informative registers (inner, middle, outer) while monitoring central
for baseline comparison.
"""

import json
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict

class RegisterMetricsExtractor:
    def __init__(self):
        # Register importance weights based on analysis
        self.register_weights = {
            'middle': 1.0,  # Most variable and informative
            'inner': 0.9,   # Second most informative
            'outer': 0.8,   # Third most informative
            'central': 0.3  # Least variable, used as baseline
        }
        
        # Expected value ranges based on analysis
        self.metric_ranges = {
            'interference': {
                'middle': (0.138914, 0.209286),
                'inner': (0.127839, 0.182454),
                'outer': (0.128286, 0.178770),
                'central': (0.000168, 0.013683)
            },
            'coherence': {
                'middle': (1.21e-4, 1.549e-3),
                'inner': (8.00e-5, 5.51e-4),
                'outer': (8.86e-5, 7.51e-4),
                'central': (1.13e-7, 7.70e-4)
            },
            'entanglement': {
                'middle': (5.41e-4, 1.972e-3),
                'inner': (5.86e-4, 1.285e-3),
                'outer': (4.33e-4, 1.127e-3),
                'central': (0.0, 0.0)
            }
        }

    def extract_metrics(self, metrics_data):
        """
        Extract focused metrics from metrics data.
        
        Args:
            metrics_data: Loaded metrics JSON data
            
        Returns:
            Dictionary containing:
            - Per-register metrics
            - Weighted composite scores
            - Anomaly flags
        """
        try:
            metrics = {
                'registers': {},
                'composite_scores': {},
                'anomalies': []
            }
            
            # Process each register's metrics
            for reg_name, reg_metrics in metrics_data['layers'].items():
                # Store original metrics
                metrics['registers'][reg_name] = {
                    'num_shots': reg_metrics['num_shots'],
                    'coherence': reg_metrics['coherence'],
                    'entanglement': reg_metrics['entanglement'],
                    'interference': reg_metrics['interference']
                }
                
                # Check for anomalies
                anomalies = self._check_anomalies(metrics['registers'][reg_name], reg_name)
                if anomalies:
                    metrics['anomalies'].extend(anomalies)
            
            # Calculate composite scores
            metrics['composite_scores'] = self._calculate_composite_scores(
                metrics['registers']
            )
            
            return metrics
            
        except Exception as e:
            print(f"Error extracting metrics: {e}")
            return None
    
    def _calculate_register_metrics(self, array_data, num_bits, reg_name):
        """Calculate detailed metrics for a single register."""
        import base64
        
        # Decode base64 data
        decoded_data = base64.b64decode(array_data)
        bits = np.unpackbits(np.frombuffer(decoded_data, dtype=np.uint8))
        
        # Ensure complete shots
        total_bits = len(bits)
        complete_shots = total_bits - (total_bits % num_bits)
        usable_bits = bits[:complete_shots]
        
        # Reshape into shots
        num_shots = complete_shots // num_bits
        bits_matrix = usable_bits.reshape(num_shots, num_bits)
        
        # Calculate metrics
        metrics = {
            'num_shots': num_shots,
            'coherence': self._calculate_coherence(bits_matrix),
            'entanglement': self._calculate_entanglement(bits_matrix),
            'interference': self._calculate_interference(bits_matrix)
        }
        
        return metrics
    
    def _calculate_coherence(self, bits_matrix):
        """Calculate quantum coherence from measurement results."""
        # Coherence estimated from bit flip rate
        transitions = np.diff(bits_matrix, axis=1)
        return float(np.mean(transitions != 0))
    
    def _calculate_entanglement(self, bits_matrix):
        """Calculate quantum entanglement from measurement results."""
        # Entanglement estimated from pairwise correlations
        correlations = []
        for i in range(bits_matrix.shape[1]-1):
            for j in range(i+1, bits_matrix.shape[1]):
                corr = np.corrcoef(bits_matrix[:,i], bits_matrix[:,j])[0,1]
                if not np.isnan(corr):
                    correlations.append(abs(corr))
        return float(np.mean(correlations)) if correlations else 0.0
    
    def _calculate_interference(self, bits_matrix):
        """Calculate quantum interference from measurement results."""
        # Interference estimated from pattern frequencies
        patterns = [''.join(map(str, row)) for row in bits_matrix]
        unique_patterns = len(set(patterns))
        return 1.0 - (unique_patterns / len(patterns))
    
    def _check_anomalies(self, reg_metrics, reg_name):
        """Check for anomalies in register metrics."""
        anomalies = []
        
        for metric_name in ['interference', 'coherence', 'entanglement']:
            value = reg_metrics[metric_name]
            expected_range = self.metric_ranges[metric_name][reg_name]
            
            if value < expected_range[0] or value > expected_range[1]:
                anomalies.append({
                    'register': reg_name,
                    'metric': metric_name,
                    'value': value,
                    'expected_range': expected_range
                })
        
        return anomalies
    
    def _calculate_composite_scores(self, register_metrics):
        """Calculate weighted composite scores across registers."""
        scores = {}
        
        for metric in ['interference', 'coherence', 'entanglement']:
            weighted_sum = 0.0
            total_weight = 0.0
            
            for reg_name, weight in self.register_weights.items():
                if reg_name in register_metrics:
                    value = register_metrics[reg_name][metric]
                    weighted_sum += value * weight
                    total_weight += weight
            
            scores[metric] = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return scores

def process_job_results(metrics_file, output_dir=None):
    """Process quantum job metrics and save focused analysis."""
    metrics_file = Path(metrics_file)
    if output_dir is None:
        output_dir = metrics_file.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load metrics data
    with open(metrics_file) as f:
        metrics_data = json.load(f)
    
    # Extract job ID and timestamp
    job_id = metrics_data['job_id']
    timestamp = metrics_data['timestamp']
    
    # Extract focused metrics
    extractor = RegisterMetricsExtractor()
    metrics = extractor.extract_metrics(metrics_data)
    
    if metrics is None:
        return None
    
    # Add metadata
    metrics['job_id'] = job_id
    metrics['timestamp'] = timestamp
    
    # Save focused metrics
    focused_file = output_dir / f"{job_id}_focused_metrics.json"
    with open(focused_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    # Generate summary plot
    plt.figure(figsize=(12, 6))
    
    # Plot interference values with error bars
    registers = []
    values = []
    errors = []
    
    for reg_name, reg_metrics in metrics['registers'].items():
        registers.append(reg_name)
        values.append(reg_metrics['interference'])
        
        # Use metric range as error bars
        value_range = extractor.metric_ranges['interference'][reg_name]
        error = (value_range[1] - value_range[0]) / 2
        errors.append(error)
    
    plt.errorbar(registers, values, yerr=errors, fmt='o-', capsize=5)
    plt.title(f'Register Interference Values (Job {job_id})')
    plt.ylabel('Interference')
    plt.grid(True, alpha=0.3)
    
    # Add anomaly markers if present
    for anomaly in metrics['anomalies']:
        if anomaly['metric'] == 'interference':
            plt.plot(anomaly['register'], anomaly['value'], 'rx', markersize=10, label='Anomaly')
    
    plt.tight_layout()
    plt.savefig(output_dir / f"{job_id}_interference_summary.png", dpi=300)
    plt.close()
    
    return metrics

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract focused quantum register metrics")
    parser.add_argument("--result-file", required=True, help="Path to job result file")
    parser.add_argument("--output", help="Output directory for metrics")
    args = parser.parse_args()
    
    metrics = process_job_results(args.result_file, args.output)
    if metrics:
        print(f"Processed job {metrics['job_id']}")
        if metrics['anomalies']:
            print("Anomalies detected:")
            for anomaly in metrics['anomalies']:
                print(f"  {anomaly['register']}: {anomaly['metric']} = {anomaly['value']:.6f}")
                print(f"    Expected range: {anomaly['expected_range']}")

if __name__ == "__main__":
    main()
