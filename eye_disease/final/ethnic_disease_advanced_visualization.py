import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# Set font and style
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8-whitegrid')

# Read data
print("Reading data...")
df = pd.read_csv('analysis_result_eyes_realigned.tsv', sep='\t')

# Define ethnic group mapping
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

# Define disease columns
disease_cols_group1 = {
    'glaucoma_diag': 'Glaucoma',
    'amd_diag': 'Age-related Macular Degeneration', 
    'cataract_diag': 'Cataract',
    'diabetes_test': 'Diabetes (Reported or Blood Test)',
    'has_diabetes_baseline': 'Diabetes History (Baseline)'
}

disease_cols_group2 = {
    'ihd_diag': 'Ischemic Heart Disease',
    'peri_art_dis_symptoms': 'Peripheral Artery Disease Symptoms',
    'pre_18_pneu_bronch_tb': 'Pneumonia/Bronchitis/Tuberculosis Before Age 18'
}

# Calculate prevalence data for each ethnic group
def calculate_detailed_prevalence(df, disease_cols):
    results = []
    ethnic_groups = sorted(df['ethnic_group'].unique())
    
    for ethnic in ethnic_groups:
        ethnic_df = df[df['ethnic_group'] == ethnic]
        
        for col, name in disease_cols.items():
            if col in df.columns:
                valid_data = ethnic_df[ethnic_df[col].notna()]
                if len(valid_data) > 0:
                    cases = valid_data[col].sum()
                    total = len(valid_data)
                    prevalence = (cases / total * 100) if total > 0 else 0
                    
                    results.append({
                        'ethnic_group': ethnic,
                        'disease': name,
                        'prevalence': round(prevalence, 2),
                        'cases': int(cases),
                        'total': total
                    })
    
    return pd.DataFrame(results)

# Get prevalence data
prevalence_data_group1 = calculate_detailed_prevalence(df, disease_cols_group1)
prevalence_data_group2 = calculate_detailed_prevalence(df, disease_cols_group2)

# Filter ethnic groups with sufficient sample size (at least 10 people)
ethnic_counts = df['ethnic_group'].value_counts()
valid_ethnic_groups = ethnic_counts[ethnic_counts >= 10].index.tolist()

# Create comprehensive figure with subplots
fig = plt.figure(figsize=(28, 24))
gs = GridSpec(4, 2, figure=fig, hspace=0.35, wspace=0.25, height_ratios=[1.2, 1, 1, 1])

# Define color schemes
ethnic_colors = {
    'Han': '#1f77b4',
    'Miao': '#ff7f0e', 
    'Hui': '#2ca02c',
    'Mongolian': '#d62728',
    'Dong': '#9467bd',
    'Yao': '#8c564b',
    'Lisu': '#e377c2',
    'Dai': '#7f7f7f',
    'Manchu': '#bcbd22',
    'Others': '#17becf'
}

disease_colors_group1 = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
disease_colors_group2 = ['#34495e', '#16a085', '#e67e22']

# 1. Overview: Disease prevalence heatmap
ax1 = fig.add_subplot(gs[0, :])
all_diseases = {**disease_cols_group1, **disease_cols_group2}
prevalence_matrix = []
disease_names = []
ethnic_names = []

for ethnic in valid_ethnic_groups:
    row = []
    for col, name in all_diseases.items():
        data = prevalence_data_group1[
            (prevalence_data_group1['ethnic_group'] == ethnic) & 
            (prevalence_data_group1['disease'] == name)
        ]
        if data.empty:
            data = prevalence_data_group2[
                (prevalence_data_group2['ethnic_group'] == ethnic) & 
                (prevalence_data_group2['disease'] == name)
            ]
        
        if not data.empty:
            row.append(data['prevalence'].values[0])
        else:
            row.append(0)
    
    if ethnic not in ethnic_names:
        ethnic_names.append(ethnic)
    prevalence_matrix.append(row)

disease_names = list(all_diseases.values())

# Create heatmap
im = ax1.imshow(np.array(prevalence_matrix).T, cmap='YlOrRd', aspect='auto')
ax1.set_xticks(range(len(ethnic_names)))
ax1.set_yticks(range(len(disease_names)))
ax1.set_xticklabels(ethnic_names, rotation=45, ha='right', fontsize=11)
ax1.set_yticklabels(disease_names, fontsize=11)

# Add text annotations
for i in range(len(disease_names)):
    for j in range(len(ethnic_names)):
        text = ax1.text(j, i, f'{prevalence_matrix[j][i]:.1f}%',
                       ha="center", va="center", color="black", fontsize=9)

ax1.set_title('Disease Prevalence Heatmap Across Ethnic Groups', fontsize=20, fontweight='bold', pad=20)
cbar = plt.colorbar(im, ax=ax1, orientation='horizontal', pad=0.1)
cbar.set_label('Prevalence (%)', fontsize=12)

