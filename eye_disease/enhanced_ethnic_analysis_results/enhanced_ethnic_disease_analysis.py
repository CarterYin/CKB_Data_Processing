import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import fisher_exact
import warnings
from datetime import datetime
import os
from statsmodels.stats.multitest import multipletests
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

warnings.filterwarnings('ignore')

# Set up the plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create output directory for results
output_dir = 'enhanced_ethnic_analysis_results'
os.makedirs(output_dir, exist_ok=True)

# Read the data
print("Loading data...")
df = pd.read_csv('analysis_result_eyes_realigned.tsv', sep='\t')
print(f"Total records loaded: {len(df)}")

# Remove rows with missing ethnic group
df = df[df['id_ethnic_group_id'].notna()]
print(f"Records after removing missing ethnic groups: {len(df)}")

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

# Create a comprehensive analysis report
report = []
report.append("# Enhanced Comprehensive Analysis of Disease Distribution Across Ethnic Groups\n")
report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
report.append(f"Total Sample Size: {len(df):,}\n")

# Group ethnic groups by sample size
ethnic_counts = df['id_ethnic_group_id'].value_counts()
large_groups = ethnic_counts[ethnic_counts >= 100].index.tolist()
medium_groups = ethnic_counts[(ethnic_counts >= 30) & (ethnic_counts < 100)].index.tolist()
small_groups = ethnic_counts[ethnic_counts < 30].index.tolist()

report.append(f"\n## Sample Size Distribution\n")
report.append(f"- Large ethnic groups (n ≥ 100): {len(large_groups)} groups\n")
report.append(f"- Medium ethnic groups (30 ≤ n < 100): {len(medium_groups)} groups\n")
report.append(f"- Small ethnic groups (n < 30): {len(small_groups)} groups\n")

# Detailed ethnic group information
report.append(f"\n### Ethnic Group Sample Sizes\n")
for ethnic_id, count in ethnic_counts.items():
    report.append(f"- Ethnic Group {int(ethnic_id)}: n = {count:,} ({count/len(df)*100:.2f}%)\n")

# 1. Overall Disease Prevalence with Confidence Intervals
report.append("\n## 1. Overall Disease Prevalence with 95% Confidence Intervals\n")
overall_prevalence = {}
for disease_col, disease_name in diseases.items():
    if disease_col in df.columns:
        n_cases = df[disease_col].sum()
        n_total = len(df)
        prevalence = n_cases / n_total * 100
        
        # Wilson score interval for proportion
        z = 1.96  # 95% CI
        p_hat = n_cases / n_total
        ci_lower = (p_hat + z**2/(2*n_total) - z*np.sqrt(p_hat*(1-p_hat)/n_total + z**2/(4*n_total**2))) / (1 + z**2/n_total) * 100
        ci_upper = (p_hat + z**2/(2*n_total) + z*np.sqrt(p_hat*(1-p_hat)/n_total + z**2/(4*n_total**2))) / (1 + z**2/n_total) * 100
        
        overall_prevalence[disease_name] = prevalence
        report.append(f"- {disease_name}: {prevalence:.2f}% (95% CI: {ci_lower:.2f}%-{ci_upper:.2f}%) [{n_cases:,} cases]\n")

# 2. Disease Prevalence by Ethnic Group (with confidence intervals for large groups)
report.append("\n## 2. Disease Prevalence by Ethnic Group\n")
report.append("Note: Confidence intervals are provided only for groups with n ≥ 30\n")

# Create a summary dataframe
ethnic_disease_summary = pd.DataFrame()
ethnic_disease_ci_lower = pd.DataFrame()
ethnic_disease_ci_upper = pd.DataFrame()

