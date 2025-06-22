# Green Remedy - Forest Loss Analysis

A comprehensive web application for analyzing global forest loss and environmental impact data. Built with Flask and interactive data visualization.

## Features

### Three Interactive World Maps:
1. **Forest Loss (Hectares)** - Shows absolute forest loss in hectares across countries
2. **Forest Loss Percentage** - Shows forest loss as a percentage of total forest area
3. **CO₂ Emissions (Million Tons)** - Shows annual CO₂ emissions by country

### Data Sources:
- Forest loss data from Global Forest Watch
- Forest area data from World Bank
- CO₂ emissions data from international climate databases

### Technology Stack:
- **Backend:** Python Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Data Visualization:** Plotly.js
- **Database:** SQLite
- **Styling:** Bootstrap 5 with custom dark theme

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rotterdam02/forest_website.git
cd forest_website
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5001`

## Project Structure

```
forest_website/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Main webpage template
├── uli/
│   └── databases/        # SQLite database files
│       ├── forest_lost_filtered_database.db
│       ├── sorted_forest_value_database.db
│       └── file_path_new_emissions_database.db
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Usage

1. **Interactive Maps:** Use the selector buttons to switch between different environmental metrics
2. **Hover Information:** Hover over countries to see detailed data
3. **Top Countries Table:** View the top 10 countries by forest loss
4. **Responsive Design:** Works on desktop, tablet, and mobile devices

## Data Analysis

The application combines data from three databases:
- **Forest Loss:** Annual forest loss in hectares
- **Forest Value:** Total forest area in millions of hectares
- **Emissions:** Annual CO₂ emissions in million tons

Calculations include:
- Forest loss percentage: `(forest_loss_ha / forest_value_ha) × 100`
- Direct emissions data for environmental impact analysis

## Contributing

This project was created for educational purposes as part of a university assignment on climate change data visualization.

## License

This project is for educational use only. 