# 2. Sample distribution pie chart
ax2 = fig.add_subplot(gs[1, 0])
ethnic_counts_filtered = ethnic_counts[valid_ethnic_groups]
colors_pie = [ethnic_colors.get(eth, '#17becf') for eth in ethnic_counts_filtered.index]
wedges, texts, autotexts = ax2.pie(ethnic_counts_filtered.values, 
                                   labels=ethnic_counts_filtered.index,
                                   autopct='%1.1f%%',
                                   colors=colors_pie,
                                   startangle=90)
ax2.set_title('Sample Distribution by Ethnic Group', fontsize=16, fontweight='bold', pad=20)

# 3. Radar chart for top ethnic groups
ax3 = fig.add_subplot(gs[1, 1], projection='polar')
top_ethnic_groups = ethnic_counts_filtered.head(4).index.tolist()
angles = np.linspace(0, 2 * np.pi, len(disease_cols_group1), endpoint=False)
angles = np.concatenate([angles, [angles[0]]])

for ethnic in top_ethnic_groups:
    values = []
    for col, name in disease_cols_group1.items():
        data = prevalence_data_group1[
            (prevalence_data_group1['ethnic_group'] == ethnic) & 
            (prevalence_data_group1['disease'] == name)
        ]
        if not data.empty:
            values.append(data['prevalence'].values[0])
        else:
            values.append(0)
    
    values = values + [values[0]]
    ax3.plot(angles, values, 'o-', linewidth=2, label=ethnic, 
             color=ethnic_colors.get(ethnic, '#17becf'))
    ax3.fill(angles, values, alpha=0.15, color=ethnic_colors.get(ethnic, '#17becf'))

ax3.set_xticks(angles[:-1])
ax3.set_xticklabels(list(disease_cols_group1.values()), fontsize=10)
ax3.set_ylim(0, max([d['prevalence'] for d in prevalence_data_group1.to_dict('records')]) * 1.2)
ax3.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
ax3.set_title('Eye Disease and Diabetes Prevalence Radar Chart', fontsize=16, fontweight='bold', pad=30)
ax3.grid(True)

# 4. Group 1 diseases bar chart
ax4 = fig.add_subplot(gs[2, :])
data_group1_filtered = prevalence_data_group1[prevalence_data_group1['ethnic_group'].isin(valid_ethnic_groups)]
pivot_data1 = data_group1_filtered.pivot(index='ethnic_group', columns='disease', values='prevalence').fillna(0)

x = np.arange(len(pivot_data1.index))
width = 0.15
multiplier = 0

for i, (disease, values) in enumerate(pivot_data1.items()):
    offset = width * multiplier
    bars = ax4.bar(x + offset, values, width, label=disease, color=disease_colors_group1[i])
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=8)
    
    multiplier += 1

ax4.set_xlabel('Ethnic Group', fontsize=14, fontweight='bold')
ax4.set_ylabel('Prevalence (%)', fontsize=14, fontweight='bold')
ax4.set_title('Eye Diseases and Diabetes Prevalence by Ethnic Group', fontsize=18, fontweight='bold', pad=20)
ax4.set_xticks(x + width * 2)
ax4.set_xticklabels(pivot_data1.index, rotation=45, ha='right')
ax4.legend(title='Disease Type', bbox_to_anchor=(1.05, 1), loc='upper left')
ax4.grid(True, axis='y', alpha=0.3)

# 5. Group 2 diseases bar chart
ax5 = fig.add_subplot(gs[3, :])
data_group2_filtered = prevalence_data_group2[prevalence_data_group2['ethnic_group'].isin(valid_ethnic_groups)]
pivot_data2 = data_group2_filtered.pivot(index='ethnic_group', columns='disease', values='prevalence').fillna(0)

x = np.arange(len(pivot_data2.index))
width = 0.25
multiplier = 0

for i, (disease, values) in enumerate(pivot_data2.items()):
    offset = width * multiplier
    bars = ax5.bar(x + offset, values, width, label=disease, color=disease_colors_group2[i])
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=8)
    
    multiplier += 1

ax5.set_xlabel('Ethnic Group', fontsize=14, fontweight='bold')
ax5.set_ylabel('Prevalence (%)', fontsize=14, fontweight='bold')
ax5.set_title('Cardiovascular and Respiratory Disease Prevalence by Ethnic Group', fontsize=18, fontweight='bold', pad=20)
ax5.set_xticks(x + width)
ax5.set_xticklabels(pivot_data2.index, rotation=45, ha='right')
ax5.legend(title='Disease Type', bbox_to_anchor=(1.05, 1), loc='upper left')
ax5.grid(True, axis='y', alpha=0.3)

