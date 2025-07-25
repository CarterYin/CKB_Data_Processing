import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# Set plotting parameters for high quality
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.style.use('seaborn-v0_8-whitegrid')

print("Loading and processing data...")

# Read data
df = pd.read_csv('analysis_result_eyes_realigned.tsv', sep='\t')

# Define comprehensive ethnic group mapping
ethnic_mapping = {
    1: 'Han',
    2: 'Zhuang', 
    3: 'Hui',
    6: 'Manchu',
    8: 'Miao',
    10: 'Tibetan',
    11: 'Mongolian',
    12: 'Dong',
    13: 'Yao',
    19: 'Dai',
    31: 'She',
    32: 'Lisu',
    36: 'Jingpo',
    37: 'Jing',
    38: 'Achang'
}

# Map ethnic groups
df['ethnic_group'] = df['id_ethnic_group_id'].map(ethnic_mapping)
df = df[df['ethnic_group'].notna()].copy()

# Define all disease columns with full English names (no abbreviations)
disease_definitions = {
    'glaucoma_diag': 'Glaucoma',
    'amd_diag': 'Age-related Macular Degeneration',
    'cataract_diag': 'Cataract',
    'diabetes_test': 'Participant Reports History of Diabetes or Diabetes Detected by Blood Test',
    'has_diabetes_baseline': 'Participant Has History of Diabetes (Reported or Random Blood Glucose ≥11.1 mmol/L or Fasting Blood Glucose ≥7.0 mmol/L)',
    'ihd_diag': 'Ischemic Heart Disease',
    'peri_art_dis_symptoms': 'Peripheral Artery Disease Symptoms (Painful Cramping Legs, Leg Numbness or Weakness, and Cold Legs)',
    'pre_18_pneu_bronch_tb': 'Hospitalized for Pneumonia, Bronchitis, or Tuberculosis Before Age 18'
}

def calculate_comprehensive_prevalence(df, disease_definitions):
    """Calculate disease prevalence for all ethnic groups including small samples"""
    results = []
    ethnic_groups = sorted(df['ethnic_group'].unique())
    
    print(f"Analyzing {len(ethnic_groups)} ethnic groups: {ethnic_groups}")
    
    for ethnic in ethnic_groups:
        ethnic_df = df[df['ethnic_group'] == ethnic]
        total_ethnic_population = len(ethnic_df)
        
        for col, disease_name in disease_definitions.items():
            if col in df.columns:
                # Count valid responses (non-NA values)
                valid_data = ethnic_df[ethnic_df[col].notna()]
                if len(valid_data) > 0:
                    cases = valid_data[col].sum()
                    total_responses = len(valid_data)
                    prevalence = (cases / total_responses * 100) if total_responses > 0 else 0
                    
                    results.append({
                        'ethnic_group': ethnic,
                        'disease': disease_name,
                        'prevalence': round(prevalence, 2),
                        'cases': int(cases),
                        'total_responses': total_responses,
                        'total_ethnic_population': total_ethnic_population
                    })
                else:
                    # No valid data for this disease in this ethnic group
                    results.append({
                        'ethnic_group': ethnic,
                        'disease': disease_name,
                        'prevalence': 0,
                        'cases': 0,
                        'total_responses': 0,
                        'total_ethnic_population': total_ethnic_population
                    })
    
    return pd.DataFrame(results)

# Calculate prevalence data
print("Calculating prevalence data...")
prevalence_data = calculate_comprehensive_prevalence(df, disease_definitions)

# Get sample sizes for each ethnic group
ethnic_sample_sizes = df['ethnic_group'].value_counts().to_dict()

# Define color palette for ethnic groups
def get_ethnic_colors(ethnic_groups):
    """Generate distinct colors for ethnic groups"""
    # Use a combination of qualitative color palettes
    colors = plt.cm.Set3(np.linspace(0, 1, len(ethnic_groups)))
    return dict(zip(sorted(ethnic_groups), colors))

ethnic_colors = get_ethnic_colors(df['ethnic_group'].unique())

