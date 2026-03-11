import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Home, Users, DollarSign, FileText, Dices, Trophy, LogOut, Key } from 'lucide-react';
import clsx from 'clsx';

export function Sidebar() {
  const { role, loginAsDiretoria, logout } = useAuth();
  const location = useLocation();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const isDiretoria = role === 'Diretoria';

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (loginAsDiretoria(password)) {
      setPassword('');
      setError('');
    } else {
      setError('Senha incorreta.');
    }
  };

  const navItems = [
    { path: '/', label: 'Página Principal', icon: Home },
    { path: '/players', label: 'Gerenciar Jogadores', icon: Users },
    ...(isDiretoria ? [{ path: '/payments', label: 'Mensalidades', icon: DollarSign }] : []),
    { path: '/summary', label: 'Nova Súmula', icon: FileText },
    { path: '/draw', label: 'Sorteio de Times', icon: Dices },
    { path: '/ranking', label: 'Ranking', icon: Trophy },
  ];

  return (
    <aside className="w-72 bg-zinc-900 text-zinc-100 flex flex-col h-screen fixed left-0 top-0 border-r border-zinc-800">
      <div className="p-6 flex flex-col items-center border-b border-zinc-800">
        <img 
          src="https://raw.githubusercontent.com/gabrielxrm-lab/sjfc-streamlit-app/main/logo_sao_jorge.png" 
          alt="Logo SJFC" 
          className="w-24 h-24 object-contain mb-4"
          onError={(e) => {
            (e.target as HTMLImageElement).src = 'https://via.placeholder.com/150?text=SJFC';
          }}
        />
        <h1 className="text-xl font-bold text-center">São Jorge FC</h1>
      </div>

      <div className="p-4 border-b border-zinc-800">
        <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-4">Perfil de Acesso</h2>
        
        {isDiretoria ? (
          <div className="bg-emerald-900/30 border border-emerald-800/50 rounded-lg p-4">
            <p className="text-emerald-400 text-sm font-medium mb-3">Logado como Diretoria</p>
            <button 
              onClick={logout}
              className="w-full flex items-center justify-center gap-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 py-2 rounded-md transition-colors text-sm"
            >
              <LogOut size={16} />
              Sair do modo Edição
            </button>
          </div>
        ) : (
          <div className="bg-zinc-800/50 rounded-lg p-4">
            <p className="text-zinc-300 text-sm mb-3">Modo Jogador (Visualização)</p>
            <form onSubmit={handleLogin} className="space-y-2">
              <input 
                type="password" 
                placeholder="Senha da Diretoria" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
              />
              {error && <p className="text-red-400 text-xs">{error}</p>}
              <button 
                type="submit"
                className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-md transition-colors text-sm"
              >
                <Key size={16} />
                Entrar como Diretoria
              </button>
            </form>
          </div>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <li key={item.path}>
                <Link 
                  to={item.path}
                  className={clsx(
                    "flex items-center gap-3 px-3 py-2.5 rounded-md transition-colors text-sm font-medium",
                    isActive 
                      ? "bg-indigo-600/10 text-indigo-400" 
                      : "text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100"
                  )}
                >
                  <Icon size={18} />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="p-4 border-t border-zinc-800 text-xs text-zinc-500 text-center">
        <p>Desenvolvido por:</p>
        <p className="font-semibold text-zinc-400 mt-1">Gabriel Conrado</p>
        <p>📱 (21) 97275-7256</p>
      </div>
    </aside>
  );
}
