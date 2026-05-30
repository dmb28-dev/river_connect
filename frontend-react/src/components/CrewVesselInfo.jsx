import {
  Ship, Gauge, Thermometer, Wind, Fuel, Anchor, Users, Cog, MapPin, Shield,
} from 'lucide-react';

const statusLabels = { moving: 'В движении', docked: 'На стоянке', mooring: 'Швартовка' };
const typeLabels = {
  passenger_liner: 'Пассажирский лайнер',
  cruise_ship: 'Круизное судно',
  fast_ferry: 'Скоростной паром',
};

const engineLabels = { running: 'Работает', standby: 'Ожидание', off: 'Выключен' };

function Metric({ icon: Icon, label, value, accent = 'text-primary' }) {
  return (
    <div className="bg-slate-700/50 rounded-lg p-3">
      <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
        <Icon size={14} className={accent} />
        {label}
      </div>
      <div className="font-semibold text-sm">{value}</div>
    </div>
  );
}

export default function CrewVesselInfo({ vessel, route, telemetry }) {
  if (!vessel) return null;

  const weather = vessel.weather_info || {};
  const tech = vessel.technical_info || {};
  const latest = telemetry?.[0];
  const fuelLevel = latest?.fuel_level ?? tech.fuel_level;
  const loadPercent = vessel.capacity
    ? Math.round((vessel.passenger_count / vessel.capacity) * 100)
    : 0;

  const eta = route?.estimated_arrival
    ? new Date(route.estimated_arrival).toLocaleString('ru-RU', {
        hour: '2-digit', minute: '2-digit', day: 'numeric', month: 'short',
      })
    : '—';

  const engines = tech.engines || {};

  return (
    <div className="space-y-3">
      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <Ship className="text-primary shrink-0" size={24} />
            <div>
              <h2 className="font-bold text-lg">{vessel.name}</h2>
              <p className="text-sm text-slate-400">
                {typeLabels[vessel.type] || vessel.type} • {statusLabels[vessel.status]}
              </p>
            </div>
          </div>
          <span className="text-xs px-2 py-1 rounded bg-warning/20 text-warning">Экипаж</span>
        </div>

        {route && (
          <div className="mt-3 text-sm border-t border-slate-700 pt-3">
            <span className="text-slate-400">Маршрут: </span>
            {route.departure_port} → {route.arrival_port}
            <div className="text-primary mt-1">ETA: {eta}</div>
          </div>
        )}
      </div>

      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
          <Gauge size={16} className="text-primary" /> Навигация
        </h3>
        <div className="grid grid-cols-2 gap-2">
          <Metric icon={Gauge} label="Скорость" value={`${vessel.current_speed.toFixed(1)} км/ч`} />
          <Metric icon={MapPin} label="Координаты" value={`${vessel.latitude.toFixed(4)}, ${vessel.longitude.toFixed(4)}`} />
          <Metric icon={Thermometer} label="Температура" value={`${weather.air_temp ?? '—'}°C / вода ${weather.water_temp ?? '—'}°C`} accent="text-warning" />
          <Metric icon={Wind} label="Погода" value={`${weather.wind ?? '—'} • ${weather.conditions ?? '—'}`} accent="text-slate-400" />
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
          <Cog size={16} className="text-warning" /> Техническое состояние
        </h3>
        <div className="grid grid-cols-2 gap-2">
          <Metric icon={Anchor} label="Осадка" value={`${tech.draft ?? '—'} м`} />
          <Metric icon={Ship} label="Водоизмещение" value={`${tech.displacement ?? '—'} т`} />
          <Metric icon={Fuel} label="Топливо" value={`${fuelLevel ?? '—'}%`} accent="text-warning" />
          <Metric icon={Shield} label="Главный двигатель" value={engineLabels[engines.main] || engines.main || '—'} accent="text-success" />
          <Metric icon={Cog} label="Вспом. двигатель" value={engineLabels[engines.aux] || engines.aux || '—'} />
          <Metric icon={Shield} label="Безопасность" value="Исправно" accent="text-success" />
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
          <Users size={16} className="text-primary" /> Загрузка судна
        </h3>
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-slate-400">Пассажиры на борту</span>
          <span className="font-semibold">{vessel.passenger_count} / {vessel.capacity}</span>
        </div>
        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${loadPercent > 90 ? 'bg-emergency' : loadPercent > 75 ? 'bg-warning' : 'bg-success'}`}
            style={{ width: `${Math.min(loadPercent, 100)}%` }}
          />
        </div>
        <p className="text-xs text-slate-500 mt-1">Загрузка: {loadPercent}%</p>
      </div>
    </div>
  );
}
