import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api, AppData } from '../lib/api';
import { motion } from 'motion/react';
import { Trophy, AlertTriangle } from 'lucide-react';

export function Ranking() {
  const { role } = useAuth();
  const [data, setData] = useState<AppData | null>(null);
  const [password, setPassword] = useState('');

  const isDiretoria = role === 'Diretoria';

  const loadData = () => {
    api.getData().then(setData).catch(console.error);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleClear = async () => {
    const correctPassword = import.meta.env.VITE_DIRETORIA_PASSWORD || 'admin123';
    if (password !== correctPassword) {
      alert('Senha incorreta.');
      return;
    }

    if (!window.confirm('Esta ação apagará permanentemente TODAS as estatísticas de TODAS as partidas salvas. Esta ação é irreversível.')) return;

    try {
      await api.clearStats();
      alert('O histórico do ranking foi limpo com sucesso!');
      setPassword('');
      loadData();
    } catch (error) {
      console.error(error);
      alert('Erro ao limpar o ranking');
    }
  };

  if (!data) return null;

  const stats = data.game_stats || [];

  const rankingMap = new Map<string, any>();
  stats.forEach(stat => {
    if (!rankingMap.has(stat.player_name)) {
      rankingMap.set(stat.player_name, {
        name: stat.player_name,
        goals: 0,
        yellow_cards: 0,
        red_cards: 0,
        craque: 0,
        goleiro: 0,
        gol: 0
      });
    }
    const p = rankingMap.get(stat.player_name);
    p.goals += stat.goals;
    p.yellow_cards += stat.yellow_cards;
    p.red_cards += stat.red_cards;
    if (stat.craque_do_jogo) p.craque += 1;
    if (stat.goleiro_do_jogo) p.goleiro += 1;
    if (stat.gol_do_jogo) p.gol += 1;
  });

  const ranking = Array.from(rankingMap.values());

  const artilharia = [...ranking].filter(p => p.goals > 0).sort((a, b) => b.goals - a.goals);
  const amarelos = [...ranking].filter(p => p.yellow_cards > 0).sort((a, b) => b.yellow_cards - a.yellow_cards);
  const vermelhos = [...ranking].filter(p => p.red_cards > 0).sort((a, b) => b.red_cards - a.red_cards);
  const premios = [...ranking].filter(p => p.craque > 0 || p.goleiro > 0 || p.gol > 0).sort((a, b) => b.craque - a.craque);

  const Table = ({ title, data, columns }: any) => (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
      <div className="p-4 border-b border-zinc-800 bg-zinc-950">
        <h3 className="font-bold text-lg flex items-center gap-2">{title}</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-zinc-900 text-zinc-400 uppercase tracking-wider text-xs border-b border-zinc-800">
            <tr>
              <th className="px-4 py-3 font-medium w-12 text-center">#</th>
              <th className="px-4 py-3 font-medium">Jogador</th>
              {columns.map((col: any, i: number) => (
                <th key={i} className="px-4 py-3 font-medium text-center">{col.label}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {data.length === 0 ? (
              <tr>
                <td colSpan={columns.length + 2} className="px-4 py-6 text-center text-zinc-500">
                  Nenhum registro.
                </td>
              </tr>
            ) : (
              data.map((row: any, i: number) => (
                <tr key={i} className="hover:bg-zinc-800/50 transition-colors">
                  <td className="px-4 py-3 text-center text-zinc-500 font-medium">{i + 1}</td>
                  <td className="px-4 py-3 font-medium text-white">{row.name}</td>
                  {columns.map((col: any, j: number) => (
                    <td key={j} className="px-4 py-3 text-center text-zinc-300 font-bold">{row[col.key]}</td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Trophy className="text-yellow-500" size={32} />
          Ranking Geral de Atletas
        </h1>
      </div>

      <div className="bg-indigo-900/20 border border-indigo-700/50 text-indigo-300 p-4 rounded-lg">
        As estatísticas são atualizadas sempre que uma nova súmula é salva.
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Table 
          title="⚽ Artilharia" 
          data={artilharia} 
          columns={[{ label: 'Gols', key: 'goals' }]} 
        />
        <Table 
          title="🟨 Cartões Amarelos" 
          data={amarelos} 
          columns={[{ label: 'Amarelos', key: 'yellow_cards' }]} 
        />
        <Table 
          title="🟥 Cartões Vermelhos" 
          data={vermelhos} 
          columns={[{ label: 'Vermelhos', key: 'red_cards' }]} 
        />
        <Table 
          title="⭐ Prêmios Individuais" 
          data={premios} 
          columns={[
            { label: 'Craque', key: 'craque' },
            { label: 'Goleiro', key: 'goleiro' },
            { label: 'Gol do Jogo', key: 'gol' }
          ]} 
        />
      </div>

      {isDiretoria && (
        <div className="mt-12 bg-red-900/10 border border-red-900/50 rounded-xl p-6">
          <h2 className="text-xl font-bold text-red-500 flex items-center gap-2 mb-4">
            <AlertTriangle size={24} />
            Área Restrita - Limpar Histórico
          </h2>
          <p className="text-zinc-400 mb-4 text-sm">
            Esta ação apagará permanentemente TODAS as estatísticas de TODAS as partidas salvas. Esta ação é irreversível.
          </p>
          <div className="flex gap-4 max-w-md">
            <input 
              type="password" 
              placeholder="Senha da Diretoria" 
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="flex-1 bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 focus:outline-none focus:border-red-500"
            />
            <button 
              onClick={handleClear}
              disabled={!password}
              className="bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white px-6 py-2 rounded-lg transition-colors font-medium"
            >
              Limpar Ranking
            </button>
          </div>
        </div>
      )}
    </motion.div>
  );
}
