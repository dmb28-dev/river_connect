import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Anchor } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export default function LoginPage() {
  const [email, setEmail] = useState('passenger1@test.com');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка входа');
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = (em, pw) => {
    setEmail(em);
    setPassword(pw);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-slate-900 to-blue-950">
      <div className="w-full max-w-md bg-slate-800/80 backdrop-blur rounded-2xl p-8 shadow-xl">
        <div className="text-center mb-8">
          <Anchor className="mx-auto text-primary mb-2" size={48} />
          <h1 className="text-2xl font-bold">River Connect</h1>
          <p className="text-slate-400 text-sm">Система связи для речных судов</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            className="w-full p-3 rounded-lg bg-slate-700 border border-slate-600 focus:border-primary outline-none"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Пароль"
            className="w-full p-3 rounded-lg bg-slate-700 border border-slate-600 focus:border-primary outline-none"
            required
          />
          {error && <p className="text-emergency text-sm">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-primary rounded-lg font-semibold hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-slate-700">
          <p className="text-xs text-slate-500 mb-2">Тестовые аккаунты:</p>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => quickLogin('passenger1@test.com', 'password123')} className="text-xs px-2 py-1 bg-slate-700 rounded">Пассажир</button>
            <button type="button" onClick={() => quickLogin('captain@ship.com', 'captain123')} className="text-xs px-2 py-1 bg-slate-700 rounded">Капитан</button>
          </div>
        </div>
      </div>
    </div>
  );
}
