"""
Analyze quantum metrics from pentagon resonance circuit results.
Compares meditation vs control conditions across different layers and metrics.
"""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from scipy import stats

def load_metrics(metrics_dir):
    """Load all metrics files from directory into a pandas DataFrame."""
    metrics_dir = Path(metrics_dir)
    data = []
    
    # Load each metrics file
    for metrics_file in metrics_dir.glob('job-*-metrics.json'):
        with open(metrics_file, 'r') as f:
            job_metrics = json.load(f)
            
            # Extract job ID and timestamp
            job_id = job_metrics['job_id']
            timestamp = datetime.fromisoformat(job_metrics['timestamp'])
            
            # Extract metrics for each layer
            for layer_name, layer_metrics in job_metrics['layers'].items():
                row = {
                    'job_id': job_id,
                    'timestamp': timestamp,
                    'layer': layer_name,
                    'coherence': layer_metrics['coherence'],
                    'entanglement': layer_metrics['entanglement'],
                    'interference': layer_metrics['interference'],
                    'num_shots': layer_metrics['num_shots']
                }
                data.append(row)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    # Add time-based features
    df['minutes_elapsed'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds() / 60
    
    return df

def plot_metrics_over_time(df, output_dir):
    """Plot metrics evolution over time for each layer."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set style
    plt.style.use('seaborn')
    
    # Plot each metric
    metrics = ['coherence', 'entanglement', 'interference']
    
    for metric in metrics:
        plt.figure(figsize=(12, 6))
        
        # Plot each layer
        for layer in df['layer'].unique():
            layer_data = df[df['layer'] == layer]
            plt.plot(layer_data['minutes_elapsed'], 
                    layer_data[metric], 
                    'o-', 
                    label=layer,
                    alpha=0.7)
        
        plt.xlabel('Minutes Elapsed')
        plt.ylabel(metric.capitalize())
        plt.title(f'{metric.capitalize()} Evolution Over Time by Layer')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save plot
        plt.savefig(output_dir / f'{metric}_evolution.png', dpi=300, bbox_inches='tight')
        plt.close()

def analyze_layer_correlations(df, output_dir):
    """Analyze correlations between layers for each metric."""
    output_dir = Path(output_dir)
    metrics = ['coherence', 'entanglement', 'interference']
    layers = sorted(df['layer'].unique())
    
    results = []
    
    for metric in metrics:
        # Reshape data to have layers as columns
        pivot_df = df.pivot(index='job_id', columns='layer', values=metric)
        
        # Calculate correlation matrix
        corr_matrix = pivot_df.corr()
        
        # Plot correlation heatmap
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, vmin=-1, vmax=1)
        plt.title(f'Layer Correlations - {metric.capitalize()}')
        plt.savefig(output_dir / f'{metric}_correlations.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Find significant correlations
        for i, layer1 in enumerate(layers):
            for j, layer2 in enumerate(layers[i+1:], i+1):
                corr, p_value = stats.pearsonr(pivot_df[layer1].dropna(), 
                                             pivot_df[layer2].dropna())
                if p_value < 0.05:  # Statistically significant
                    results.append({
                        'metric': metric,
                        'layer1': layer1,
                        'layer2': layer2,
                        'correlation': corr,
                        'p_value': p_value
                    })
    
    return pd.DataFrame(results)

def analyze_temporal_patterns(df):
    """Analyze temporal patterns in the metrics."""
    results = []
    
    for layer in df['layer'].unique():
        layer_data = df[df['layer'] == layer]
        
        for metric in ['coherence', 'entanglement', 'interference']:
            # Test for trend
            correlation, p_value = stats.pearsonr(layer_data['minutes_elapsed'], 
                                                layer_data[metric])
            
            # Test for periodicity using autocorrelation
            autocorr = pd.Series(layer_data[metric]).autocorr()
            
            results.append({
                'layer': layer,
                'metric': metric,
                'trend_correlation': correlation,
                'trend_p_value': p_value,
                'autocorrelation': autocorr,
                'mean': layer_data[metric].mean(),
                'std': layer_data[metric].std(),
                'min': layer_data[metric].min(),
                'max': layer_data[metric].max()
            })
    
    return pd.DataFrame(results)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Analyze quantum metrics from pentagon resonance circuit")
    parser.add_argument("--metrics-dir", required=True, help="Directory containing metrics JSON files")
    parser.add_argument("--output", required=True, help="Output directory for analysis results")
    args = parser.parse_args()
    
    try:
        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created output directory: {output_dir}")
        
        # Load metrics data
        print("\nLoading metrics data...")
        metrics_dir = Path(args.metrics_dir)
        print(f"Looking for metrics files in: {metrics_dir}")
        df = load_metrics(metrics_dir)
        print(f"Loaded {len(df)} data points")
        
        # Plot metrics evolution
        print("\nPlotting metrics evolution...")
        plot_metrics_over_time(df, output_dir)
        print("Saved evolution plots")
        
        # Analyze layer correlations
        print("\nAnalyzing layer correlations...")
        correlations = analyze_layer_correlations(df, output_dir)
        print("Saved correlation plots")
        
        # Save significant correlations
        if not correlations.empty:
            corr_file = output_dir / 'significant_correlations.csv'
            correlations.to_csv(corr_file, index=False)
            print(f"\nSaved significant correlations to {corr_file}")
            print("\nSignificant correlations found:")
            print(correlations.to_string(index=False))
        
        # Analyze temporal patterns
        print("\nAnalyzing temporal patterns...")
        patterns = analyze_temporal_patterns(df)
        patterns_file = output_dir / 'temporal_patterns.csv'
        patterns.to_csv(patterns_file, index=False)
        print(f"Saved temporal patterns to {patterns_file}")
        
        # Print summary statistics
        print("\nSummary Statistics by Layer:")
        summary = df.groupby('layer').agg({
            'coherence': ['mean', 'std', 'min', 'max'],
            'entanglement': ['mean', 'std', 'min', 'max'],
            'interference': ['mean', 'std', 'min', 'max']
        })
        print(summary.round(4).to_string())
        
        # Save summary to file
        summary_file = output_dir / 'summary_statistics.csv'
        summary.to_csv(summary_file)
        print(f"\nSaved summary statistics to {summary_file}")
        
    except Exception as e:
        print(f"\nError during analysis: {e}")

if __name__ == "__main__":
    main()
