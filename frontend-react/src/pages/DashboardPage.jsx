import { useEffect, useState, useCallback } from 'react';
import { Map, Bell, LogOut, Users } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { vesselsApi, notificationsApi } from '../services/api';
import { createWebSocket, vibrateEmergency } from '../services/websocket';
import VesselMap from '../components/VesselMap';
import VesselInfo from '../components/VesselInfo';
import CrewVesselInfo from '../components/CrewVesselInfo';
import NotificationList from '../components/NotificationList';
import SOSButton from '../components/SOSButton';
import CrewPanel from '../components/CrewPanel';

export default function DashboardPage() {
  const { user, logout, isCrew } = useAuth();
  const [tab, setTab] = useState('map');
  const [vessel, setVessel] = useState(null);
  const [route, setRoute] = useState(null);
  const [telemetry, setTelemetry] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState('all');
  const [toast, setToast] = useState(null);

  const vesselId = user?.vessel_id || 1;

  const loadData = useCallback(async () => {
    try {
      const [vRes, rRes, tRes, nRes] = await Promise.all([
        vesselsApi.get(vesselId),
        vesselsApi.route(vesselId),
        vesselsApi.telemetry(vesselId),
        notificationsApi.list(filter === 'all' ? null : filter),
      ]);
      setVessel(vRes.data);
      setRoute(rRes.data);
      setTelemetry(tRes.data);
      setNotifications(nRes.data);
    } catch (e) {
      console.error(e);
    }
  }, [vesselId, filter]);

  useEffect(() => { loadData(); }, [loadData]);

  useEffect(() => {
    const wsVessel = createWebSocket(`/ws/vessels/${vesselId}`, (msg) => {
      if (msg.type === 'telemetry_update') {
        setVessel((v) => v ? { ...v, ...msg.data, current_speed: msg.data.speed } : v);
      }
    });

    const wsNotif = createWebSocket('/ws/notifications', (msg) => {
      if (msg.type === 'new_notification' || msg.type === 'emergency_alert') {
        setToast(msg.data);
        if (msg.type === 'emergency_alert') vibrateEmergency();
        loadData();
      }
    });

    let wsEmergency;
    if (isCrew) {
      wsEmergency = createWebSocket('/ws/emergency', (msg) => {
        if (msg.type === 'sos_alert') {
          setToast({ title: 'SOS!', content: `${msg.data.passenger_name}: ${msg.data.location}`, priority: 'critical' });
          vibrateEmergency();
          loadData();
        }
      });
    }

    return () => {
      wsVessel?.close();
      wsNotif?.close();
      wsEmergency?.close();
    };
  }, [vesselId, isCrew, loadData]);

  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(null), 5000);
      return () => clearTimeout(t);
    }
  }, [toast]);

  const tabs = [
    { id: 'map', icon: Map, label: 'Карта' },
    { id: 'notifications', icon: Bell, label: 'Уведомления' },
    ...(isCrew ? [{ id: 'crew', icon: Users, label: 'Панель' }] : []),
  ];

  return (
    <div className="h-screen flex flex-col bg-slate-900">
      <header className="flex items-center justify-between p-3 bg-slate-800 border-b border-slate-700">
        <div>
          <h1 className="font-bold">River Connect</h1>
          <p className="text-xs text-slate-400">{user?.full_name} • {isCrew ? 'Экипаж' : `Каюта ${user?.cabin_number || '—'}`}</p>
        </div>
        <button onClick={logout} className="p-2 hover:bg-slate-700 rounded"><LogOut size={20} /></button>
      </header>

      <main className="flex-1 overflow-hidden relative">
        {tab === 'map' && (
          <div className="h-full overflow-y-auto p-4 space-y-4 bg-slate-900">
            {isCrew ? (
              <CrewVesselInfo vessel={vessel} route={route} telemetry={telemetry} />
            ) : (
              <VesselInfo vessel={vessel} route={route} />
            )}

            <section className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
              <div className="px-4 py-2.5 border-b border-slate-700 flex items-center justify-between">
                <h3 className="font-semibold text-sm">Карта маршрута</h3>
                {vessel && (
                  <span className="text-xs text-slate-400">
                    {vessel.latitude.toFixed(4)}°, {vessel.longitude.toFixed(4)}°
                  </span>
                )}
              </div>
              <div className="h-52 sm:h-60">
                {vessel ? (
                  <VesselMap vessel={vessel} route={route} telemetry={telemetry} />
                ) : (
                  <div className="h-full flex items-center justify-center text-slate-500 text-sm">
                    Загрузка карты...
                  </div>
                )}
              </div>
            </section>
          </div>
        )}
        {tab === 'notifications' && (
          <NotificationList
            notifications={notifications}
            onRefresh={loadData}
            filter={filter}
            onFilterChange={setFilter}
          />
        )}
        {tab === 'crew' && isCrew && (
          <CrewPanel vesselId={vesselId} onRefresh={loadData} />
        )}

        {!isCrew && <SOSButton onSent={loadData} />}
      </main>

      <nav className="flex bg-slate-800 border-t border-slate-700 safe-area-bottom">
        {tabs.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`flex-1 flex flex-col items-center py-3 ${tab === id ? 'text-primary' : 'text-slate-400'}`}
          >
            <Icon size={22} />
            <span className="text-xs mt-1">{label}</span>
          </button>
        ))}
      </nav>

      {toast && (
        <div className={`fixed top-16 left-4 right-4 z-[200] p-4 rounded-lg shadow-lg ${
          toast.priority === 'critical' ? 'bg-emergency' : 'bg-primary'
        }`}>
          <strong>{toast.title}</strong>
          <p className="text-sm">{toast.content}</p>
        </div>
      )}
    </div>
  );
}
