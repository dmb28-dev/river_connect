import { Ship, Thermometer, Wind, Gauge } from 'lucide-react';

const statusLabels = { moving: 'В движении', docked: 'На стоянке', mooring: 'Швартовка' };
const typeLabels = {
  passenger_liner: 'Пассажирский лайнер',
  cruise_ship: 'Круизное судно',
  fast_ferry: 'Скоростной паром',
};

export default function VesselInfo({ vessel, route }) {
  if (!vessel) return null;

  const weather = vessel.weather_info || {};
  const eta = route?.estimated_arrival
    ? new Date(route.estimated_arrival).toLocaleString('ru-RU', { hour: '2-digit', minute: '2-digit', day: 'numeric', month: 'short' })
    : '—';

  return (
    <div className="bg-slate-800 rounded-xl p-4 space-y-3 border border-slate-700">
      <div className="flex items-center gap-2">
        <Ship className="text-primary" size={24} />
        <div>
          <h2 className="font-bold text-lg">{vessel.name}</h2>
          <p className="text-sm text-slate-400">{typeLabels[vessel.type] || vessel.type} • {statusLabels[vessel.status]}</p>
        </div>
      </div>

      {route && (
        <div className="text-sm">
          <span className="text-slate-400">Маршрут: </span>
          {route.departure_port} → {route.arrival_port}
          <div className="text-primary mt-1">ETA: {eta}</div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="flex items-center gap-2 bg-slate-700/50 p-2 rounded">
          <Gauge size={16} className="text-primary" />
          <span>{vessel.current_speed.toFixed(1)} км/ч</span>
        </div>
        <div className="flex items-center gap-2 bg-slate-700/50 p-2 rounded">
          <Thermometer size={16} className="text-warning" />
          <span>{weather.air_temp ?? '—'}°C / вода {weather.water_temp ?? '—'}°C</span>
        </div>
        <div className="flex items-center gap-2 bg-slate-700/50 p-2 rounded col-span-2">
          <Wind size={16} className="text-slate-400" />
          <span>{weather.wind ?? '—'} • {weather.conditions ?? '—'}</span>
        </div>
      </div>
    </div>
  );
}