plt.suptitle('Comprehensive Analysis of Disease Distribution Across Ethnic Groups in China', 
            fontsize=24, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('ethnic_disease_comprehensive_advanced.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

# Create separate detailed charts for each disease group
# Chart 1: Eye Diseases and Diabetes
fig1, ax = plt.subplots(figsize=(18, 12))
data1 = data_group1_filtered.pivot(index='ethnic_group', columns='disease', values='prevalence').fillna(0)

# Sort by total prevalence
data1['Total'] = data1.sum(axis=1)
data1 = data1.sort_values('Total', ascending=False).drop('Total', axis=1)

x = np.arange(len(data1.index))
width = 0.15
patterns = ['/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*']

for i, (disease, values) in enumerate(data1.items()):
    bars = ax.bar(x + i*width - width*2, values, width, label=disease, 
                  color=disease_colors_group1[i], edgecolor='black', linewidth=1.5,
                  hatch=patterns[i % len(patterns)])
    
    # Add value labels
    for j, bar in enumerate(bars):
        height = bar.get_height()
        if height > 0:
            # Add case numbers too
            ethnic = data1.index[j]
            case_data = prevalence_data_group1[
                (prevalence_data_group1['ethnic_group'] == ethnic) & 
                (prevalence_data_group1['disease'] == disease)
            ]
            if not case_data.empty:
                cases = case_data['cases'].values[0]
                total = case_data['total'].values[0]
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%\n({cases}/{total})', 
                       ha='center', va='bottom', fontsize=8)

ax.set_xlabel('Ethnic Group', fontsize=16, fontweight='bold')
ax.set_ylabel('Prevalence (%)', fontsize=16, fontweight='bold')
ax.set_title('Detailed Analysis: Eye Diseases and Diabetes Prevalence Across Ethnic Groups', 
            fontsize=20, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(data1.index, rotation=45, ha='right', fontsize=12)
ax.legend(title='Disease Type', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12, 
         title_fontsize=14)
ax.grid(True, axis='y', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# Add background shading
for i in range(0, len(x), 2):
    ax.axvspan(i-0.5, i+0.5, alpha=0.05, color='gray')

plt.tight_layout()
plt.savefig('ethnic_disease_group1_advanced.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

# Chart 2: Cardiovascular and Respiratory Diseases
fig2, ax = plt.subplots(figsize=(18, 12))
data2 = data_group2_filtered.pivot(index='ethnic_group', columns='disease', values='prevalence').fillna(0)

# Sort by total prevalence
data2['Total'] = data2.sum(axis=1)
data2 = data2.sort_values('Total', ascending=False).drop('Total', axis=1)

x = np.arange(len(data2.index))
width = 0.25

for i, (disease, values) in enumerate(data2.items()):
    bars = ax.bar(x + i*width - width, values, width, label=disease,
                  color=disease_colors_group2[i], edgecolor='black', linewidth=1.5,
                  hatch=patterns[i % len(patterns)])
    
    # Add value labels with case numbers
    for j, bar in enumerate(bars):
        height = bar.get_height()
        if height > 0:
            ethnic = data2.index[j]
            case_data = prevalence_data_group2[
                (prevalence_data_group2['ethnic_group'] == ethnic) & 
                (prevalence_data_group2['disease'] == disease)
            ]
            if not case_data.empty:
                cases = case_data['cases'].values[0]
                total = case_data['total'].values[0]
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%\n({cases}/{total})', 
                       ha='center', va='bottom', fontsize=8)

ax.set_xlabel('Ethnic Group', fontsize=16, fontweight='bold')
ax.set_ylabel('Prevalence (%)', fontsize=16, fontweight='bold')
ax.set_title('Detailed Analysis: Cardiovascular and Respiratory Disease Prevalence Across Ethnic Groups', 
            fontsize=20, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(data2.index, rotation=45, ha='right', fontsize=12)
ax.legend(title='Disease Type', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12,
         title_fontsize=14)
ax.grid(True, axis='y', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# Add background shading
for i in range(0, len(x), 2):
    ax.axvspan(i-0.5, i+0.5, alpha=0.05, color='gray')

plt.tight_layout()
plt.savefig('ethnic_disease_group2_advanced.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print("\nAdvanced visualization completed!")
print("\nGenerated files:")
print("1. ethnic_disease_comprehensive_advanced.png - Comprehensive analysis with multiple chart types")
print("2. ethnic_disease_group1_advanced.png - Detailed eye diseases and diabetes analysis")
print("3. ethnic_disease_group2_advanced.png - Detailed cardiovascular and respiratory diseases analysis")

# Export data for MCP chart creation
# Prepare data for MCP charts
group1_data = []
for _, row in prevalence_data_group1.iterrows():
    if row['ethnic_group'] in valid_ethnic_groups:
        group1_data.append({
            'category': row['ethnic_group'],
            'value': row['prevalence'],
            'group': row['disease']
        })

group2_data = []
for _, row in prevalence_data_group2.iterrows():
    if row['ethnic_group'] in valid_ethnic_groups:
        group2_data.append({
            'category': row['ethnic_group'],
            'value': row['prevalence'],
            'group': row['disease']
        })

# Save data for reference
import json
with open('ethnic_disease_data_group1.json', 'w') as f:
    json.dump(group1_data, f, indent=2)

with open('ethnic_disease_data_group2.json', 'w') as f:
    json.dump(group2_data, f, indent=2)

print("\nData exported for MCP chart creation:")
print("- ethnic_disease_data_group1.json")
print("- ethnic_disease_data_group2.json") 