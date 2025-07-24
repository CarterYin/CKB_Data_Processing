import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
from datetime import datetime
import os

warnings.filterwarnings('ignore')

# Set up the plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create output directory for results
output_dir = 'ethnic_disease_analysis_results'
os.makedirs(output_dir, exist_ok=True)

# Read the data
print("Loading data...")
df = pd.read_csv('analysis_result_eyes_realigned.tsv', sep='\t')
print(f"Total records loaded: {len(df)}")

# Define the diseases to analyze
diseases = {
    'glaucoma_diag': 'Glaucoma',
    'amd_diag': 'Age-related Macular Degeneration',
    'cataract_diag': 'Cataract',
    'diabetes_test': 'Diabetes (Reported or Blood Test)',
    'has_diabetes_baseline': 'Diabetes (Clinical Criteria)',
    'ihd_diag': 'Ischemic Heart Disease',
    'peri_art_dis_symptoms': 'Peripheral Artery Disease Symptoms',
    'pre_18_pneu_bronch_tb': 'Early Life Respiratory Disease'
}

# Get ethnic group information
print("\nAnalyzing ethnic group distribution...")
ethnic_counts = df['id_ethnic_group_id'].value_counts()
print(f"Number of ethnic groups: {len(ethnic_counts)}")
print("\nEthnic group distribution:")
for ethnic_id, count in ethnic_counts.items():
    print(f"  Ethnic Group {ethnic_id}: {count} ({count/len(df)*100:.2f}%)")

# Create a comprehensive analysis report
report = []
report.append("# Comprehensive Analysis of Disease Distribution Across Ethnic Groups\n")
report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
report.append(f"Total Sample Size: {len(df):,}\n")
report.append(f"Number of Ethnic Groups: {len(ethnic_counts)}\n")

# 1. Overall Disease Prevalence
report.append("\n## 1. Overall Disease Prevalence\n")
overall_prevalence = {}
for disease_col, disease_name in diseases.items():
    if disease_col in df.columns:
        prevalence = df[disease_col].sum() / len(df) * 100
        overall_prevalence[disease_name] = prevalence
        report.append(f"- {disease_name}: {prevalence:.2f}% ({df[disease_col].sum():,} cases)\n")

# 2. Disease Prevalence by Ethnic Group
report.append("\n## 2. Disease Prevalence by Ethnic Group\n")

# Create a summary dataframe
ethnic_disease_summary = pd.DataFrame()

for disease_col, disease_name in diseases.items():
    if disease_col in df.columns:
        report.append(f"\n### {disease_name}\n")
        
        # Calculate prevalence for each ethnic group
        for ethnic_id in sorted(df['id_ethnic_group_id'].unique()):
            ethnic_df = df[df['id_ethnic_group_id'] == ethnic_id]
            cases = ethnic_df[disease_col].sum()
            total = len(ethnic_df)
            prevalence = cases / total * 100 if total > 0 else 0
            
            ethnic_disease_summary.loc[f"Ethnic Group {ethnic_id}", disease_name] = prevalence
            report.append(f"- Ethnic Group {ethnic_id}: {prevalence:.2f}% ({cases}/{total})\n")

# 3. Statistical Analysis
report.append("\n## 3. Statistical Analysis\n")

# Perform chi-square tests for each disease
for disease_col, disease_name in diseases.items():
    if disease_col in df.columns:
        # Create contingency table
        contingency_table = pd.crosstab(df['id_ethnic_group_id'], df[disease_col])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        report.append(f"\n### {disease_name}\n")
        report.append(f"- Chi-square statistic: {chi2:.4f}\n")
        report.append(f"- p-value: {p_value:.4e}\n")
        report.append(f"- Degrees of freedom: {dof}\n")
        if p_value < 0.05:
            report.append("- Result: Statistically significant difference between ethnic groups (p < 0.05)\n")
        else:
            report.append("- Result: No statistically significant difference between ethnic groups (p ≥ 0.05)\n")

# 4. Risk Ratios
report.append("\n## 4. Risk Ratios (Relative to Overall Population)\n")

