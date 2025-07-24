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

# Define ethnic group mapping (assuming based on China's official ethnic groups)
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
df['ethnic_group'] = df['ethnic_group'].fillna('Other/Unknown')

# Define disease columns and their full names
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
    'pre_18_pneu_bronch_tb': 'Pneumonia/Bronchitis/TB Before Age 18'
}

# Filter out 'Other/Unknown' ethnic group for cleaner visualization
df_filtered = df[df['ethnic_group'] != 'Other/Unknown'].copy()

# Calculate prevalence for each disease by ethnic group
def calculate_prevalence(df, disease_cols):
    prevalence_data = {}
    for col, name in disease_cols.items():
        if col in df.columns:
            # Create a clean dataset without NA values
            clean_df = df.dropna(subset=[col])
            if len(clean_df) > 0:
                prevalence = clean_df.groupby('ethnic_group')[col].agg(['sum', 'count'])
                prevalence['rate'] = (prevalence['sum'] / prevalence['count'] * 100).round(2)
                prevalence_data[name] = prevalence['rate']
    return pd.DataFrame(prevalence_data)

# Create comprehensive visualization
fig = plt.figure(figsize=(24, 20))
gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

# Color palette
colors = sns.color_palette("husl", n_colors=len(df_filtered['ethnic_group'].unique()))

# 1. Overall Disease Prevalence by Ethnic Group (Heatmap)
ax1 = fig.add_subplot(gs[0, :2])
all_diseases = {**disease_cols_group1, **disease_cols_group2}
prevalence_all = calculate_prevalence(df_filtered, all_diseases)
if not prevalence_all.empty:
    sns.heatmap(prevalence_all.T, annot=True, fmt='.1f', cmap='YlOrRd', 
                cbar_kws={'label': 'Prevalence (%)'}, ax=ax1)
    ax1.set_title('Disease Prevalence Heatmap Across Ethnic Groups', fontsize=16, pad=20)
    ax1.set_xlabel('Ethnic Group', fontsize=12)
    ax1.set_ylabel('Disease', fontsize=12)

# 2. Sample Size Distribution
ax2 = fig.add_subplot(gs[0, 2])
ethnic_counts = df_filtered['ethnic_group'].value_counts()
ax2.pie(ethnic_counts.values, labels=ethnic_counts.index, autopct='%1.1f%%', colors=colors)
ax2.set_title('Sample Distribution by Ethnic Group', fontsize=14, pad=20)

# 3. Eye Disease Prevalence (Group 1)
ax3 = fig.add_subplot(gs[1, :])
prevalence_group1 = calculate_prevalence(df_filtered, disease_cols_group1)
if not prevalence_group1.empty:
    x = np.arange(len(prevalence_group1.index))
    width = 0.15
    
    for i, (disease, values) in enumerate(prevalence_group1.items()):
        ax3.bar(x + i*width, values, width, label=disease, alpha=0.8)
    
    ax3.set_xlabel('Ethnic Group', fontsize=12)
    ax3.set_ylabel('Prevalence (%)', fontsize=12)
    ax3.set_title('Eye Diseases and Diabetes Prevalence by Ethnic Group', fontsize=16, pad=20)
    ax3.set_xticks(x + width * 2)
    ax3.set_xticklabels(prevalence_group1.index, rotation=45, ha='right')
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax3.grid(True, alpha=0.3)

# 4. Cardiovascular and Other Diseases (Group 2)
ax4 = fig.add_subplot(gs[2, :])
prevalence_group2 = calculate_prevalence(df_filtered, disease_cols_group2)
if not prevalence_group2.empty:
    x = np.arange(len(prevalence_group2.index))
    width = 0.25
    
    for i, (disease, values) in enumerate(prevalence_group2.items()):
        ax4.bar(x + i*width, values, width, label=disease, alpha=0.8)
    
    ax4.set_xlabel('Ethnic Group', fontsize=12)
    ax4.set_ylabel('Prevalence (%)', fontsize=12)
    ax4.set_title('Cardiovascular and Respiratory Disease Prevalence by Ethnic Group', fontsize=16, pad=20)
    ax4.set_xticks(x + width)
    ax4.set_xticklabels(prevalence_group2.index, rotation=45, ha='right')
    ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax4.grid(True, alpha=0.3)

