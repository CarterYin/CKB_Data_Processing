#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized Comprehensive Ethnic Group Analysis Chart - English Version
Enhanced version fixing pie chart labels, emoji display, and layout issues
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import numpy as np
from matplotlib import gridspec
from matplotlib.patches import FancyBboxPatch
import warnings
warnings.filterwarnings('ignore')

# Set high-quality English fonts and styling
plt.style.use('default')
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

# Color palette for professional look
COLORS = {
    'primary': '#2E86AB',      # Professional blue
    'secondary': '#A23B72',    # Deep pink
    'accent': '#F18F01',       # Orange
    'success': '#C73E1D',      # Red
    'info': '#6C5B7B',         # Purple
    'light': '#F5F5F5',        # Light gray
    'dark': '#2C3E50',         # Dark blue-gray
    'han': '#3498DB',          # Blue for Han
    'minority': '#E74C3C',     # Red for minorities
    'background': '#FAFAFA'    # Very light gray
}

# Extended color palette for multiple ethnic groups
ETHNIC_COLORS = [
    '#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6', 
    '#1ABC9C', '#34495E', '#E67E22', '#95A5A6', '#16A085',
    '#27AE60', '#2980B9', '#8E44AD', '#F1C40F', '#E8F5E8'
]

def load_and_process_data():
    """Load and process ethnic distribution data"""
    print("Loading and processing data...")
    
    # Read the TSV file
    df = pd.read_csv('analysis_result_eyes_realigned.tsv', sep='\t', 
                     usecols=['samples', 'id_ethnic_group_id'])
    
    # Ethnic mapping
    ethnic_mapping = {
        1: 'Han', 2: 'Mongol', 3: 'Hui', 4: 'Tibetan', 5: 'Uyghur',
        6: 'Miao', 7: 'Yi', 8: 'Zhuang', 9: 'Bouyei', 10: 'Korean',
        11: 'Manchu', 12: 'Dong', 13: 'Yao', 14: 'Bai', 15: 'Tujia',
        16: 'Hani', 17: 'Kazak', 18: 'Dai', 19: 'Li', 20: 'Lisu',
        21: 'Va', 22: 'She', 23: 'Gaoshan', 24: 'Lahu', 25: 'Shui',
        26: 'Dongxiang', 27: 'Naxi', 28: 'Jingpo', 29: 'Kirgiz', 30: 'Tu',
        31: 'Daur', 32: 'Mulao', 33: 'Qiang', 34: 'Blang', 35: 'Salar',
        36: 'Maonan', 37: 'Gelao', 38: 'Xibe'
    }
    
    # Process data
    total_samples = len(df)
    valid_data = df[df['id_ethnic_group_id'].notna()]
    valid_samples = len(valid_data)
    missing_samples = total_samples - valid_samples
    
    # Count ethnic groups
    ethnic_counts = valid_data['id_ethnic_group_id'].value_counts()
    
    # Map to names
    ethnic_names = {}
    for code, count in ethnic_counts.items():
        if pd.notna(code):
            ethnic_names[ethnic_mapping.get(int(code), f'Unknown_{int(code)}')] = count
    
    # Calculate additional statistics
    ethnic_series = pd.Series(ethnic_names).sort_values(ascending=False)
    minority_data = ethnic_series[ethnic_series.index != 'Han']
    
    stats = {
        'total_samples': total_samples,
        'valid_samples': valid_samples,
        'missing_samples': missing_samples,
        'completeness': valid_samples / total_samples * 100,
        'ethnic_groups_count': len(ethnic_names),
        'han_count': ethnic_names.get('Han', 0),
        'minority_count': valid_samples - ethnic_names.get('Han', 0),
        'han_percentage': ethnic_names.get('Han', 0) / valid_samples * 100,
        'minority_percentage': (valid_samples - ethnic_names.get('Han', 0)) / valid_samples * 100,
        'largest_minority': minority_data.index[0] if len(minority_data) > 0 else 'None',
        'largest_minority_count': minority_data.iloc[0] if len(minority_data) > 0 else 0,
        'smallest_minority_count': minority_data.iloc[-1] if len(minority_data) > 0 else 0,
        'average_minority_size': minority_data.mean() if len(minority_data) > 0 else 0,
        'diversity_index': len(minority_data)
    }
    
    return ethnic_names, stats

