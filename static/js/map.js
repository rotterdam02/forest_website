document.addEventListener('DOMContentLoaded', function() {
    // Initialize the map
    const map = L.map('map').setView([20, 0], 2);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Create a layer for country boundaries
    const countriesLayer = L.geoJson(null, {
        style: function(feature) {
            return {
                fillColor: getColor(feature.properties.forest_loss || 0),
                weight: 1,
                opacity: 1,
                color: 'white',
                fillOpacity: 0.8
            };
        },
        onEachFeature: onEachFeature
    }).addTo(map);

    // Add legend
    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'info legend');
        const grades = [0, 1000, 5000, 10000, 50000, 100000, 500000, 1000000];
        const labels = [];

        // Loop through our density intervals and generate a label with a colored square for each interval
        for (let i = 0; i < grades.length; i++) {
            const from = grades[i];
            const to = grades[i + 1];
            
            labels.push(
                '<i style="background:' + getColor(from + 1) + '"></i> ' +
                from + (to ? '–' + to : '+') + ' ha'
            );
        }


        div.innerHTML = labels.join('<br>');
        return div;
    };
    legend.addTo(map);

    // Function to get color based on forest loss value
    function getColor(d) {
        return d > 1000000 ? '#800026' :
               d > 500000  ? '#BD0026' :
               d > 100000  ? '#E31A1C' :
               d > 50000   ? '#FC4E2A' :
               d > 10000   ? '#FD8D3C' :
               d > 5000    ? '#FEB24C' :
               d > 1000    ? '#FED976' :
                            '#FFEDA0';
    }


    // Function to handle feature interaction
    function onEachFeature(feature, layer) {
        if (feature.properties && feature.properties.name) {
            layer.bindPopup(`<b>${feature.properties.name}</b><br>Forest Loss: ${feature.properties.forest_loss ? feature.properties.forest_loss.toLocaleString() + ' ha' : 'No data'}`);
            
            layer.on('click', function() {
                updateCountryInfo(feature.properties);
            });
        }
    }


    // Function to update country info panel
    function updateCountryInfo(properties) {
        const infoDiv = document.getElementById('country-info');
        if (!properties) {
            infoDiv.innerHTML = '<p class="text-muted">No data available for this country</p>';
            return;
        }

        
        infoDiv.innerHTML = `
            <h4>${properties.name || 'N/A'}</h4>
            <hr>
            <p><strong>Forest Loss:</strong> ${properties.forest_loss ? properties.forest_loss.toLocaleString() + ' ha' : 'No data'}</p>
            <p><strong>ISO Code:</strong> ${properties.iso_a3 || 'N/A'}</p>
            <p><strong>Region:</strong> ${properties.region_wb || 'N/A'}</p>
        `;
    }


    // Load country boundaries and forest loss data
    Promise.all([
        // Load country boundaries
        fetch('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json')
            .then(response => response.json()),
        // Load forest loss data
        fetch('/data')
            .then(response => response.json())
    ]).then(([geoData, forestData]) => {
        // Create a lookup for forest data by ISO code
        const forestLookup = {};
        forestData.forEach(country => {
            forestLookup[country.iso] = country.umd_tree_cover_loss__ha;
        });

        // Add forest loss data to GeoJSON features
        geoData.features.forEach(feature => {
            const isoCode = feature.properties.iso_a3;
            if (forestLookup.hasOwnProperty(isoCode)) {
                feature.properties.forest_loss = forestLookup[isoCode];
            }
        });

        // Add the GeoJSON data to the map
        countriesLayer.addData(geoData);
        
        // Fit the map to show all countries
        map.fitBounds(countriesLayer.getBounds());
    }).catch(error => {
        console.error('Error loading map data:', error);
        document.getElementById('country-info').innerHTML = 
            '<div class="alert alert-danger">Error loading map data. Please try again later.</div>';
    });
});
