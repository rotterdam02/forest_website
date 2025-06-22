from flask import Flask, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)

# Get absolute path to database
def get_db_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'uli', 'databases', 'forest_lost_filtered_database.db')

def get_combined_data():
    """Load and combine data from forest loss, forest value, and emissions databases using ISO as primary key"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load forest loss data
    forest_loss_path = os.path.join(base_dir, 'uli', 'databases', 'forest_lost_filtered_database.db')
    conn = sqlite3.connect(forest_loss_path)
    cursor = conn.cursor()
    cursor.execute('SELECT iso, umd_tree_cover_loss__ha, country_name FROM Countries')
    forest_loss_data = cursor.fetchall()
    conn.close()
    
    # Load forest value data
    forest_value_path = os.path.join(base_dir, 'uli', 'databases', 'sorted_forest_value_database.db')
    conn = sqlite3.connect(forest_value_path)
    cursor = conn.cursor()
    cursor.execute('SELECT iso, F2020 FROM Countries')
    forest_value_data = cursor.fetchall()
    conn.close()
    
    # Load emissions data
    emissions_path = os.path.join(base_dir, 'uli', 'databases', 'file_path_new_emissions_database.db')
    conn = sqlite3.connect(emissions_path)
    cursor = conn.cursor()
    cursor.execute('SELECT iso, year_ FROM Countries')
    emissions_data = cursor.fetchall()
    conn.close()
    
    # Create a dictionary for easy lookup using ISO as primary key
    combined_data = {}
    
    # Add forest loss data first
    for iso, loss, country_name in forest_loss_data:
        combined_data[iso] = {
            'iso': iso,
            'country_name': country_name,
            'forest_loss_ha': loss,
            'forest_value_million_ha': None,
            'forest_value_ha': None,
            'forest_loss_percentage': None,
            'emissions_million_tons_co2': None
        }
    
    # Add forest value data and calculate percentage
    for iso, value_million_ha in forest_value_data:
        if iso in combined_data:
            combined_data[iso]['forest_value_million_ha'] = value_million_ha
            # Convert from millions of hectares to hectares
            if value_million_ha and value_million_ha > 0:
                forest_value_ha = value_million_ha * 1000000  # Convert to hectares
                combined_data[iso]['forest_value_ha'] = forest_value_ha
                # Calculate forest loss percentage: (forest_loss_ha / forest_value_ha) * 100
                if combined_data[iso]['forest_loss_ha']:
                    combined_data[iso]['forest_loss_percentage'] = (combined_data[iso]['forest_loss_ha'] / forest_value_ha) * 100
        else:
            # If country not in forest loss data, add it with forest value only
            combined_data[iso] = {
                'iso': iso,
                'country_name': iso,  # Use ISO as country name if not available
                'forest_loss_ha': None,
                'forest_value_million_ha': value_million_ha,
                'forest_value_ha': value_million_ha * 1000000 if value_million_ha else None,
                'forest_loss_percentage': None,
                'emissions_million_tons_co2': None
            }
    
    # Add emissions data (in million tons of CO2)
    for iso, emissions in emissions_data:
        if iso in combined_data:
            combined_data[iso]['emissions_million_tons_co2'] = emissions
        else:
            # If country not in combined data, add it with emissions only
            combined_data[iso] = {
                'iso': iso,
                'country_name': iso,  # Use ISO as country name if not available
                'forest_loss_ha': None,
                'forest_value_million_ha': None,
                'forest_value_ha': None,
                'forest_loss_percentage': None,
                'emissions_million_tons_co2': emissions
            }
    
    return list(combined_data.values())

def get_forest_loss_percentage_data():
    """Get data specifically for forest loss percentage visualization"""
    data = get_combined_data()
    # Filter out countries with no percentage data or invalid values
    filtered_data = []
    for item in data:
        if (item['forest_loss_percentage'] is not None and 
            item['forest_loss_percentage'] > 0 and 
            item['forest_loss_percentage'] <= 100):  # Reasonable percentage range
            filtered_data.append(item)
    
    return filtered_data

def get_emissions_data():
    """Get data specifically for emissions visualization"""
    data = get_combined_data()
    # Filter out countries with no emissions data or invalid values
    filtered_data = []
    for item in data:
        if (item['emissions_million_tons_co2'] is not None and 
            item['emissions_million_tons_co2'] > 0):  # Only positive values
            filtered_data.append(item)
    
    return filtered_data

@app.route('/')
def index():
    # Get forest loss data for top countries table
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('SELECT iso, umd_tree_cover_loss__ha, country_name FROM Countries ORDER BY umd_tree_cover_loss__ha DESC LIMIT 10')
    top_countries = cursor.fetchall()
    conn.close()
    
    # Get combined data for the maps
    map_data = get_combined_data()
    percentage_data = get_forest_loss_percentage_data()
    emissions_data = get_emissions_data()
    
    return render_template('index.html', 
                         top_countries=top_countries,
                         map_data=map_data,
                         percentage_data=percentage_data,
                         emissions_data=emissions_data)

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/data')
def get_data():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('SELECT iso, umd_tree_cover_loss__ha, country_name FROM Countries')
    data = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries for JSON response
    result = []
    for row in data:
        result.append({
            'iso': row[0],
            'forest_loss': row[1],
            'country_name': row[2]
        })
    
    return jsonify(result)

@app.route('/analytics')
def analytics():
    # Get analytics data
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(umd_tree_cover_loss__ha) as total_loss FROM Countries')
    total_loss = cursor.fetchone()[0]
    conn.close()
    
    return render_template('analytics.html', total_loss=total_loss)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