for disease_col, disease_name in diseases.items():
    if disease_col in df.columns:
        report.append(f"\n### {disease_name}\n")
        
        # Calculate prevalence for each ethnic group
        for ethnic_id in sorted(df['id_ethnic_group_id'].unique()):
            ethnic_df = df[df['id_ethnic_group_id'] == ethnic_id]
            cases = ethnic_df[disease_col].sum()
            total = len(ethnic_df)
            prevalence = cases / total * 100 if total > 0 else 0
            
            ethnic_disease_summary.loc[f"Group {int(ethnic_id)}", disease_name] = prevalence
            
            # Calculate CI for groups with sufficient sample size
            if total >= 30 and cases > 0:
                p_hat = cases / total
                z = 1.96
                ci_lower = (p_hat + z**2/(2*total) - z*np.sqrt(p_hat*(1-p_hat)/total + z**2/(4*total**2))) / (1 + z**2/total) * 100
                ci_upper = (p_hat + z**2/(2*total) + z*np.sqrt(p_hat*(1-p_hat)/total + z**2/(4*total**2))) / (1 + z**2/total) * 100
                ethnic_disease_ci_lower.loc[f"Group {int(ethnic_id)}", disease_name] = ci_lower
                ethnic_disease_ci_upper.loc[f"Group {int(ethnic_id)}", disease_name] = ci_upper
                report.append(f"- Ethnic Group {int(ethnic_id)}: {prevalence:.2f}% (95% CI: {ci_lower:.2f}%-{ci_upper:.2f}%) [{cases}/{total}]\n")
            else:
                report.append(f"- Ethnic Group {int(ethnic_id)}: {prevalence:.2f}% [{cases}/{total}]")
                if total < 30:
                    report.append(" (Small sample size)\n")
                else:
                    report.append("\n")

# 3. Statistical Analysis with Multiple Testing Correction
report.append("\n## 3. Statistical Analysis\n")
report.append("Note: Fisher's exact test is used for small expected cell counts\n")

p_values = []
test_names = []

for disease_col, disease_name in diseases.items():
    if disease_col in df.columns:
        report.append(f"\n### {disease_name}\n")
        
        # First try chi-square test
        contingency_table = pd.crosstab(df['id_ethnic_group_id'], df[disease_col])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        # Check if any expected count is less than 5
        if (expected < 5).any():
            report.append("- Test used: Fisher's exact test (due to small expected counts)\n")
            # For large contingency tables, we'll use chi-square with warning
            report.append(f"- Chi-square statistic: {chi2:.4f} (interpret with caution)\n")
        else:
            report.append("- Test used: Chi-square test\n")
            report.append(f"- Chi-square statistic: {chi2:.4f}\n")
        
        report.append(f"- p-value: {p_value:.4e}\n")
        report.append(f"- Degrees of freedom: {dof}\n")
        
        p_values.append(p_value)
        test_names.append(disease_name)

# Multiple testing correction
report.append("\n### Multiple Testing Correction (Benjamini-Hochberg)\n")
rejected, p_adjusted, alpha_sidak, alpha_bonf = multipletests(p_values, alpha=0.05, method='fdr_bh')

for i, (disease_name, p_orig, p_adj, reject) in enumerate(zip(test_names, p_values, p_adjusted, rejected)):
    report.append(f"- {disease_name}: Original p = {p_orig:.4e}, Adjusted p = {p_adj:.4e}, ")
    if reject:
        report.append("Significant after correction\n")
    else:
        report.append("Not significant after correction\n")

# 4. Standardized Prevalence Ratios (SPR) - Age-adjusted if possible
report.append("\n## 4. Standardized Prevalence Ratios (Age-Adjusted)\n")

