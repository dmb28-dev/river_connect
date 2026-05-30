import { useState } from 'react';
import { AlertCircle, X } from 'lucide-react';
import { emergencyApi } from '../services/api';

export default function SOSButton({ onSent }) {
  const [showModal, setShowModal] = useState(false);
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);

  const sendSOS = async () => {
    setLoading(true);
    try {
      await emergencyApi.create({ location: location || 'Текущее местоположение' });
      setShowModal(false);
      setLocation('');
      onSent?.();
    } catch (e) {
      alert(e.response?.data?.detail || 'Ошибка отправки SOS');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="fixed bottom-24 right-4 z-50 w-16 h-16 rounded-full bg-emergency text-white flex items-center justify-center sos-pulse shadow-lg"
        aria-label="SOS"
      >
        <AlertCircle size={32} />
      </button>

      {showModal && (
        <div className="fixed inset-0 z-[100] bg-black/70 flex items-center justify-center p-4">
          <div className="bg-slate-800 rounded-xl p-6 max-w-sm w-full">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-emergency">Экстренный вызов</h3>
              <button onClick={() => setShowModal(false)}><X /></button>
            </div>
            <p className="text-sm text-slate-300 mb-4">
              Сигнал будет немедленно отправлен капитану с вашим местоположением.
            </p>
            <input
              type="text"
              placeholder="Где вы находитесь?"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full p-3 rounded-lg bg-slate-700 border border-slate-600 mb-4"
            />
            <div className="flex gap-3">
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 py-3 rounded-lg bg-slate-600"
              >
                Отмена
              </button>
              <button
                onClick={sendSOS}
                disabled={loading}
                className="flex-1 py-3 rounded-lg bg-emergency font-bold disabled:opacity-50"
              >
                {loading ? 'Отправка...' : 'Отправить SOS'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
