import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import ReactDOMServer from 'react-dom/server'; // Import ReactDOMServer for rendering the icons
import 'leaflet/dist/leaflet.css';
import './Marker.css';

import CottageOutlinedIcon from '@mui/icons-material/CottageOutlined';
import CottageIcon from '@mui/icons-material/Cottage';

// Function to create the custom icon
const createCustomIcon = (isSelected) => {
  const IconComponent = isSelected ? <CottageIcon /> : <CottageOutlinedIcon />; // JSX
  const svgString = ReactDOMServer.renderToString(IconComponent); // Convert to string for Leaflet
  
  return L.divIcon({
    html: `<div class="custom-icon">${svgString}</div>`,
    className: 'custom-div-icon',
    iconAnchor: [12, 41],
    popupAnchor: [7, -35],
  });
};

function MapComponent({ priceRange, county }) {
  const [locations, setLocations] = useState([]);
  const [selectedMarker, setSelectedMarker] = useState(null); // Store only the selected marker's case_number
  const ohioPosition = [40.4173, -82.9071]; // Ohio coordinates [latitude, longitude]

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/locations')
      .then(response => {
        setLocations(response.data);
      })
      .catch(error => {
        console.error('Error fetching locations:', error);
      });
  }, []);

  // Price Filter (Opening Bid)
  const filteredLocations = locations.filter(
    loc => Number(loc.opening_bid.replace(/[^0-9.-]+/g, "")) >= priceRange[0] &&
    Number(loc.opening_bid.replace(/[^0-9.-]+/g, "")) <= priceRange[1]
  );

  // County Filter
  const countyFilteredLocations = county
    ? filteredLocations.filter(loc => loc.county.toLowerCase() === county.toLowerCase())
    : filteredLocations;

  const validLocations = countyFilteredLocations.filter(loc => loc.lat !== null && loc.lon !== null);

  // Handle marker click to toggle selected marker
  const handleMarkerClick = (caseNumber) => {
    setSelectedMarker(prevSelected => (prevSelected === caseNumber ? null : caseNumber)); // Toggle selection
  };

  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <MapContainer center={ohioPosition} zoom={7} style={{ height: "80%", width: "100%" }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {validLocations.map(loc => (
          <Marker
            key={loc.case_number}
            position={[loc.lat, loc.lon]}
            icon={createCustomIcon(selectedMarker === loc.case_number)} // Only one marker will be selected
            eventHandlers={{
              click: () => handleMarkerClick(loc.case_number), // Handle marker click
            }}
          >
            <Popup>
              <div className="popup-container">
                <h3 className="popup-title">{loc.property_address}</h3>
                <div className="popup-details">
                  <p><strong>County:</strong> {loc.county}</p>
                  <p><strong>Start Date:</strong> {loc.start_date}</p>
                  <p><strong>Case Number:</strong> {loc.case_number}</p>
                  <p><strong>Parcel ID:</strong> {loc.parcel_id}</p>
                  {/* <p><strong>Property Address:</strong> {loc.property_address}</p> */}
                  <p><strong>Appraised Value:</strong> {loc.appraised_value}</p>
                  <p><strong>Opening Bid:</strong> {loc.opening_bid}</p>
                  <p><strong>Deposit Requirement:</strong> {loc.deposit_requirement}</p>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default MapComponent;