for disease_col, disease_name in diseases.items():
    if disease_col in df.columns:
        report.append(f"\n### {disease_name}\n")
        overall_prevalence_value = df[disease_col].sum() / len(df)
        
        for ethnic_id in sorted(df['id_ethnic_group_id'].unique()):
            ethnic_df = df[df['id_ethnic_group_id'] == ethnic_id]
            ethnic_prevalence = ethnic_df[disease_col].sum() / len(ethnic_df) if len(ethnic_df) > 0 else 0
            risk_ratio = ethnic_prevalence / overall_prevalence_value if overall_prevalence_value > 0 else 0
            
            report.append(f"- Ethnic Group {ethnic_id}: RR = {risk_ratio:.3f}")
            if risk_ratio > 1.2:
                report.append(" (Increased risk)\n")
            elif risk_ratio < 0.8:
                report.append(" (Decreased risk)\n")
            else:
                report.append(" (Similar to population average)\n")

# 5. Comorbidity Analysis
report.append("\n## 5. Comorbidity Analysis by Ethnic Group\n")

# Analyze common disease combinations
for ethnic_id in sorted(df['id_ethnic_group_id'].unique()):
    ethnic_df = df[df['id_ethnic_group_id'] == ethnic_id]
    report.append(f"\n### Ethnic Group {ethnic_id}\n")
    
    # Count individuals with multiple conditions
    disease_cols = [col for col in diseases.keys() if col in df.columns]
    ethnic_df['disease_count'] = ethnic_df[disease_cols].sum(axis=1)
    
    for i in range(len(disease_cols) + 1):
        count = (ethnic_df['disease_count'] == i).sum()
        percentage = count / len(ethnic_df) * 100 if len(ethnic_df) > 0 else 0
        report.append(f"- {i} disease(s): {count} ({percentage:.2f}%)\n")

# 6. Age-Adjusted Analysis (if age data is available)
if 'age_at_study_date_x100_baseline' in df.columns:
    report.append("\n## 6. Age Distribution by Disease and Ethnic Group\n")
    
    # Convert age from x100 format
    df['age'] = df['age_at_study_date_x100_baseline'] / 100
    
    for disease_col, disease_name in diseases.items():
        if disease_col in df.columns:
            report.append(f"\n### {disease_name}\n")
            
            for ethnic_id in sorted(df['id_ethnic_group_id'].unique()):
                ethnic_disease_df = df[(df['id_ethnic_group_id'] == ethnic_id) & (df[disease_col] == 1)]
                if len(ethnic_disease_df) > 0:
                    mean_age = ethnic_disease_df['age'].mean()
                    std_age = ethnic_disease_df['age'].std()
                    report.append(f"- Ethnic Group {ethnic_id}: Mean age = {mean_age:.1f} ± {std_age:.1f} years\n")

# Save the report
report_text = ''.join(report)
with open(f'{output_dir}/comprehensive_disease_ethnic_analysis_report.md', 'w') as f:
    f.write(report_text)

print("\nReport saved to: comprehensive_disease_ethnic_analysis_report.md")

# Create visualizations
print("\nCreating visualizations...")

# 1. Heatmap of disease prevalence by ethnic group
plt.figure(figsize=(12, 8))
sns.heatmap(ethnic_disease_summary.T, annot=True, fmt='.2f', cmap='YlOrRd', 
            cbar_kws={'label': 'Prevalence (%)'})
