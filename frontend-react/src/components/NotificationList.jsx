import { Bell, AlertTriangle, Info } from 'lucide-react';
import { notificationsApi } from '../services/api';

const priorityColors = {
  low: 'border-primary bg-blue-900/30',
  medium: 'border-yellow-500 bg-yellow-900/20',
  high: 'border-warning bg-orange-900/30',
  critical: 'border-emergency bg-red-900/40',
};

const typeIcons = {
  general: Info,
  emergency: AlertTriangle,
};

export default function NotificationList({ notifications, onRefresh, filter, onFilterChange }) {
  const markRead = async (id, requiresAck) => {
    await notificationsApi.markRead(id);
    onRefresh();
    if (requiresAck) return;
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex gap-2 p-3 border-b border-slate-700">
        {['all', 'general', 'emergency'].map((f) => (
          <button
            key={f}
            onClick={() => onFilterChange(f)}
            className={`px-3 py-1 rounded-full text-sm ${filter === f ? 'bg-primary' : 'bg-slate-700'}`}
          >
            {f === 'all' ? 'Все' : f === 'general' ? 'Общие' : 'Экстренные'}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {notifications.map((n) => {
          const Icon = typeIcons[n.type] || Bell;
          return (
            <div
              key={n.id}
              className={`p-4 rounded-lg border-l-4 ${priorityColors[n.priority]} ${!n.is_read ? 'ring-1 ring-white/20' : 'opacity-70'}`}
              onClick={() => markRead(n.id, n.requires_acknowledgment)}
            >
              <div className="flex items-start gap-2">
                <Icon size={18} className={n.type === 'emergency' ? 'text-emergency' : 'text-primary'} />
                <div className="flex-1">
                  <h4 className="font-semibold">{n.title}</h4>
                  <p className="text-sm text-slate-300 mt-1">{n.content}</p>
                  <span className="text-xs text-slate-500 mt-2 block">
                    {new Date(n.created_at).toLocaleString('ru-RU')}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
        {notifications.length === 0 && (
          <p className="text-center text-slate-500 py-8">Нет уведомлений</p>
        )}
      </div>
    </div>
  );
}
