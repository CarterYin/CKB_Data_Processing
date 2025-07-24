#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
眼科疾病数据分析与可视化
基于analysis_result_eyes_realigned.tsv数据
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_and_prepare_data():
    """加载和预处理数据"""
    print("正在加载数据...")
    
    # 读取数据
    df = pd.read_csv('analysis_result_eyes_realigned.tsv', sep='\t', low_memory=False)
    
    print(f"数据形状: {df.shape}")
    print(f"列名: {df.columns.tolist()}")
    
    # 关注的变量
    key_vars = [
        'glaucoma_diag', 'amd_diag', 'cataract_diag', 'diabetes_test',
        'has_diabetes_baseline', 'ihd_diag', 'peri_art_dis_symptoms', 
        'pre_18_pneu_bronch_tb', 'is_female_baseline', 'age_at_study_date_x100_baseline'
    ]
    
    # 检查变量是否存在
    available_vars = [var for var in key_vars if var in df.columns]
    print(f"可用的关键变量: {available_vars}")
    
    return df, available_vars

def create_grouped_bar_chart(df, variables):
    """创建类似用户图片的分组柱状图"""
    
    # 准备数据 - 按性别和年龄组分组
    df_clean = df.copy()
    
    # 创建年龄组
    if 'age_at_study_date_x100_baseline' in df.columns:
        df_clean['age_group'] = pd.cut(df_clean['age_at_study_date_x100_baseline']/100, 
                                     bins=[0, 50, 65, 100], 
                                     labels=['<50岁', '50-65岁', '>65岁'])
    else:
        df_clean['age_group'] = 'All'
    
    # 性别分组
    if 'is_female_baseline' in df.columns:
        df_clean['gender'] = df_clean['is_female_baseline'].map({0: '男性', 1: '女性'})
    else:
        df_clean['gender'] = 'All'
    
    # 计算各疾病的患病率
    disease_vars = ['glaucoma_diag', 'amd_diag', 'cataract_diag', 'ihd_diag']
    available_disease_vars = [var for var in disease_vars if var in df.columns]
    
    # 创建统计数据
    stats_data = []
    
    for gender in df_clean['gender'].unique():
        if pd.isna(gender):
            continue
        for age_group in df_clean['age_group'].unique():
            if pd.isna(age_group):
                continue
            
            subset = df_clean[(df_clean['gender'] == gender) & 
                            (df_clean['age_group'] == age_group)]
            
            for disease in available_disease_vars:
                if disease in subset.columns:
                    prevalence = subset[disease].sum() / len(subset) * 100 if len(subset) > 0 else 0
                    stats_data.append({
                        'gender': gender,
                        'age_group': age_group,
                        'disease': disease.replace('_diag', '').replace('_', ' ').title(),
                        'prevalence': prevalence,
                        'count': subset[disease].sum(),
                        'total': len(subset)
                    })
    
    stats_df = pd.DataFrame(stats_data)
    
    # 创建分组柱状图
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 使用类似原图的颜色
    colors = ['#1f4e79', '#2e75b6', '#87ceeb', '#d3d3d3']
    
    # 创建分组图
    x_labels = []
    x_pos = []
    bar_width = 0.2
    
    genders = stats_df['gender'].unique()
    age_groups = stats_df['age_group'].unique()
    diseases = stats_df['disease'].unique()
    
    pos = 0
    for gender in genders:
        for age_group in age_groups:
            subset = stats_df[(stats_df['gender'] == gender) & 
                            (stats_df['age_group'] == age_group)]
            
            for i, disease in enumerate(diseases):
                disease_data = subset[subset['disease'] == disease]
                if not disease_data.empty:
                    prevalence = disease_data['prevalence'].iloc[0]
                    ax.bar(pos + i * bar_width, prevalence, bar_width, 
                          label=disease if pos == 0 else "", 
                          color=colors[i % len(colors)])
            
            x_labels.append(f"{gender}\n{age_group}")
            x_pos.append(pos + bar_width * (len(diseases) - 1) / 2)
            pos += 1
    
    ax.set_xlabel('人群分组', fontsize=12)
    ax.set_ylabel('患病率 (%)', fontsize=12)
    ax.set_title('不同人群中各种眼科疾病的患病率分布', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # 添加垂直分隔线
    for i in range(1, len(genders)):
        ax.axvline(x=i * len(age_groups) - 0.5, color='black', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('grouped_disease_prevalence.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return stats_df

def create_advanced_visualizations(df, variables):
    """创建高级可视化图表"""
    
    # 1. 相关性热力图
    numeric_vars = []
    for var in variables:
        if var in df.columns and df[var].dtype in ['int64', 'float64']:
            numeric_vars.append(var)
    
    if len(numeric_vars) > 1:
        plt.figure(figsize=(12, 10))
        correlation_matrix = df[numeric_vars].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5)
        plt.title('眼科疾病相关性热力图', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    # 2. 疾病共患率分析 - 桑基图样式
    disease_vars = ['glaucoma_diag', 'amd_diag', 'cataract_diag', 'ihd_diag']
    available_diseases = [var for var in disease_vars if var in df.columns]
    
    if len(available_diseases) >= 2:
        # 计算疾病组合
        disease_combinations = {}
        for _, row in df.iterrows():
            combo = []
            for disease in available_diseases:
                if pd.notna(row[disease]) and row[disease] == 1:
                    combo.append(disease.replace('_diag', ''))
            
            combo_str = '+'.join(sorted(combo)) if combo else '无疾病'
            disease_combinations[combo_str] = disease_combinations.get(combo_str, 0) + 1
        
        # 创建疾病组合柱状图
        plt.figure(figsize=(12, 8))
        sorted_combos = sorted(disease_combinations.items(), key=lambda x: x[1], reverse=True)[:10]
        
        combo_names = [combo for combo, count in sorted_combos]
        combo_counts = [count for combo, count in sorted_combos]
        
        bars = plt.bar(range(len(combo_names)), combo_counts, 
                      color=plt.cm.Set3(np.linspace(0, 1, len(combo_names))))
        
        plt.xlabel('疾病组合', fontsize=12)
        plt.ylabel('患者数量', fontsize=12)
        plt.title('眼科疾病共患情况分析（前10种组合）', fontsize=14, fontweight='bold')
        plt.xticks(range(len(combo_names)), combo_names, rotation=45, ha='right')
        
        # 添加数值标签
        for bar, count in zip(bars, combo_counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + count*0.01,
                    str(count), ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('disease_combinations.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    # 3. 年龄分布与疾病关系 - 小提琴图
    if 'age_at_study_date_x100_baseline' in df.columns and available_diseases:
        plt.figure(figsize=(14, 8))
        
        plot_data = []
        for disease in available_diseases[:4]:  # 限制为前4种疾病
            disease_patients = df[df[disease] == 1]['age_at_study_date_x100_baseline'] / 100
            healthy = df[df[disease] == 0]['age_at_study_date_x100_baseline'] / 100
            
            for age in disease_patients.dropna():
                plot_data.append({
                    'disease': disease.replace('_diag', '').title(),
                    'age': age,
                    'status': '患病'
                })
            
            # 随机采样健康人群以保持数据平衡
            healthy_sample = healthy.dropna().sample(min(len(disease_patients), len(healthy)))
            for age in healthy_sample:
                plot_data.append({
                    'disease': disease.replace('_diag', '').title(),
                    'age': age,
                    'status': '健康'
                })
        
        plot_df = pd.DataFrame(plot_data)
        
        if not plot_df.empty:
            sns.violinplot(data=plot_df, x='disease', y='age', hue='status', split=True)
            plt.title('不同疾病患者的年龄分布比较', fontsize=14, fontweight='bold')
            plt.xlabel('疾病类型', fontsize=12)
            plt.ylabel('年龄', fontsize=12)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('age_disease_violin.png', dpi=300, bbox_inches='tight')
            plt.show()
    
    # 4. 雷达图 - 不同年龄组的疾病风险
    if 'age_at_study_date_x100_baseline' in df.columns and len(available_diseases) >= 3:
        age_groups = pd.cut(df['age_at_study_date_x100_baseline']/100, 
                           bins=[0, 40, 50, 60, 70, 100], 
                           labels=['<40', '40-50', '50-60', '60-70', '>70'])
        
        radar_data = []
        for age_group in age_groups.unique():
            if pd.isna(age_group):
                continue
                
            group_data = df[age_groups == age_group]
            group_stats = {}
            
            for disease in available_diseases:
                prevalence = group_data[disease].sum() / len(group_data) * 100
                group_stats[disease.replace('_diag', '').title()] = prevalence
            
            radar_data.append({
                'age_group': str(age_group),
                **group_stats
            })
        
        if radar_data:
            # 创建雷达图
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            
            diseases = list(radar_data[0].keys())[1:]  # 除了age_group
            angles = np.linspace(0, 2 * np.pi, len(diseases), endpoint=False).tolist()
            angles += angles[:1]  # 闭合图形
            
            colors = plt.cm.Set1(np.linspace(0, 1, len(radar_data)))
            
            for i, data in enumerate(radar_data):
                values = [data[disease] for disease in diseases]
                values += values[:1]  # 闭合图形
                
                ax.plot(angles, values, 'o-', linewidth=2, 
                       label=f"{data['age_group']}岁", color=colors[i])
                ax.fill(angles, values, alpha=0.25, color=colors[i])
            
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(diseases)
            ax.set_ylim(0, max([max([data[d] for d in diseases]) for data in radar_data]) * 1.1)
            ax.set_title('不同年龄组疾病患病率雷达图', fontsize=14, fontweight='bold', y=1.08)
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
            ax.grid(True)
            
            plt.tight_layout()
            plt.savefig('radar_chart.png', dpi=300, bbox_inches='tight')
            plt.show()

def main():
    """主函数"""
    print("=== 眼科疾病数据分析与可视化 ===")
    
    # 加载数据
    df, variables = load_and_prepare_data()
    
    print(f"\n数据概览:")
    print(f"总样本数: {len(df)}")
    
    # 显示关键变量的基本统计
    for var in variables[:8]:  # 显示前8个变量
        if var in df.columns:
            if df[var].dtype in ['int64', 'float64']:
                print(f"{var}: 均值={df[var].mean():.3f}, 标准差={df[var].std():.3f}")
            else:
                print(f"{var}: 类型={df[var].dtype}")
    
    print("\n=== 开始创建可视化图表 ===")
    
    # 1. 创建分组柱状图（类似用户图片）
    print("\n1. 创建分组疾病患病率图表...")
    stats_df = create_grouped_bar_chart(df, variables)
    
    # 2. 创建高级可视化图表
    print("\n2. 创建高级可视化图表...")
    create_advanced_visualizations(df, variables)
    
    print("\n=== 所有图表创建完成！ ===")
    print("生成的图表文件:")
    print("- grouped_disease_prevalence.png: 分组疾病患病率图")
    print("- correlation_heatmap.png: 相关性热力图")
    print("- disease_combinations.png: 疾病共患分析图")
    print("- age_disease_violin.png: 年龄-疾病分布小提琴图")
    print("- radar_chart.png: 年龄组疾病风险雷达图")

if __name__ == "__main__":
    main() 