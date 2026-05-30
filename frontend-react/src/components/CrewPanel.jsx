import { useState, useEffect } from 'react';
import { emergencyApi, notificationsApi } from '../services/api';

export default function CrewPanel({ vesselId, onRefresh }) {
  const [tab, setTab] = useState('sos');
  const [notifForm, setNotifForm] = useState({ title: '', content: '', priority: 'low' });
  const [emergencyForm, setEmergencyForm] = useState({ title: '', content: '', instructions: '' });
  const [requests, setRequests] = useState([]);

  const loadRequests = async () => {
    const { data } = await emergencyApi.list();
    setRequests(data);
  };

  useEffect(() => { loadRequests(); }, []);

  const updateStatus = async (id, status) => {
    await emergencyApi.updateStatus(id, { status });
    loadRequests();
    onRefresh?.();
  };

  const sendNotification = async () => {
    await notificationsApi.create({ vessel_id: vesselId, ...notifForm, type: 'general' });
    setNotifForm({ title: '', content: '', priority: 'low' });
    onRefresh?.();
  };

  const sendEmergency = async () => {
    await notificationsApi.emergency({ vessel_id: vesselId, ...emergencyForm, priority: 'critical' });
    setEmergencyForm({ title: '', content: '', instructions: '' });
    onRefresh?.();
  };

  return (
    <div className="p-4 space-y-4">
      <div className="flex gap-2">
        {['sos', 'notify', 'alert'].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-3 py-1 rounded text-sm ${tab === t ? 'bg-primary' : 'bg-slate-700'}`}
          >
            {t === 'sos' ? 'SOS' : t === 'notify' ? 'Объявления' : 'Тревога'}
          </button>
        ))}
      </div>

      {tab === 'sos' && (
        <div className="space-y-3">
          {requests.map((r) => (
            <div key={r.id} className="p-3 bg-slate-800 rounded-lg border-l-4 border-emergency">
              <div className="font-semibold">{r.passenger_name} — {r.location}</div>
              <div className="text-sm text-slate-400">Каюта: {r.passenger_cabin} | {r.passenger_phone}</div>
              <div className="text-xs text-slate-500">{new Date(r.created_at).toLocaleString('ru-RU')}</div>
              <div className="flex gap-2 mt-2">
                {r.status === 'pending' && (
                  <button onClick={() => updateStatus(r.id, 'in_progress')} className="px-3 py-1 bg-warning rounded text-sm">
                    Принято
                  </button>
                )}
                {r.status !== 'resolved' && (
                  <button onClick={() => updateStatus(r.id, 'resolved')} className="px-3 py-1 bg-success rounded text-sm">
                    Решено
                  </button>
                )}
                <span className={`text-sm px-2 py-1 rounded ${
                  r.status === 'pending' ? 'bg-emergency/30' :
                  r.status === 'in_progress' ? 'bg-warning/30' : 'bg-success/30'
                }`}>{r.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === 'notify' && (
        <div className="space-y-3">
          <input
            placeholder="Заголовок"
            value={notifForm.title}
            onChange={(e) => setNotifForm({ ...notifForm, title: e.target.value })}
            className="w-full p-2 rounded bg-slate-700"
          />
          <textarea
            placeholder="Текст объявления"
            value={notifForm.content}
            onChange={(e) => setNotifForm({ ...notifForm, content: e.target.value })}
            className="w-full p-2 rounded bg-slate-700 h-24"
          />
          <button onClick={sendNotification} className="w-full py-2 bg-primary rounded">Отправить</button>
        </div>
      )}

      {tab === 'alert' && (
        <div className="space-y-3">
          <input
            placeholder="Заголовок тревоги"
            value={emergencyForm.title}
            onChange={(e) => setEmergencyForm({ ...emergencyForm, title: e.target.value })}
            className="w-full p-2 rounded bg-slate-700"
          />
          <textarea
            placeholder="Сообщение"
            value={emergencyForm.content}
            onChange={(e) => setEmergencyForm({ ...emergencyForm, content: e.target.value })}
            className="w-full p-2 rounded bg-slate-700 h-20"
          />
          <textarea
            placeholder="Инструкции для пассажиров"
            value={emergencyForm.instructions}
            onChange={(e) => setEmergencyForm({ ...emergencyForm, instructions: e.target.value })}
            className="w-full p-2 rounded bg-slate-700 h-20"
          />
          <button onClick={sendEmergency} className="w-full py-2 bg-emergency rounded font-bold">Отправить тревогу</button>
        </div>
      )}
    </div>
  );
}