plt.title('Disease Prevalence by Ethnic Group (%)', fontsize=16, pad=20)
plt.xlabel('Ethnic Group', fontsize=12)
plt.ylabel('Disease', fontsize=12)
plt.tight_layout()
plt.savefig(f'{output_dir}/disease_prevalence_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. Bar plots for each disease
for disease_col, disease_name in diseases.items():
    if disease_col in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Calculate prevalence for each ethnic group
        prevalence_data = []
        ethnic_labels = []
        for ethnic_id in sorted(df['id_ethnic_group_id'].unique()):
            ethnic_df = df[df['id_ethnic_group_id'] == ethnic_id]
            prevalence = ethnic_df[disease_col].sum() / len(ethnic_df) * 100 if len(ethnic_df) > 0 else 0
            prevalence_data.append(prevalence)
            ethnic_labels.append(f"Group {ethnic_id}")
        
        bars = ax.bar(ethnic_labels, prevalence_data, color='skyblue', edgecolor='navy', alpha=0.7)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        # Add overall prevalence line
        overall_prev = df[disease_col].sum() / len(df) * 100
        ax.axhline(y=overall_prev, color='red', linestyle='--', 
                  label=f'Overall prevalence: {overall_prev:.1f}%')
        
        ax.set_xlabel('Ethnic Group', fontsize=12)
        ax.set_ylabel('Prevalence (%)', fontsize=12)
        ax.set_title(f'{disease_name} Prevalence by Ethnic Group', fontsize=14, pad=20)
        ax.legend()
        plt.tight_layout()
        
        # Save with clean filename
        clean_name = disease_name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
        plt.savefig(f'{output_dir}/{clean_name}_by_ethnic_group.png', dpi=300, bbox_inches='tight')
        plt.close()

# 3. Risk ratio plot
fig, ax = plt.subplots(figsize=(14, 10))
risk_ratios = pd.DataFrame()

for disease_col, disease_name in diseases.items():
    if disease_col in df.columns:
        overall_prevalence_value = df[disease_col].sum() / len(df)
        
        for ethnic_id in sorted(df['id_ethnic_group_id'].unique()):
            ethnic_df = df[df['id_ethnic_group_id'] == ethnic_id]
            ethnic_prevalence = ethnic_df[disease_col].sum() / len(ethnic_df) if len(ethnic_df) > 0 else 0
            risk_ratio = ethnic_prevalence / overall_prevalence_value if overall_prevalence_value > 0 else 0
            risk_ratios.loc[f"Group {ethnic_id}", disease_name] = risk_ratio

# Create heatmap for risk ratios
sns.heatmap(risk_ratios.T, annot=True, fmt='.3f', cmap='RdBu_r', center=1.0,
            cbar_kws={'label': 'Risk Ratio'})
plt.title('Disease Risk Ratios by Ethnic Group (Relative to Overall Population)', fontsize=16, pad=20)
plt.xlabel('Ethnic Group', fontsize=12)
plt.ylabel('Disease', fontsize=12)
plt.tight_layout()
plt.savefig(f'{output_dir}/risk_ratio_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. Comorbidity visualization
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
axes = axes.ravel()

for idx, ethnic_id in enumerate(sorted(df['id_ethnic_group_id'].unique())[:4]):  # Show first 4 ethnic groups
    ethnic_df = df[df['id_ethnic_group_id'] == ethnic_id]
    disease_cols = [col for col in diseases.keys() if col in df.columns]
    ethnic_df['disease_count'] = ethnic_df[disease_cols].sum(axis=1)
    
    disease_count_dist = ethnic_df['disease_count'].value_counts().sort_index()
    
    axes[idx].bar(disease_count_dist.index, disease_count_dist.values, 
                  color='coral', edgecolor='darkred', alpha=0.7)
    axes[idx].set_xlabel('Number of Diseases', fontsize=12)
    axes[idx].set_ylabel('Number of Individuals', fontsize=12)
    axes[idx].set_title(f'Disease Count Distribution - Ethnic Group {ethnic_id}', fontsize=14)
    
    # Add percentage labels
    for i, v in enumerate(disease_count_dist.values):
        percentage = v / len(ethnic_df) * 100
        axes[idx].text(disease_count_dist.index[i], v, f'{percentage:.1f}%', 
                      ha='center', va='bottom')

plt.tight_layout()
plt.savefig(f'{output_dir}/comorbidity_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# Save summary data to CSV
ethnic_disease_summary.to_csv(f'{output_dir}/disease_prevalence_by_ethnic_group.csv')
risk_ratios.to_csv(f'{output_dir}/risk_ratios_by_ethnic_group.csv')

print("\nAnalysis complete! All results saved to the 'ethnic_disease_analysis_results' directory.")
print("\nFiles generated:")
print("- comprehensive_disease_ethnic_analysis_report.md (Main report)")
print("- disease_prevalence_heatmap.png")
print("- Individual disease prevalence charts (8 files)")
print("- risk_ratio_heatmap.png")
print("- comorbidity_distribution.png")
print("- disease_prevalence_by_ethnic_group.csv")
print("- risk_ratios_by_ethnic_group.csv") 