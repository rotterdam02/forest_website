from flask import Flask, render_template
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
from scipy import stats
import numpy as np
import pycountry
import sqlite3

app = Flask(__name__)

def get_country_code(country_name):
    try:
        country = pycountry.countries.search_fuzzy(country_name)[0]
        return country.alpha_3
    except:
        return None

# Load and process data of the database files
# connect the website with the databases
emmissions_conn = sqlite3.connect("/Users/uliwintersperger/Desktop/uni/cssci/Semester_2/individual-assignments/codes/individual_website/wintersperger_individual-website 2/uli/databases/file_path_new_emissions_database.db")
forest_lost_conn = sqlite3.connect("/Users/uliwintersperger/Desktop/uni/cssci/Semester_2/individual-assignments/codes/individual_website/wintersperger_individual-website 2/uli/databases/forest_lost_filtered_database.db")
forest_value_total_conn = sqlite3.connect("/Users/uliwintersperger/Desktop/uni/cssci/Semester_2/individual-assignments/codes/individual_website/wintersperger_individual-website 2/uli/databases/sorted_forest_value_database.db")



# Clean up the data
emissions_df = emissions_df.dropna(subset=['emissions', 'country_code'])
forest_loss_df = forest_loss_df.dropna(subset=['forest_loss', 'country_code'])
carbon_storage_df = carbon_storage_df.dropna(subset=['carbon_storage', 'country_code'])

def create_emissions_plot():
    # Sort by emissions in descending order and take top 20
    sorted_df = emissions_df.sort_values('emissions', ascending=True).tail(20)
    
    fig = px.bar(sorted_df,
                 x='emissions',
                 y='Country',
                 orientation='h',
                 title='Top 20 Countries by CO2 Emissions',
                 labels={'emissions': 'CO2 Emissions (2018)',
                         'Country': 'Country'},
                 color='emissions',
                 color_continuous_scale='Reds')
    
    fig.update_layout(showlegend=False, height=600)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_forest_loss_plot():
    # Sort by forest loss in descending order and take top 20
    sorted_df = forest_loss_df.sort_values('forest_loss', ascending=True).tail(20)
    
    fig = px.bar(sorted_df,
                 x='forest_loss',
                 y='country_code',
                 orientation='h',
                 title='Top 20 Countries by Forest Loss',
                 labels={'forest_loss': 'Forest Loss (hectares)',
                         'country_code': 'Country Code'},
                 color='forest_loss',
                 color_continuous_scale='RdYlGn_r')
    
    fig.update_layout(showlegend=False, height=600)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_carbon_storage_plot():
    # Remove NaN values, sort by carbon storage, and take top 20
    clean_df = carbon_storage_df.dropna(subset=['carbon_storage'])
    sorted_df = clean_df.sort_values('carbon_storage', ascending=True).tail(20)
    
    fig = px.bar(sorted_df,
                 x='carbon_storage',
                 y='Country',
                 orientation='h',
                 title='Top 20 Countries by Forest Carbon Storage',
                 labels={'carbon_storage': 'Carbon Storage (2020)',
                         'Country': 'Country'},
                 color='carbon_storage',
                 color_continuous_scale='Viridis')
    
    fig.update_layout(showlegend=False, height=600)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def perform_correlation_analysis():
    try:
        # Merge datasets on country code
        emissions_forest = pd.merge(emissions_df, forest_loss_df, on='country_code', how='inner')
        emissions_carbon = pd.merge(emissions_df, carbon_storage_df, on='country_code', how='inner')
        forest_carbon = pd.merge(forest_loss_df, carbon_storage_df, on='country_code', how='inner')
        
        # Calculate correlations
        corr_emissions_loss = stats.pearsonr(emissions_forest['emissions'], emissions_forest['forest_loss'])
        corr_emissions_storage = stats.pearsonr(emissions_carbon['emissions'], emissions_carbon['carbon_storage'])
        corr_loss_storage = stats.pearsonr(forest_carbon['forest_loss'], forest_carbon['carbon_storage'])
        
        return {
            'emissions_loss': {
                'correlation': f"{round(corr_emissions_loss[0], 3)} ({len(emissions_forest)} countries)",
                'p_value': f"{round(corr_emissions_loss[1], 4)}"
            },
            'emissions_storage': {
                'correlation': f"{round(corr_emissions_storage[0], 3)} ({len(emissions_carbon)} countries)",
                'p_value': f"{round(corr_emissions_storage[1], 4)}"
            },
            'loss_storage': {
                'correlation': f"{round(corr_loss_storage[0], 3)} ({len(forest_carbon)} countries)",
                'p_value': f"{round(corr_loss_storage[1], 4)}"
            }
        }
    except Exception as e:
        print(f'Error in correlation analysis: {str(e)}')
        return {
            'emissions_loss': {'correlation': 'Error', 'p_value': 'N/A'},
            'emissions_storage': {'correlation': 'Error', 'p_value': 'N/A'},
            'loss_storage': {'correlation': 'Error', 'p_value': 'N/A'}
        }

@app.route('/')
def index():
    emissions_plot = create_emissions_plot()
    forest_loss_plot = create_forest_loss_plot()
    carbon_storage_plot = create_carbon_storage_plot()
    correlations = perform_correlation_analysis()
    
    return render_template('index.html',
                         emissions_plot=emissions_plot,
                         forest_loss_plot=forest_loss_plot,
                         carbon_storage_plot=carbon_storage_plot,
                         correlations=correlations)

if __name__ == '__main__':
    app.run(debug=True)
