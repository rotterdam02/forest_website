// Initialize map
var map = L.map('map').setView([20, 0], 2);

// Add base map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Get forest loss data
fetch('/data')
    .then(response => response.json())
    .then(data => {
        // Create country layer
        fetch('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json')
            .then(response => response.json())
            .then(countries => {
                // Create a color scale
                const maxLoss = Math.max(...data.map(d => d.loss));
                const getColor = (loss) => {
                    if (loss === 0) return '#ffffff';
                    return `hsl(${(loss / maxLoss) * 120}, 100%, 50%)`;
                };

                // Add countries to map
                L.geoJSON(countries, {
                    style: feature => ({
                        fillColor: getColor(data.find(d => d.iso === feature.properties.iso_a3)?.loss || 0),
                        weight: 1,
                        opacity: 1,
                        color: 'white',
                        fillOpacity: 0.7
                    }),
                    onEachFeature: (feature, layer) => {
                        const countryData = data.find(d => d.iso === feature.properties.iso_a3);
                        if (countryData) {
                            layer.bindPopup(`
                                <h5>${countryData.name}</h5>
                                <p>Forest Loss: ${countryData.loss.toLocaleString()} ha</p>
                            `);
                            
                            layer.on('mouseover', () => {
                                layer.setStyle({
                                    weight: 3,
                                    color: '#666',
                                    fillOpacity: 0.8
                                });
                                document.getElementById('country-info').innerHTML = `
                                    <h5>${countryData.name}</h5>
                                    <p>Forest Loss: ${countryData.loss.toLocaleString()} ha</p>
                                `;
                            });
                            
                            layer.on('mouseout', () => {
                                layer.setStyle({
                                    weight: 1,
                                    color: 'white',
                                    fillOpacity: 0.7
                                });
                                document.getElementById('country-info').innerHTML = `
                                    <p>Select a country to view detailed information</p>
                                `;
                            });
                        }
                    }
                }).addTo(map);
            });
    });

// Analytics tracking
const trackPageView = () => {
    fetch('/track', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            page: window.location.pathname,
            timestamp: new Date().toISOString(),
        })
    });
};

// Track page view on load
trackPageView();

// Track scroll depth
let scrollDepth = 0;
window.addEventListener('scroll', () => {
    const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
    if (scrollPercent > scrollDepth) {
        scrollDepth = scrollPercent;
        fetch('/track-scroll', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                scrollDepth: scrollPercent,
                timestamp: new Date().toISOString(),
            })
        });
    }
});
