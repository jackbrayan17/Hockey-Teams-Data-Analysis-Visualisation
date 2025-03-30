from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

app = Flask(__name__)

# Load data from the CSV file
data = pd.read_csv('teams_data.csv')

@app.route('/')
def home():
    return render_template('index.html', data=data.to_dict(orient='records'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/dashboard_data')
def dashboard_data():
    # Prepare data for visualization
    average_wins = data.groupby('Team Name')['Wins'].mean().to_dict()
    total_goals = data.groupby('Team Name')['Goals For (GF)'].sum().to_dict()
    win_percentage = data.groupby('Team Name')['Win %'].mean().to_dict()
    total_losses = data.groupby('Team Name')['Losses'].sum().to_dict()
    total_ot_losses = data.groupby('Team Name')['OT Losses'].sum().to_dict()
    average_goals_for = data.groupby('Team Name')['Goals For (GF)'].mean().to_dict()
    average_goals_against = data.groupby('Team Name')['Goals Against (GA)'].mean().to_dict()
    total_games_played = data.groupby('Team Name').size().to_dict()
    average_plus_minus = data.groupby('Team Name')['+ / -'].mean().to_dict()
    max_wins = data.groupby('Team Name')['Wins'].max().to_dict()
    min_wins = data.groupby('Team Name')['Wins'].min().to_dict()
    total_points = (data['Wins'] * 2 + data['OT Losses']).groupby(data['Team Name']).sum().to_dict()

    return jsonify({
        'average_wins': average_wins,
        'total_goals': total_goals,
        'win_percentage': win_percentage,
        'total_losses': total_losses,
        'total_ot_losses': total_ot_losses,
        'average_goals_for': average_goals_for,
        'average_goals_against': average_goals_against,
        'total_games_played': total_games_played,
        'average_plus_minus': average_plus_minus,
        'max_wins': max_wins,
        'min_wins': min_wins,
        'total_points': total_points,
    })

@app.route('/search')
def search():
    query = request.args.get('q', '')
    filtered_data = data[data['Team Name'].str.contains(query, case=False)]
    return jsonify(filtered_data.to_dict(orient='records'))

@app.route('/statistics')
def statistics():
    stats = {
        'mean_wins': float(data['Wins'].mean()),
        'median_wins': float(data['Wins'].median()),
        'mode_wins': int(data['Wins'].mode()[0]) if not data['Wins'].mode().empty else None,
        'std_wins': float(data['Wins'].std()),
        'correlation_GF_Wins': float(data['Goals For (GF)'].corr(data['Wins'])),
        'correlation_Win_Percentage_GA': float(data['Win %'].corr(data['Goals Against (GA)']))
    }
    return jsonify(stats)

@app.route('/best_year/<team_name>')
def best_year(team_name):
    team_data = data[data['Team Name'] == team_name]
    if team_data.empty:
        return jsonify({'error': 'Team not found'}), 404
    best_year = team_data.loc[team_data['Win %'].idxmax()]
    return jsonify(best_year.to_dict())

@app.route('/team_performance/<team_name>')
def team_performance(team_name):
    team_data = data[data['Team Name'] == team_name]
    if team_data.empty:
        return jsonify({'error': 'Team not found'}), 404
    performance = team_data[['Year', 'Wins', 'Losses']]
    return jsonify(performance.to_dict(orient='records'))

@app.route('/correlation')
def correlation():
    correlation_data = {
        'win_goals': float(data['Wins'].corr(data['Goals For (GF)'])),
        'win_percentage_goals_against': float(data['Win %'].corr(data['Goals Against (GA)']))
    }
    return jsonify(correlation_data)

@app.route('/visualizations/<team_name>')
def visualizations(team_name):
    team_data = data[data['Team Name'] == team_name]
    if team_data.empty:
        return jsonify({'error': 'Team not found'}), 404

    # Visualization 1: Evolution of Wins
    plt.figure(figsize=(10, 5))
    plt.plot(team_data['Year'], team_data['Wins'], marker='o', label='Victoires')
    plt.title(f'Évolution des victoires de {team_name} sur plusieurs années')
    plt.xlabel('Année')
    plt.ylabel('Victoires')
    plt.grid()
    plt.xticks(team_data['Year'], rotation=45)
    plt.tight_layout()
    plt.savefig('static/victories_evolution.png')
    plt.close()

    # Visualization 2: Histogram of Goals Scored
    plt.figure(figsize=(10, 5))
    team_data.groupby('Year')['Goals For (GF)'].sum().plot(kind='bar', color='skyblue')
    plt.title('Nombre total de buts marqués par année')
    plt.xlabel('Année')
    plt.ylabel('Buts marqués')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/goals_per_year.png')
    plt.close()

    # Visualization 3: Boxplot of Wins by Team
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='Team Name', y='Wins', data=data)
    plt.title('Boxplot des victoires par équipe')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/victories_boxplot.png')
    plt.close()

    # Visualization 4: Heatmap of Average Performance by Year
    pivot_data = data.pivot_table(index='Year', values='Win %', aggfunc='mean')
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot_data, annot=True, cmap='YlGnBu', cbar_kws={'label': 'Pourcentage de Victoires'})
    plt.title('Heatmap des performances moyennes par année')
    plt.xlabel('Année')
    plt.ylabel('Moyenne des victoires')
    plt.tight_layout()
    plt.savefig('static/performance_heatmap.png')
    plt.close()

    # Visualization 5: Scatter Plot between Goals Scored and Win Percentage
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Goals For (GF)', y='Win %', data=data, hue='Team Name', palette='Set1', alpha=0.7)
    plt.title('Scatter plot : Buts marqués vs Pourcentage de victoires')
    plt.xlabel('Buts marqués (GF)')
    plt.ylabel('Pourcentage de victoires')
    plt.grid()
    plt.tight_layout()
    plt.savefig('static/goals_vs_wins_scatter.png')
    plt.close()

    # Visualization 6: Distribution of Team Performances for a Given Year
    year_to_analyze = team_data['Year'].mode()[0]  # Use the most common year for demonstration
    plt.figure(figsize=(10, 6))
    sns.histplot(data[data['Year'] == year_to_analyze]['Win %'], bins=10, kde=True)
    plt.title(f'Distribution des performances des équipes pour l\'année {year_to_analyze}')
    plt.xlabel('Pourcentage de victoires')
    plt.ylabel('Fréquence')
    plt.grid()
    plt.tight_layout()
    plt.savefig('static/performance_distribution.png')
    plt.close()

    return jsonify({
        'victories_evolution': 'static/victories_evolution.png',
        'goals_per_year': 'static/goals_per_year.png',
        'victories_boxplot': 'static/victories_boxplot.png',
        'performance_heatmap': 'static/performance_heatmap.png',
        'goals_vs_wins_scatter': 'static/goals_vs_wins_scatter.png',
        'performance_distribution': 'static/performance_distribution.png',
    })

@app.route('/download_results/<filename>')
def download_results(filename):
    return send_file(f'static/{filename}', as_attachment=True)

@app.route('/visualization_page')
def visualization_page():
    return render_template('visualization.html')

if __name__ == '__main__':
    # Ensure the static folder exists
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)