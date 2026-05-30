import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Popup, CircleMarker } from 'react-leaflet';
import L from 'leaflet';

const vesselIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default function VesselMap({ vessel, route, telemetry }) {
  const mapRef = useRef(null);

  useEffect(() => {
    if (vessel && mapRef.current) {
      mapRef.current.setView([vessel.latitude, vessel.longitude], 10);
    }
  }, [vessel?.latitude, vessel?.longitude]);

  if (!vessel) return null;

  const waypoints = route?.waypoints || [];
  const routeLine = waypoints.map((wp) => [wp.lat, wp.lng]);
  const passedLine = telemetry?.length
    ? telemetry.slice(0, 5).map((t) => [t.latitude, t.longitude]).reverse()
    : [];

  return (
    <MapContainer
      center={[vessel.latitude, vessel.longitude]}
      zoom={10}
      className="h-full w-full"
      ref={mapRef}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {routeLine.length > 1 && (
        <Polyline positions={routeLine} color="#3B82F6" weight={3} dashArray="10 5" />
      )}
      {passedLine.length > 1 && (
        <Polyline positions={passedLine} color="#10B981" weight={4} />
      )}
      {waypoints.map((wp, i) => (
        <CircleMarker key={i} center={[wp.lat, wp.lng]} radius={6} color="#F59E0B" fillOpacity={0.8}>
          <Popup>{wp.name}</Popup>
        </CircleMarker>
      ))}
      <Marker position={[vessel.latitude, vessel.longitude]} icon={vesselIcon}>
        <Popup>
          <strong>{vessel.name}</strong><br />
          Скорость: {vessel.current_speed.toFixed(1)} км/ч<br />
          Статус: {vessel.status}
        </Popup>
      </Marker>
    </MapContainer>
  );
}
