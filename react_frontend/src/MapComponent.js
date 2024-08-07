import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconAnchor: [12, 41] // Point of the icon which will correspond to marker's location
});

L.Marker.prototype.options.icon = DefaultIcon;

function MapComponent() {
  const [locations, setLocations] = useState([]);
  const ohioPosition = [40.4173, -82.9071]; // Ohio coordinates [latitude, longitude]

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/locations')
      .then(response => {
        console.log('Fetched locations:', response.data);  // Debugging
        setLocations(response.data);
      })
      .catch(error => {
        console.error('Error fetching locations:', error);
      });
  }, []);

  // Filter out locations with null latitude or longitude
  const validLocations = locations.filter(loc => loc.lat !== null && loc.lng !== null);

  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <MapContainer center={ohioPosition} zoom={7} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {validLocations.map(loc => ( 
          <Marker key={loc.case_number} position={[loc.lat, loc.lon]}>
            <Popup>
              <strong>County:</strong> {loc.county}<br />
              <strong>Start Date:</strong> {loc.start_date}<br />
              <strong>Case Number:</strong> {loc.case_number}<br />
              <strong>Parcel ID:</strong> {loc.parcel_id}<br />
              <strong>Property Address:</strong> {loc.property_address}<br />
              <strong>Appraised Value:</strong> {loc.appraised_value}<br />
              <strong>Opening Bid:</strong> {loc.opening_bid}<br />
              <strong>Deposit Requirement:</strong> {loc.deposit_requirement}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default MapComponent;
