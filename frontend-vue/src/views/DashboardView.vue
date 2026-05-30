<template>
  <div class="h-screen flex flex-col">
    <header class="flex justify-between items-center p-3 bg-slate-800">
      <div>
        <h1 class="font-bold">River Connect</h1>
        <p class="text-xs text-slate-400">{{ auth.user?.full_name }}</p>
      </div>
      <button @click="auth.logout(); $router.push('/login')" class="text-sm text-slate-400">Выход</button>
    </header>

    <div class="flex gap-2 p-2 bg-slate-800 border-b border-slate-700">
      <button v-for="t in tabs" :key="t.id" @click="tab = t.id"
        :class="['px-3 py-1 rounded text-sm', tab === t.id ? 'bg-primary' : 'bg-slate-700']">
        {{ t.label }}
      </button>
    </div>

    <main class="flex-1 overflow-hidden">
      <div v-if="tab === 'map'" class="h-full overflow-y-auto p-4 space-y-4 bg-slate-900">
        <!-- Пассажир -->
        <div v-if="!auth.isCrew && vessel" class="bg-slate-800 rounded-xl p-4 border border-slate-700 space-y-3">
          <h2 class="font-bold text-lg">{{ vessel.name }}</h2>
          <p class="text-sm text-slate-400">{{ typeLabel(vessel.type) }} • {{ statusLabel(vessel.status) }}</p>
          <p v-if="route" class="text-sm">{{ route.departure_port }} → {{ route.arrival_port }}</p>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <div class="bg-slate-700/50 p-2 rounded">{{ vessel.current_speed?.toFixed(1) }} км/ч</div>
            <div class="bg-slate-700/50 p-2 rounded">{{ weatherText(vessel) }}</div>
          </div>
        </div>

        <!-- Экипаж -->
        <template v-if="auth.isCrew && vessel">
          <div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <div class="flex justify-between items-start">
              <div>
                <h2 class="font-bold text-lg">{{ vessel.name }}</h2>
                <p class="text-sm text-slate-400">{{ typeLabel(vessel.type) }} • {{ statusLabel(vessel.status) }}</p>
              </div>
              <span class="text-xs px-2 py-1 rounded bg-warning/20 text-warning">Экипаж</span>
            </div>
            <p v-if="route" class="text-sm mt-3 pt-3 border-t border-slate-700">{{ route.departure_port }} → {{ route.arrival_port }}</p>
          </div>

          <div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <h3 class="text-sm font-semibold text-slate-300 mb-3">Навигация</h3>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div class="bg-slate-700/50 p-2 rounded"><span class="text-slate-400 text-xs block">Скорость</span>{{ vessel.current_speed?.toFixed(1) }} км/ч</div>
              <div class="bg-slate-700/50 p-2 rounded"><span class="text-slate-400 text-xs block">Координаты</span>{{ vessel.latitude?.toFixed(4) }}, {{ vessel.longitude?.toFixed(4) }}</div>
              <div class="bg-slate-700/50 p-2 rounded col-span-2"><span class="text-slate-400 text-xs block">Погода</span>{{ weatherText(vessel) }}</div>
            </div>
          </div>

          <div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <h3 class="text-sm font-semibold text-slate-300 mb-3">Техническое состояние</h3>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div class="bg-slate-700/50 p-2 rounded"><span class="text-slate-400 text-xs block">Осадка</span>{{ vessel.technical_info?.draft ?? '—' }} м</div>
              <div class="bg-slate-700/50 p-2 rounded"><span class="text-slate-400 text-xs block">Водоизмещение</span>{{ vessel.technical_info?.displacement ?? '—' }} т</div>
              <div class="bg-slate-700/50 p-2 rounded"><span class="text-slate-400 text-xs block">Топливо</span>{{ vessel.technical_info?.fuel_level ?? '—' }}%</div>
              <div class="bg-slate-700/50 p-2 rounded"><span class="text-slate-400 text-xs block">Двигатели</span>{{ engineText(vessel) }}</div>
            </div>
          </div>

          <div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <h3 class="text-sm font-semibold text-slate-300 mb-3">Загрузка</h3>
            <div class="flex justify-between text-sm mb-2">
              <span class="text-slate-400">Пассажиры</span>
              <span>{{ vessel.passenger_count }} / {{ vessel.capacity }}</span>
            </div>
            <div class="h-2 bg-slate-700 rounded-full overflow-hidden">
              <div class="h-full bg-success rounded-full" :style="{ width: loadPercent(vessel) + '%' }"></div>
            </div>
          </div>
        </template>

        <section class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
          <div class="px-4 py-2.5 border-b border-slate-700 flex justify-between items-center">
            <h3 class="font-semibold text-sm">Карта маршрута</h3>
            <span v-if="vessel" class="text-xs text-slate-400">{{ vessel.latitude?.toFixed(4) }}°, {{ vessel.longitude?.toFixed(4) }}°</span>
          </div>
          <div ref="mapEl" class="h-52 w-full"></div>
        </section>
      </div>

      <div v-if="tab === 'notifications'" class="p-3 space-y-3 overflow-y-auto h-full">
        <div v-for="n in notifications" :key="n.id" @click="markRead(n.id)"
          :class="['p-4 rounded-lg border-l-4', n.type === 'emergency' ? 'border-emergency bg-red-900/30' : 'border-primary bg-blue-900/20']">
          <h4 class="font-semibold">{{ n.title }}</h4>
          <p class="text-sm text-slate-300">{{ n.content }}</p>
        </div>
      </div>

      <div v-if="tab === 'crew' && auth.isCrew" class="p-3 space-y-3 overflow-y-auto h-full">
        <div v-for="r in emergencies" :key="r.id" class="p-3 bg-slate-800 rounded border-l-4 border-emergency">
          <div class="font-semibold">{{ r.passenger_name }} — {{ r.location }}</div>
          <div class="flex gap-2 mt-2">
            <button v-if="r.status !== 'resolved'" @click="updateSos(r.id, 'in_progress')" class="px-2 py-1 bg-warning rounded text-sm">Принято</button>
            <button v-if="r.status !== 'resolved'" @click="updateSos(r.id, 'resolved')" class="px-2 py-1 bg-success rounded text-sm">Решено</button>
          </div>
        </div>
      </div>

      <button v-if="!auth.isCrew" @click="showSos = true"
        class="fixed bottom-6 right-4 w-14 h-14 rounded-full bg-emergency flex items-center justify-center text-xl font-bold z-50">
        SOS
      </button>
    </main>

    <div v-if="showSos" class="fixed inset-0 bg-black/70 flex items-center justify-center z-[100] p-4">
      <div class="bg-slate-800 rounded-xl p-6 max-w-sm w-full">
        <h3 class="text-xl font-bold text-emergency mb-4">Экстренный вызов</h3>
        <input v-model="sosLocation" placeholder="Где вы находитесь?" class="w-full p-3 rounded bg-slate-700 mb-4" />
        <div class="flex gap-3">
          <button @click="showSos = false" class="flex-1 py-2 bg-slate-600 rounded">Отмена</button>
          <button @click="sendSos" class="flex-1 py-2 bg-emergency rounded font-bold">Отправить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import L from 'leaflet';