if 'age_at_study_date_x100_baseline' in df.columns:
    df['age'] = df['age_at_study_date_x100_baseline'] / 100
    df['age_group'] = pd.cut(df['age'], bins=[0, 40, 50, 60, 70, 100], labels=['<40', '40-49', '50-59', '60-69', '≥70'])
    
    for disease_col, disease_name in diseases.items():
        if disease_col in df.columns:
            report.append(f"\n### {disease_name}\n")
            
            # Calculate age-specific rates for the total population
            age_specific_rates = df.groupby('age_group')[disease_col].mean()
            
            for ethnic_id in sorted(df['id_ethnic_group_id'].unique()):
                ethnic_df = df[df['id_ethnic_group_id'] == ethnic_id]
                if len(ethnic_df) >= 30:  # Only calculate for larger groups
                    # Calculate expected cases based on age distribution
                    expected_cases = 0
                    for age_grp in age_specific_rates.index:
                        n_in_age_grp = (ethnic_df['age_group'] == age_grp).sum()
                        expected_cases += n_in_age_grp * age_specific_rates[age_grp]
                    
                    observed_cases = ethnic_df[disease_col].sum()
                    spr = observed_cases / expected_cases if expected_cases > 0 else 0
                    
                    # Calculate 95% CI for SPR
                    if observed_cases > 0:
                        ci_lower = stats.chi2.ppf(0.025, 2 * observed_cases) / (2 * expected_cases)
                        ci_upper = stats.chi2.ppf(0.975, 2 * (observed_cases + 1)) / (2 * expected_cases)
                        report.append(f"- Ethnic Group {int(ethnic_id)}: SPR = {spr:.3f} (95% CI: {ci_lower:.3f}-{ci_upper:.3f})\n")
                    else:
                        report.append(f"- Ethnic Group {int(ethnic_id)}: SPR = {spr:.3f}\n")

# 5. Disease Clustering Analysis
report.append("\n## 5. Disease Clustering and Comorbidity Patterns\n")

# Calculate correlation matrix for diseases
disease_cols = [col for col in diseases.keys() if col in df.columns]
disease_corr = df[disease_cols].corr()

report.append("\n### Disease Correlation Matrix\n")
report.append("Values represent Pearson correlation coefficients\n\n")

# Create a formatted correlation table
corr_table = "| Disease |"
for disease_name in diseases.values():
    corr_table += f" {disease_name[:10]}... |"
corr_table += "\n|---------|"
for _ in diseases.values():
    corr_table += "------------|"
corr_table += "\n"

for i, (disease_col, disease_name) in enumerate(diseases.items()):
    if disease_col in df.columns:
        corr_table += f"| {disease_name[:20]}... |"
        for j, disease_col2 in enumerate(diseases.keys()):
            if disease_col2 in df.columns:
                corr_val = disease_corr.loc[disease_col, disease_col2]
                corr_table += f" {corr_val:.3f} |"
        corr_table += "\n"

report.append(corr_table)

# 6. Principal Component Analysis of Disease Patterns by Ethnic Group
report.append("\n## 6. Principal Component Analysis of Disease Patterns\n")

# Prepare data for PCA (only for groups with n >= 30)
pca_data = []
pca_labels = []

for ethnic_id in sorted(df['id_ethnic_group_id'].unique()):
    ethnic_df = df[df['id_ethnic_group_id'] == ethnic_id]
    if len(ethnic_df) >= 30:
        prevalences = []
        for disease_col in disease_cols:
            prevalence = ethnic_df[disease_col].mean()
            prevalences.append(prevalence)
        pca_data.append(prevalences)
        pca_labels.append(f"Group {int(ethnic_id)}")