def create_title_section(fig, stats):
    """Create an attractive title section"""
    # Main title
    fig.suptitle('China Biobank Eye Cohort: Ethnic Group Distribution Analysis', 
                fontsize=18, fontweight='bold', y=0.96, color=COLORS['dark'])
    
    # Subtitle with key statistics
    subtitle = f"Total Samples: {stats['total_samples']:,} | Valid Data: {stats['valid_samples']:,} ({stats['completeness']:.1f}%) | Ethnic Groups: {stats['ethnic_groups_count']}"
    fig.text(0.5, 0.93, subtitle, ha='center', va='center', 
             fontsize=12, color=COLORS['info'], style='italic')

def create_overview_pie_chart(ax, ethnic_names, stats):
    """Create a clean overview pie chart with enhanced visibility for smaller segments"""
    # Prepare data - show top 5 + others
    ethnic_series = pd.Series(ethnic_names).sort_values(ascending=False)
    
    if len(ethnic_series) > 5:
        top_4 = ethnic_series.head(4)
        others = ethnic_series.tail(len(ethnic_series) - 4).sum()
        display_data = top_4.copy()
        display_data['Other Minorities'] = others
    else:
        display_data = ethnic_series
    
    # Calculate percentages for explode effect
    percentages = display_data.values / stats['valid_samples'] * 100
    
    # Create explode array - minorities get larger explode values for prominence
    explode_values = []
    ethnic_names_list = list(display_data.keys())
    
    for i, (ethnic_name, pct) in enumerate(zip(ethnic_names_list, percentages)):
        if ethnic_name == 'Han':  # Han ethnic group stays close to center
            explode_values.append(0.05)
        else:  # All minorities get exploded for prominence
            if pct < 1:        # Very small minority segments (< 1%)
                explode_values.append(0.5)  # Maximum explosion for visibility
            elif pct < 5:      # Small minority segments (1-5%)
                explode_values.append(0.45)  # High explosion
            elif pct < 15:     # Medium minority segments (5-15%)
                explode_values.append(0.4)  # Moderate explosion
            else:              # Large minority segments (> 15%)
                explode_values.append(0.35)  # Slight explosion
    
    # Enhanced colors - more prominent colors for ethnic minorities
    enhanced_colors = []
    ethnic_names_list = list(display_data.keys())
    
    for i, (ethnic_name, pct) in enumerate(zip(ethnic_names_list, percentages)):
        if ethnic_name == 'Han':  # Han ethnic group gets a moderate blue color
            enhanced_colors.append('#5DADE2')  # Soft blue for Han
        else:  # All minorities get highly vibrant, prominent colors
            if pct < 1:  # Very small minority segments get ultra-bright colors
                ultra_bright_colors = ['#FF1744', '#00E676', '#FF6D00', '#E91E63', '#00BCD4', '#FFC107']
                enhanced_colors.append(ultra_bright_colors[i % len(ultra_bright_colors)])
            elif pct < 5:  # Small minority segments get bright colors
                bright_minority_colors = ['#FF5722', '#4CAF50', '#FF9800', '#9C27B0', '#00ACC1', '#FFEB3B']
                enhanced_colors.append(bright_minority_colors[i % len(bright_minority_colors)])
            else:  # Larger minority segments get vivid colors
                vivid_minority_colors = ['#F44336', '#2196F3', '#FF5722', '#9C27B0', '#00BCD4', '#FF9800']
                enhanced_colors.append(vivid_minority_colors[i % len(vivid_minority_colors)])
    
    # Create pie chart with enhanced visual effects for minorities
    wedges, texts = ax.pie(
        display_data.values,
        labels=None,  # Remove direct labels
        autopct=None,  # Remove percentage display on slices
        startangle=70,  # Adjusted start angle for better small segment visibility
        explode=explode_values,  # Explode minorities for prominence
        colors=enhanced_colors,
        wedgeprops=dict(width=1, edgecolor='white', linewidth=0.1, alpha=0.9),  # Thicker borders, slight transparency
        shadow=False,  # Remove shadow for cleaner look
        textprops={'fontweight': 'bold'}  # Bold text for better readability
    )
    
    # No percentage text to enhance since autopct=None
    
    # Create legend with proper spacing
    legend_labels = []
    for name, count in display_data.items():
        percentage = count / stats['valid_samples'] * 100
        legend_labels.append(f'{name}\n({count:,}, {percentage:.1f}%)')
    
    ax.legend(wedges, legend_labels, 
              title="Ethnic Groups", 
              loc="center left", 
              bbox_to_anchor=(1.1, 0, 0.5, 1),
              fontsize=9,
              title_fontsize=10,
              frameon=True,
              fancybox=True,
              shadow=True)
    
    ax.set_title('Overall Ethnic Distribution', fontsize=14, fontweight='bold', 
                pad=15, color=COLORS['dark'])