import { useAuthStore } from '../stores/auth';
import { vesselsApi, notificationsApi, emergencyApi } from '../services/api';

const auth = useAuthStore();
const tab = ref('map');
const vessel = ref(null);
const route = ref(null);
const notifications = ref([]);
const emergencies = ref([]);
const mapEl = ref(null);
const showSos = ref(false);
const sosLocation = ref('');
let map = null;
let marker = null;
let ws = null;

const vesselId = computed(() => auth.user?.vessel_id || 1);

const tabs = computed(() => [
  { id: 'map', label: 'Карта' },
  { id: 'notifications', label: 'Уведомления' },
  ...(auth.isCrew ? [{ id: 'crew', label: 'SOS панель' }] : []),
]);

async function loadData() {
  const [v, r, n] = await Promise.all([
    vesselsApi.get(vesselId.value),
    vesselsApi.route(vesselId.value),
    notificationsApi.list(),
  ]);
  vessel.value = v.data;
  route.value = r.data;
  notifications.value = n.data;
  if (auth.isCrew) {
    const e = await emergencyApi.list();
    emergencies.value = e.data;
  }
  updateMap();
}

function updateMap() {
  if (!mapEl.value || !vessel.value) return;
  if (!map) {
    map = L.map(mapEl.value).setView([vessel.value.latitude, vessel.value.longitude], 10);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
  }
  map.invalidateSize();
  if (marker) marker.setLatLng([vessel.value.latitude, vessel.value.longitude]);
  else marker = L.marker([vessel.value.latitude, vessel.value.longitude]).addTo(map);
  map.setView([vessel.value.latitude, vessel.value.longitude], 10);
}

const statusLabels = { moving: 'В движении', docked: 'На стоянке', mooring: 'Швартовка' };
const typeLabels = { passenger_liner: 'Пассажирский лайнер', cruise_ship: 'Круизное судно', fast_ferry: 'Скоростной паром' };

function statusLabel(s) { return statusLabels[s] || s; }
function typeLabel(t) { return typeLabels[t] || t; }
function weatherText(v) {
  const w = v.weather_info || {};
  return `${w.air_temp ?? '—'}°C / вода ${w.water_temp ?? '—'}°C • ${w.conditions ?? '—'}`;
}
function engineText(v) {
  const e = v.technical_info?.engines || {};
  return `Гл.: ${e.main || '—'}, Всп.: ${e.aux || '—'}`;
}
function loadPercent(v) {
  return v.capacity ? Math.round((v.passenger_count / v.capacity) * 100) : 0;
}

async function markRead(id) {
  await notificationsApi.markRead(id);
  loadData();
}

async function sendSos() {
  await emergencyApi.create({ location: sosLocation.value || 'Текущее местоположение' });
  showSos.value = false;
  sosLocation.value = '';
}

async function updateSos(id, status) {
  await emergencyApi.updateStatus(id, { status });
  loadData();
}

onMounted(() => {
  loadData();
  const token = localStorage.getItem('access_token');
  ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/vessels/${vesselId.value}?token=${token}`);
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.type === 'telemetry_update' && vessel.value) {
      vessel.value = { ...vessel.value, ...msg.data, current_speed: msg.data.speed };
      updateMap();
    }
  };
});

onUnmounted(() => ws?.close());

watch(vesselId, loadData);

watch(tab, () => {
  if (tab.value === 'map') setTimeout(updateMap, 100);
});
</script>