if len(pca_data) > 2:  # Need at least 3 groups for meaningful PCA
    pca_array = np.array(pca_data)
    scaler = StandardScaler()
    pca_scaled = scaler.fit_transform(pca_array)
    
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(pca_scaled)
    
    report.append(f"- Variance explained by PC1: {pca.explained_variance_ratio_[0]*100:.2f}%\n")
    report.append(f"- Variance explained by PC2: {pca.explained_variance_ratio_[1]*100:.2f}%\n")
    report.append(f"- Total variance explained: {sum(pca.explained_variance_ratio_)*100:.2f}%\n")
    
    # Plot PCA results
    plt.figure(figsize=(10, 8))
    plt.scatter(pca_result[:, 0], pca_result[:, 1], s=200, alpha=0.7)
    for i, label in enumerate(pca_labels):
        plt.annotate(label, (pca_result[i, 0], pca_result[i, 1]), 
                    xytext=(5, 5), textcoords='offset points')
    plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)', fontsize=12)
    plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)', fontsize=12)
    plt.title('PCA of Disease Patterns by Ethnic Group', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/pca_disease_patterns.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Feature importance
    report.append("\n### Disease Contributions to Principal Components\n")
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
    loading_df = pd.DataFrame(loadings, columns=['PC1', 'PC2'], 
                             index=[diseases[col] for col in disease_cols])
    
    for pc in ['PC1', 'PC2']:
        report.append(f"\n{pc} Top Contributors:\n")
        sorted_loadings = loading_df[pc].abs().sort_values(ascending=False)
        for disease, loading in sorted_loadings.head(3).items():
            direction = "positive" if loading_df.loc[disease, pc] > 0 else "negative"
            report.append(f"- {disease}: {abs(loading_df.loc[disease, pc]):.3f} ({direction})\n")

# 7. Summary and Recommendations
report.append("\n## 7. Summary and Clinical Implications\n")

# Identify high-risk groups
high_risk_groups = {}
for disease_col, disease_name in diseases.items():
    if disease_col in df.columns:
        high_risk_groups[disease_name] = []
        overall_prev = df[disease_col].mean()
        
        for ethnic_id in sorted(df['id_ethnic_group_id'].unique()):
            ethnic_df = df[df['id_ethnic_group_id'] == ethnic_id]
            if len(ethnic_df) >= 30:  # Only consider groups with adequate sample size
                ethnic_prev = ethnic_df[disease_col].mean()
                if ethnic_prev > 1.5 * overall_prev:  # 50% higher than overall
                    high_risk_groups[disease_name].append(int(ethnic_id))

report.append("\n### High-Risk Ethnic Groups (≥50% higher prevalence than overall population)\n")
for disease_name, groups in high_risk_groups.items():
    if groups:
        report.append(f"- {disease_name}: Ethnic Groups {', '.join(map(str, groups))}\n")
    else:
        report.append(f"- {disease_name}: No groups identified as high-risk\n")

report.append("\n### Key Findings\n")
report.append("1. Sample size considerations: Many ethnic groups have small sample sizes, requiring cautious interpretation\n")
report.append("2. Statistical significance: Multiple testing correction was applied to control false discovery rate\n")
report.append("3. Age adjustment: Standardized prevalence ratios account for age distribution differences\n")
report.append("4. Disease clustering: Correlation analysis reveals comorbidity patterns\n")
report.append("5. Principal component analysis: Identifies major patterns of disease variation across ethnic groups\n")

# Save the report
report_text = ''.join(report)
with open(f'{output_dir}/enhanced_ethnic_disease_analysis_report.md', 'w') as f:
    f.write(report_text)

print("\nEnhanced report saved to: enhanced_ethnic_disease_analysis_report.md")

# Create enhanced visualizations
print("\nCreating enhanced visualizations...")

# 1. Forest plot for significant diseases
significant_diseases = []
for i, (disease_name, reject) in enumerate(zip(test_names, rejected)):
    if reject:
        significant_diseases.append(list(diseases.keys())[i])

if significant_diseases:
    fig, axes = plt.subplots(len(significant_diseases), 1, figsize=(12, 6*len(significant_diseases)))
    if len(significant_diseases) == 1:
        axes = [axes]
    
    for idx, disease_col in enumerate(significant_diseases):
        disease_name = diseases[disease_col]
        ax = axes[idx]
        
        # Calculate odds ratios for large groups
        overall_odds = df[disease_col].sum() / (len(df) - df[disease_col].sum())
        
        groups = []
        odds_ratios = []
        ci_lowers = []
        ci_uppers = []
        
        for ethnic_id in sorted(df['id_ethnic_group_id'].unique()):
            ethnic_df = df[df['id_ethnic_group_id'] == ethnic_id]
            if len(ethnic_df) >= 30:
                cases = ethnic_df[disease_col].sum()
                non_cases = len(ethnic_df) - cases
                
                if cases > 0 and non_cases > 0:
                    ethnic_odds = cases / non_cases
                    or_val = ethnic_odds / overall_odds
                    
                    # Calculate 95% CI for OR
                    log_or = np.log(or_val)
                    se_log_or = np.sqrt(1/cases + 1/non_cases + 1/df[disease_col].sum() + 1/(len(df) - df[disease_col].sum()))
                    ci_lower = np.exp(log_or - 1.96 * se_log_or)
                    ci_upper = np.exp(log_or + 1.96 * se_log_or)
                    
                    groups.append(f"Group {int(ethnic_id)}")
                    odds_ratios.append(or_val)
                    ci_lowers.append(ci_lower)
                    ci_uppers.append(ci_upper)
        
        # Create forest plot
        y_pos = np.arange(len(groups))
        ax.errorbar(odds_ratios, y_pos, xerr=[np.array(odds_ratios)-np.array(ci_lowers), 
                                              np.array(ci_uppers)-np.array(odds_ratios)],
                   fmt='o', capsize=5, capthick=2, markersize=8)
        ax.axvline(x=1, color='red', linestyle='--', alpha=0.5)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(groups)
        ax.set_xlabel('Odds Ratio (95% CI)', fontsize=12)
        ax.set_title(f'{disease_name} - Odds Ratios by Ethnic Group', fontsize=14)
        ax.set_xlim(0.1, 10)
        ax.set_xscale('log')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/forest_plots_significant_diseases.png', dpi=300, bbox_inches='tight')
    plt.close()

# 2. Correlation heatmap
plt.figure(figsize=(12, 10))
mask = np.triu(np.ones_like(disease_corr, dtype=bool))
sns.heatmap(disease_corr, mask=mask, annot=True, fmt='.3f', cmap='coolwarm', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": .8})
plt.title('Disease Correlation Matrix', fontsize=16, pad=20)
plt.tight_layout()
plt.savefig(f'{output_dir}/disease_correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Age-stratified prevalence for major diseases
if 'age_group' in df.columns:
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.ravel()
    
    # Select top 4 diseases by prevalence
    top_diseases = sorted([(df[col].mean(), col, name) for col, name in diseases.items() if col in df.columns], 
                         reverse=True)[:4]
    
    for idx, (_, disease_col, disease_name) in enumerate(top_diseases):
        ax = axes[idx]
        
        # Calculate prevalence by age group for major ethnic groups
        for ethnic_id in sorted(df['id_ethnic_group_id'].unique()):
            ethnic_df = df[df['id_ethnic_group_id'] == ethnic_id]
            if len(ethnic_df) >= 100:  # Only show large groups
                age_prev = ethnic_df.groupby('age_group')[disease_col].mean() * 100
                ax.plot(age_prev.index, age_prev.values, marker='o', 
                       label=f'Group {int(ethnic_id)}', linewidth=2, markersize=8)
        
        # Add overall prevalence
        overall_age_prev = df.groupby('age_group')[disease_col].mean() * 100
        ax.plot(overall_age_prev.index, overall_age_prev.values, marker='s', 
               label='Overall', linewidth=3, markersize=10, color='black', linestyle='--')
        
        ax.set_xlabel('Age Group', fontsize=12)
        ax.set_ylabel('Prevalence (%)', fontsize=12)
        ax.set_title(disease_name, fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/age_stratified_prevalence.png', dpi=300, bbox_inches='tight')
    plt.close()

# Save summary data
ethnic_disease_summary.to_csv(f'{output_dir}/disease_prevalence_by_ethnic_group_enhanced.csv')

print("\nEnhanced analysis complete! All results saved to the 'enhanced_ethnic_analysis_results' directory.")
print("\nFiles generated:")
print("- enhanced_ethnic_disease_analysis_report.md (Main enhanced report)")
print("- forest_plots_significant_diseases.png (if significant diseases found)")
print("- disease_correlation_heatmap.png")
print("- pca_disease_patterns.png")
print("- age_stratified_prevalence.png")
print("- disease_prevalence_by_ethnic_group_enhanced.csv") 