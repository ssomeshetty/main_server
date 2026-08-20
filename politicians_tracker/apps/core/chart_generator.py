import io
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server rendering
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Set institutional Seaborn plot theme
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

def generate_demographic_donut_chart(demographic_data):
    """
    Generates a high-level publication-quality SVG chart for constituency religion demographics
    using Python Matplotlib and Seaborn.
    """
    rel = demographic_data.get('religion_composition', {})
    
    labels = ['Hindu', 'Muslim', 'Christian', 'Jain', 'Buddhist', 'Sikh']
    percentages = [
        float(rel.get('hindu_pct', 0)),
        float(rel.get('muslim_pct', 0)),
        float(rel.get('christian_pct', 0)),
        float(rel.get('jain_pct', 0)),
        float(rel.get('buddhist_pct', 0)),
        float(rel.get('sikh_pct', 0))
    ]
    
    # Filter out categories with 0% for clean visual render
    filtered = [(l, p) for l, p in zip(labels, percentages) if p > 0.05]
    if not filtered:
        filtered = [('Hindu', 90.0), ('Muslim', 10.0)]
        
    plot_labels, plot_pcts = zip(*filtered)
    colors = sns.color_palette('colorblind', len(plot_labels))

    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    
    # Create Donut Chart
    wedges, texts, autotexts = ax.pie(
        plot_pcts, 
        labels=plot_labels, 
        autopct='%1.1f%%',
        startangle=140, 
        colors=colors,
        pctdistance=0.75,
        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
    )
    
    for text in texts:
        text.set_color('#1e293b')
        text.set_fontsize(10)
        text.set_weight('bold')
        
    for autotext in autotexts:
        autotext.set_color('#0f172a')
        autotext.set_fontsize(9)
        autotext.set_weight('bold')

    ax.set_title(
        f"Demographic Baseline Composition — {demographic_data.get('constituency_name', 'Constituency')}",
        fontsize=12, fontweight='bold', pad=15, color='#0f172a'
    )

    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='svg', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue().decode('utf-8')


def generate_electoral_bar_chart(electoral_data, candidate_name):
    """
    Generates a high-level publication-quality horizontal bar chart for election vote shares
    using Python Seaborn & Matplotlib.
    """
    winner_pct = float(electoral_data.get('vote_percentage', 0) or 0)
    runner_pct = float(electoral_data.get('runner_up_vote_pct', 0) or 0)
    runner_name = electoral_data.get('runner_up_name', 'Runner-up')

    df = pd.DataFrame({
        'Candidate': [candidate_name, runner_name],
        'Vote Share (%)': [winner_pct, runner_pct],
        'Role': ['Winner', 'Runner-Up']
    })

    fig, ax = plt.subplots(figsize=(7, 3), dpi=150)
    
    palette = {'Winner': '#059669', 'Runner-Up': '#64748b'}
    bars = sns.barplot(x='Vote Share (%)', y='Candidate', hue='Role', data=df, palette=palette, ax=ax, legend=False)
    
    ax.set_xlim(0, 100)
    ax.set_title(f"Vote Share Comparison — {electoral_data.get('constituency_name', 'Constituency')} ({electoral_data.get('election_year', 2023)})", fontsize=11, fontweight='bold', color='#0f172a')
    ax.set_xlabel('Vote Share (%)', fontsize=9, fontweight='bold', color='#475569')
    ax.set_ylabel('', fontsize=9)

    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.annotate(f"{width:.1f}%",
                        (width + 1.5, p.get_y() + p.get_height() / 2.),
                        ha='left', va='center', fontsize=9, fontweight='bold', color='#0f172a')

    sns.despine(top=True, right=True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='svg', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue().decode('utf-8')