def create_detailed_bar_chart(ax, ethnic_names):
    """Create an enhanced horizontal bar chart for minorities"""
    ethnic_series = pd.Series(ethnic_names).sort_values(ascending=False)
    minority_data = ethnic_series[ethnic_series.index != 'Han'].sort_values(ascending=True)
    
    if len(minority_data) > 0:
        y_positions = np.arange(len(minority_data))
        
        # Create horizontal bars with enhanced styling
        bars = ax.barh(y_positions, minority_data.values, 
                      color=ETHNIC_COLORS[1:len(minority_data)+1],
                      edgecolor='white', linewidth=1.5, alpha=0.85)
        
        # Add value labels with better positioning
        for i, (ethnic_name, count) in enumerate(minority_data.items()):
            ax.text(count + count*0.08, i, f'{count}', 
                   va='center', ha='left', fontsize=9, fontweight='medium')
        
        # Customize axes with better spacing
        ax.set_yticks(y_positions)
        ax.set_yticklabels(minority_data.index, fontsize=9)
        ax.set_xlabel('Population Count', fontsize=11, fontweight='medium')
        ax.set_title('Ethnic Minorities Distribution', fontsize=14, fontweight='bold', 
                    pad=12, color=COLORS['dark'])
        
        # Add subtle grid and formatting
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))

