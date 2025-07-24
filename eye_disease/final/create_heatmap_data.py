import pandas as pd
import json

# Read data
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

# Filter ethnic groups with at least 10 samples
ethnic_counts = df['ethnic_group'].value_counts()
valid_ethnic_groups = ethnic_counts[ethnic_counts >= 10].index.tolist()

# Disease columns
all_diseases = {
    'glaucoma_diag': 'Glaucoma',
    'amd_diag': 'AMD', 
    'cataract_diag': 'Cataract',
    'diabetes_test': 'Diabetes Test',
    'has_diabetes_baseline': 'Diabetes History',
    'ihd_diag': 'IHD',
    'peri_art_dis_symptoms': 'PAD Symptoms',
    'pre_18_pneu_bronch_tb': 'Pneumonia/TB<18'
}

# Create scatter data for heatmap visualization
scatter_data = []
for i, ethnic in enumerate(valid_ethnic_groups):
    ethnic_df = df[df['ethnic_group'] == ethnic]
    
    for j, (col, disease_name) in enumerate(all_diseases.items()):
        if col in df.columns:
            valid_data = ethnic_df[ethnic_df[col].notna()]
            if len(valid_data) > 0:
                cases = valid_data[col].sum()
                total = len(valid_data)
                prevalence = (cases / total * 100) if total > 0 else 0
                
                scatter_data.append({
                    'x': ethnic,
                    'y': disease_name,
                    'value': round(prevalence, 2)
                })

# Save for scatter plot heatmap
with open('heatmap_scatter_data.json', 'w') as f:
    json.dump(scatter_data, f, indent=2)

print(f"Created heatmap data with {len(scatter_data)} points")
print(f"Ethnic groups: {valid_ethnic_groups}")
print(f"Diseases: {list(all_diseases.values())}") 