def create_disease_bar_chart(disease_name, prevalence_subset, ethnic_sample_sizes, save_path=None):
    """Create a comprehensive bar chart for a specific disease across all ethnic groups"""
    
    # Sort by prevalence for better visualization
    prevalence_subset = prevalence_subset.sort_values('prevalence', ascending=True)
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Create bars
    bars = ax.barh(range(len(prevalence_subset)), 
                   prevalence_subset['prevalence'],
                   color=[ethnic_colors[ethnic] for ethnic in prevalence_subset['ethnic_group']],
                   alpha=0.8,
                   edgecolor='black',
                   linewidth=0.5)
    
    # Customize the plot
    ax.set_yticks(range(len(prevalence_subset)))
    
    # Create detailed labels with sample sizes
    labels = []
    for _, row in prevalence_subset.iterrows():
        ethnic = row['ethnic_group']
        sample_size = ethnic_sample_sizes.get(ethnic, 0)
        cases = row['cases']
        total_responses = row['total_responses']
        labels.append(f"{ethnic}\n(n={sample_size}, cases={cases}/{total_responses})")
    
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel('Prevalence (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Ethnic Groups', fontsize=12, fontweight='bold')
    
    # Add prevalence values on bars
    for i, (bar, prevalence) in enumerate(zip(bars, prevalence_subset['prevalence'])):
        ax.text(prevalence + 0.1, i, f'{prevalence:.1f}%', 
                va='center', fontsize=9, fontweight='bold')
    
    # Set title with word wrapping for long disease names
    title_lines = []
    words = disease_name.split()
    current_line = []
    for word in words:
        if len(' '.join(current_line + [word])) <= 70:  # Line length limit
            current_line.append(word)
        else:
            title_lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        title_lines.append(' '.join(current_line))
    
    ax.set_title('\n'.join(title_lines), fontsize=14, fontweight='bold', pad=20)
    
    # Add grid
    ax.grid(True, alpha=0.3, axis='x')
    ax.set_axisbelow(True)
    
    # Set x-axis limits
    max_prevalence = prevalence_subset['prevalence'].max()
    ax.set_xlim(0, max(max_prevalence * 1.2, 5))  # At least 5% for readability
    
    # Add subtitle with total sample information
    total_cases = prevalence_subset['cases'].sum()
    total_responses = prevalence_subset['total_responses'].sum()
    plt.figtext(0.5, 0.02, f'Total cases: {total_cases} out of {total_responses} respondents across all ethnic groups', 
                ha='center', fontsize=10, style='italic')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig

# Create individual charts for each disease
print("Creating individual disease charts...")

for disease_name in disease_definitions.values():
    disease_data = prevalence_data[prevalence_data['disease'] == disease_name].copy()
    
    if not disease_data.empty:
        # Create filename-safe disease name
        safe_name = disease_name.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '').replace('≥', 'gte').replace('/', '_or_')
        filename = f"ethnic_distribution_{safe_name}.png"
        
        print(f"Creating chart for: {disease_name}")
        fig = create_disease_bar_chart(disease_name, disease_data, ethnic_sample_sizes, filename)
        plt.show()
        plt.close()

# Create summary statistics
print("\nGenerating summary statistics...")

summary_stats = []
for disease_name in disease_definitions.values():
    disease_data = prevalence_data[prevalence_data['disease'] == disease_name]
    
    if not disease_data.empty:
        total_cases = disease_data['cases'].sum()
        total_responses = disease_data['total_responses'].sum()
        overall_prevalence = (total_cases / total_responses * 100) if total_responses > 0 else 0
        max_prevalence = disease_data['prevalence'].max()
        min_prevalence = disease_data['prevalence'].min()
        ethnic_with_max = disease_data.loc[disease_data['prevalence'].idxmax(), 'ethnic_group']
        ethnic_with_min = disease_data.loc[disease_data['prevalence'].idxmin(), 'ethnic_group']
        
        summary_stats.append({
            'Disease': disease_name,
            'Overall_Prevalence_Percent': round(overall_prevalence, 2),
            'Total_Cases': total_cases,
            'Total_Responses': total_responses,
            'Highest_Prevalence_Percent': round(max_prevalence, 2),
            'Ethnic_Group_Highest': ethnic_with_max,
            'Lowest_Prevalence_Percent': round(min_prevalence, 2),
            'Ethnic_Group_Lowest': ethnic_with_min
        })

summary_df = pd.DataFrame(summary_stats)
summary_df.to_csv('comprehensive_disease_summary_statistics.csv', index=False)

print("\nSummary Statistics:")
print(summary_df.to_string(index=False))

print(f"\nAnalysis completed!")
print(f"Generated {len(disease_definitions)} individual disease distribution charts")
print(f"Data includes {len(df['ethnic_group'].unique())} ethnic groups")
print(f"Total sample size: {len(df)} individuals")

# Display ethnic group sample sizes
print("\nEthnic Group Sample Sizes:")
for ethnic, count in sorted(ethnic_sample_sizes.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / len(df)) * 100
    print(f"{ethnic}: {count} individuals ({percentage:.2f}%)") 