def create_han_minority_comparison(ax, stats):
    """Create Han vs Minority comparison with enhanced visualization"""
    categories = ['Han\nEthnic Group', 'Ethnic\nMinorities']
    values = [stats['han_count'], stats['minority_count']]
    percentages = [stats['han_percentage'], stats['minority_percentage']]
    
    # Create bars with enhanced styling
    bars = ax.bar(categories, values, 
                 color=[COLORS['han'], COLORS['minority']], 
                 alpha=0.85, edgecolor='white', linewidth=2,
                 width=0.6)
    
    # Add value and percentage labels with better formatting
    for i, (bar, val, pct) in enumerate(zip(bars, values, percentages)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + height*0.03,
               f'{val:,}\n({pct:.1f}%)', 
               ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_title('Population Comparison', fontsize=14, fontweight='bold', 
                pad=12, color=COLORS['dark'])
    ax.set_ylabel('Population Count', fontsize=11, fontweight='medium')
    
    # Enhanced formatting
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

def create_enhanced_statistics_panel(ax, stats, ethnic_names):
    """Create an enhanced statistics information panel with more content"""
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Create background box
    bbox = FancyBboxPatch((0.3, 0.5), 11.4, 11, boxstyle="round,pad=0.3", 
                         facecolor=COLORS['light'], edgecolor=COLORS['info'], 
                         linewidth=2, alpha=0.9)
    ax.add_patch(bbox)
    
    # Title
    ax.text(6, 10.8, 'Statistical Analysis Summary', ha='center', va='center', 
           fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # Basic statistics (left column)
    ax.text(1, 10, 'BASIC STATISTICS', ha='left', va='center', 
           fontsize=12, fontweight='bold', color=COLORS['info'])
    
    basic_stats = [
        f"• Total Samples: {stats['total_samples']:,}",
        f"• Valid Data: {stats['valid_samples']:,} ({stats['completeness']:.1f}%)",
        f"• Missing Data: {stats['missing_samples']:,} ({100-stats['completeness']:.1f}%)",
        f"• Data Quality: {'Good' if stats['completeness'] > 60 else 'Fair' if stats['completeness'] > 40 else 'Poor'}",
        f"• Ethnic Diversity: {stats['ethnic_groups_count']} distinct groups"
    ]
    
    for i, text in enumerate(basic_stats):
        ax.text(1.2, 9.4 - i*0.6, text, ha='left', va='center', 
               fontsize=10, color=COLORS['dark'])
    
    # Population distribution (right column)
    ax.text(7, 10, 'POPULATION DISTRIBUTION', ha='left', va='center', 
           fontsize=12, fontweight='bold', color=COLORS['info'])
    
    distribution_stats = [
        f"• Han Population: {stats['han_count']:,} ({stats['han_percentage']:.2f}%)",
        f"• Minority Population: {stats['minority_count']:,} ({stats['minority_percentage']:.2f}%)",
        f"• Largest Minority: {stats['largest_minority']} ({stats['largest_minority_count']} people)",
        f"• Smallest Minority: {stats['smallest_minority_count']} people",
        f"• Average Minority Size: {stats['average_minority_size']:.1f} people"
    ]
    
    for i, text in enumerate(distribution_stats):
        ax.text(7.2, 9.4 - i*0.6, text, ha='left', va='center', 
               fontsize=10, color=COLORS['dark'])
    
    # Detailed minority analysis
    ax.text(1, 6.5, 'TOP ETHNIC MINORITIES', ha='left', va='center', 
           fontsize=12, fontweight='bold', color=COLORS['info'])
    
    minority_series = pd.Series(ethnic_names)
    minority_data = minority_series[minority_series.index != 'Han'].sort_values(ascending=False)
    
    for i, (ethnic_name, count) in enumerate(minority_data.head(5).items()):
        pct = count / stats['valid_samples'] * 100
        ax.text(1.2, 6 - i*0.5, f"{i+1}. {ethnic_name}: {count} people ({pct:.3f}%)", 
               ha='left', va='center', fontsize=10, color=COLORS['dark'])
    
    # Statistical insights
    ax.text(7, 6.5, 'STATISTICAL INSIGHTS', ha='left', va='center', 
           fontsize=12, fontweight='bold', color=COLORS['info'])
    
    # Calculate diversity ratio
    diversity_ratio = stats['minority_count'] / stats['han_count'] * 1000
    representation_level = "High" if diversity_ratio > 20 else "Medium" if diversity_ratio > 10 else "Low"
    
    insights = [
        f"• Diversity Ratio: {diversity_ratio:.1f} minorities per 1000 Han",
        f"• Representation Level: {representation_level}",
        f"• Population Concentration: {stats['han_percentage']:.1f}% in single group",
        f"• Minority Fragmentation: {len(minority_data)} separate groups",
        f"• Data Reliability: {stats['completeness']:.1f}% completion rate"
    ]
    
    for i, text in enumerate(insights):
        ax.text(7.2, 6 - i*0.4, text, ha='left', va='center', 
               fontsize=10, color=COLORS['dark'])
    
    # Research implications
    ax.text(1, 3.5, 'RESEARCH IMPLICATIONS', ha='left', va='center', 
           fontsize=12, fontweight='bold', color=COLORS['info'])
    
    implications = [
        "• Sample represents typical Chinese population structure",
        "• Sufficient Han majority for robust statistical analysis", 
        "• Limited minority sample sizes may require grouped analysis",
        "• Missing data pattern should be investigated for bias",
        "• Geographic distribution analysis recommended"
    ]
    
    for i, text in enumerate(implications):
        ax.text(1.2, 3 - i*0.4, text, ha='left', va='center', 
               fontsize=9, color=COLORS['dark'])

def create_comprehensive_chart(ethnic_names, stats):
    """Create the optimized comprehensive chart"""
    print("Creating optimized comprehensive chart...")
    
    # Create figure with enhanced layout
    fig = plt.figure(figsize=(22, 14), facecolor=COLORS['background'])
    
    # Create title
    create_title_section(fig, stats)
    
    # Create optimized grid layout
    gs = gridspec.GridSpec(3, 5, figure=fig, 
                          left=0.03, right=0.96, top=0.88, bottom=0.06,
                          hspace=0.35, wspace=0.25,
                          height_ratios=[1, 1, 1.2], width_ratios=[1, 1, 1, 1, 0.5])
    
    # Create subplots with better positioning (moved left)
    ax1 = fig.add_subplot(gs[0, :2])   # Pie chart (wider, moved left)
    ax2 = fig.add_subplot(gs[0, 2:4])  # Bar chart (wider, moved left)
    ax3 = fig.add_subplot(gs[1, 1:3])  # Comparison (centered)
    ax4 = fig.add_subplot(gs[2, :])    # Statistics panel (full width)
    
    # Generate individual charts
    create_overview_pie_chart(ax1, ethnic_names, stats)
    create_detailed_bar_chart(ax2, ethnic_names)
    create_han_minority_comparison(ax3, stats)
    create_enhanced_statistics_panel(ax4, stats, ethnic_names)
    
    # Add enhanced footer
    footer_text = "Source: China Biobank Eye Cohort | Analysis: ID Card Ethnic Group Distribution | Generated: 2024 | High-Resolution Analytics"
    fig.text(0.5, 0.02, footer_text, ha='center', va='center', 
             fontsize=10, color=COLORS['info'], style='italic')
    
    return fig

def save_chart(fig):
    """Save the optimized chart in multiple high-quality formats"""
    print("Saving optimized comprehensive chart...")
    
    # Save as high-resolution PNG
    fig.savefig('comprehensive_ethnic_analysis_optimized.png', 
                dpi=300, bbox_inches='tight', facecolor=COLORS['background'],
                edgecolor='none', format='png')
    
    # Save as PDF for publications
    fig.savefig('comprehensive_ethnic_analysis_optimized.pdf', 
                bbox_inches='tight', facecolor=COLORS['background'],
                edgecolor='none', format='pdf')
    
    # Save as SVG for scalability
    fig.savefig('comprehensive_ethnic_analysis_optimized.svg', 
                bbox_inches='tight', facecolor=COLORS['background'],
                edgecolor='none', format='svg')
    
    print("✅ Optimized comprehensive charts saved:")
    print("   - comprehensive_ethnic_analysis_optimized.png (High-res PNG)")
    print("   - comprehensive_ethnic_analysis_optimized.pdf (Publication quality)")
    print("   - comprehensive_ethnic_analysis_optimized.svg (Scalable vector)")

def main():
    """Main execution function"""
    print("=" * 75)
    print("🎨 Creating Optimized Comprehensive Chart - English Version")
    print("=" * 75)
    
    try:
        # Load and process data
        ethnic_names, stats = load_and_process_data()
        
        # Create optimized comprehensive chart
        fig = create_comprehensive_chart(ethnic_names, stats)
        
        # Save chart
        save_chart(fig)
        
        # Display chart
        plt.show()
        
        print("\n" + "=" * 75)
        print("✅ Optimized comprehensive chart generation completed!")
        print("   Key improvements:")
        print("   - Pie chart uses legend instead of overlapping labels")
        print("   - Removed emoji icons for better compatibility") 
        print("   - Enhanced statistical analysis content")
        print("   - Optimized layout with better spacing")
        print("   - Professional formatting throughout")
        print("=" * 75)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please ensure the data file exists and is properly formatted")

if __name__ == "__main__":
    main() 