plt.suptitle('Comprehensive Disease Distribution Analysis Across Ethnic Groups', fontsize=20, y=0.98)
plt.tight_layout()
plt.savefig('ethnic_disease_comprehensive_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# Create detailed comparison charts similar to the style requested
# Chart 1: Eye Diseases and Diabetes
fig1, ax = plt.subplots(figsize=(16, 10))

if not prevalence_group1.empty:
    prevalence_group1_sorted = prevalence_group1.sort_values(by=prevalence_group1.columns[0], ascending=False)
    x = np.arange(len(prevalence_group1_sorted.index))
    width = 0.15
    
    colors_group1 = plt.cm.Set3(np.linspace(0, 1, len(disease_cols_group1)))
    
    for i, (disease, values) in enumerate(prevalence_group1_sorted.items()):
        bars = ax.bar(x + i*width - width*2, values, width, label=disease, 
                      color=colors_group1[i], edgecolor='black', linewidth=0.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
    
    ax.set_xlabel('Ethnic Group', fontsize=14, fontweight='bold')
    ax.set_ylabel('Prevalence (%)', fontsize=14, fontweight='bold')
    ax.set_title('Eye Diseases and Diabetes Prevalence Distribution Across Ethnic Groups', 
                fontsize=18, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(prevalence_group1_sorted.index, rotation=45, ha='right', fontsize=12)
    ax.legend(title='Disease Type', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=11)
    ax.grid(True, axis='y', alpha=0.3)
    ax.set_axisbelow(True)
    
    # Add background color bands
    for i in range(0, len(x), 2):
        ax.axvspan(i-0.5, i+0.5, alpha=0.1, color='gray')

plt.tight_layout()
plt.savefig('ethnic_disease_group1_detailed.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 2: Cardiovascular and Other Diseases
fig2, ax = plt.subplots(figsize=(16, 10))

if not prevalence_group2.empty:
    prevalence_group2_sorted = prevalence_group2.sort_values(by=prevalence_group2.columns[0], ascending=False)
    x = np.arange(len(prevalence_group2_sorted.index))
    width = 0.25
    
    colors_group2 = plt.cm.Pastel1(np.linspace(0, 1, len(disease_cols_group2)))
    
    for i, (disease, values) in enumerate(prevalence_group2_sorted.items()):
        bars = ax.bar(x + i*width - width, values, width, label=disease, 
                      color=colors_group2[i], edgecolor='black', linewidth=0.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
    
    ax.set_xlabel('Ethnic Group', fontsize=14, fontweight='bold')
    ax.set_ylabel('Prevalence (%)', fontsize=14, fontweight='bold')
    ax.set_title('Cardiovascular and Respiratory Disease Prevalence Distribution Across Ethnic Groups', 
                fontsize=18, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(prevalence_group2_sorted.index, rotation=45, ha='right', fontsize=12)
    ax.legend(title='Disease Type', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=11)
    ax.grid(True, axis='y', alpha=0.3)
    ax.set_axisbelow(True)
    
    # Add background color bands
    for i in range(0, len(x), 2):
        ax.axvspan(i-0.5, i+0.5, alpha=0.1, color='gray')

plt.tight_layout()
plt.savefig('ethnic_disease_group2_detailed.png', dpi=300, bbox_inches='tight')
plt.close()

# Print summary statistics
print("\nSummary Statistics:")
print("="*50)
print(f"Total number of participants: {len(df)}")
print(f"Number of participants with ethnic group data: {len(df_filtered)}")
print(f"\nEthnic group distribution:")
for ethnic, count in ethnic_counts.items():
    print(f"  {ethnic}: {count} ({count/len(df_filtered)*100:.1f}%)")

print("\n" + "="*50)
print("Disease prevalence summary:")
for disease_group, disease_dict in [("Eye Diseases and Diabetes", disease_cols_group1), 
                                    ("Cardiovascular and Other Diseases", disease_cols_group2)]:
    print(f"\n{disease_group}:")
    for col, name in disease_dict.items():
        if col in df.columns:
            total_cases = df[col].sum()
            total_valid = df[col].notna().sum()
            if total_valid > 0:
                prevalence = total_cases / total_valid * 100
                print(f"  {name}: {prevalence:.2f}% ({int(total_cases)}/{total_valid})")

print("\nVisualization files created:")
print("  1. ethnic_disease_comprehensive_analysis.png - Comprehensive overview")
print("  2. ethnic_disease_group1_detailed.png - Eye diseases and diabetes detailed chart")
print("  3. ethnic_disease_group2_detailed.png - Cardiovascular and respiratory diseases detailed chart") 