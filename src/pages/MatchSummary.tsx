import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api, GameStat } from '../lib/api';
import { motion } from 'motion/react';
import { Save, Trash2, Download } from 'lucide-react';

export function MatchSummary() {
  const { role } = useAuth();
  const isDiretoria = role === 'Diretoria';

  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [round, setRound] = useState('');
  const [homeName, setHomeName] = useState('SÃO JORGE');
  const [awayName, setAwayName] = useState('ADVERSÁRIO');

  const [craques, setCraques] = useState<string[]>([]);
  const [goleiros, setGoleiros] = useState<string[]>([]);
  const [golsJogo, setGolsJogo] = useState<string[]>([]);

  const [homeGoals, setHomeGoals] = useState<{name: string, shirt: number, qty: number}[]>([]);
  const [awayGoals, setAwayGoals] = useState<{name: string, shirt: number, qty: number}[]>([]);

  const [homeYellow, setHomeYellow] = useState<string[]>([]);
  const [homeRed, setHomeRed] = useState<string[]>([]);
  const [awayYellow, setAwayYellow] = useState<string[]>([]);
  const [awayRed, setAwayRed] = useState<string[]>([]);

  const [suspensos, setSuspensos] = useState<string[]>([]);
  const [faltasNao, setFaltasNao] = useState<string[]>([]);
  const [cumpriu, setCumpriu] = useState<string[]>([]);
  const [faltasSim, setFaltasSim] = useState<string[]>([]);
  const [medico, setMedico] = useState<string[]>([]);
  const [cartoesMes, setCartoesMes] = useState<string[]>([]);

  const handleAddList = (setter: React.Dispatch<React.SetStateAction<string[]>>, val: string) => {
    if (val) setter(prev => [...prev, val]);
  };

  const handleRemoveList = (setter: React.Dispatch<React.SetStateAction<string[]>>, index: number) => {
    setter(prev => prev.filter((_, i) => i !== index));
  };

  const clearAll = () => {
    if (!window.confirm('Tem certeza que deseja limpar todos os campos?')) return;
    setCraques([]); setGoleiros([]); setGolsJogo([]);
    setHomeGoals([]); setAwayGoals([]);
    setHomeYellow([]); setHomeRed([]); setAwayYellow([]); setAwayRed([]);
    setSuspensos([]); setFaltasNao([]); setCumpriu([]); setFaltasSim([]); setMedico([]); setCartoesMes([]);
    setRound('');
  };

  const generateText = () => {
    const homeScore = homeGoals.reduce((sum, g) => sum + g.qty, 0);
    const awayScore = awayGoals.reduce((sum, g) => sum + g.qty, 0);
    
    const formatGoals = (goals: {name: string, shirt: number, qty: number}[]) => {
      if (goals.length === 0) return "(Sem gols)";
      return goals.map(g => `${g.name} (${g.shirt}) → ${'⚽'.repeat(g.qty)} (${g.qty})`).join('\n');
    };

    const dateObj = new Date(date);
    const dayOfWeek = dateObj.toLocaleDateString('pt-BR', { weekday: 'long' });
    const dateStr = dateObj.toLocaleDateString('pt-BR');

    return `📋 SÚMULA: ${round}
📅 ${dayOfWeek}, ${dateStr}

🏟 ${homeName} ${homeScore} x ${awayScore} ${awayName}

⚽ GOL(S) DO JOGO → ${golsJogo.join(', ') || '(Não preenchido)'}
🧤 GOLEIRO(S) DO JOGO → ${goleiros.join(', ') || '(Não preenchido)'}
⭐ CRAQUE(S) DO JOGO → ${craques.join(', ') || '(Não preenchido)'}

________________________________________

🔴⚫ Gols do ${homeName}:

${formatGoals(homeGoals)}


🟦⬛ Gols do ${awayName}:

${formatGoals(awayGoals)}
________________________________________


🟨 Cartões Amarelos – ${dateStr}
${[...homeYellow.map(n => `${n} (${homeName})`), ...awayYellow.map(n => `${n} (${awayName})`)].join('\n') || '(Sem cartões amarelos)'}

🟥 Cartões Vermelhos – ${dateStr}
${[...homeRed.map(n => `${n} (${homeName})`), ...awayRed.map(n => `${n} (${awayName})`)].join('\n') || '(Sem cartões vermelhos)'}
________________________________________

📌 Faltas não justificadas:
${faltasNao.join('\n') || '(Nenhum)'}

🚫 Suspensos:
${suspensos.join('\n') || '(Nenhum)'}
________________________________________

✅ Faltas justificadas:
${faltasSim.map(n => `(${n})`).join('\n') || '(Nenhum)'}
________________________________________

🚑 Depto. Médico:
${medico.map(n => `(${n})`).join('\n') || '(Nenhum)'}
________________________________________

📆 Cumpriu suspensão:
${cumpriu.map(n => `${n} (APTO)`).join('\n') || '(Nenhum)'}
________________________________________

🟨 Cartões (Mês):
${cartoesMes.join('\n') || '(Nenhum)'}

🖋 Gerado em: ${new Date().toLocaleString('pt-BR')}`;
  };

  const downloadTxt = () => {
    const element = document.createElement("a");
    const file = new Blob([generateText()], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `sumula_${date}.txt`;
    document.body.appendChild(element);
    element.click();
  };

  const saveStats = async () => {
    if (!isDiretoria) return;
    
    const statsMap = new Map<string, GameStat>();
    
    const getStat = (name: string) => {
      if (!statsMap.has(name)) {
        statsMap.set(name, {
          game_date: date,
          player_name: name,
          goals: 0,
          yellow_cards: 0,
          red_cards: 0,
          craque_do_jogo: false,
          goleiro_do_jogo: false,
          gol_do_jogo: false
        });
      }
      return statsMap.get(name)!;
    };

    homeGoals.forEach(g => getStat(g.name).goals += g.qty);
    awayGoals.forEach(g => getStat(g.name).goals += g.qty);
    
    homeYellow.forEach(n => getStat(n).yellow_cards += 1);
    awayYellow.forEach(n => getStat(n).yellow_cards += 1);
    
    homeRed.forEach(n => getStat(n).red_cards += 1);
    awayRed.forEach(n => getStat(n).red_cards += 1);
    
    craques.forEach(n => getStat(n).craque_do_jogo = true);
    goleiros.forEach(n => getStat(n).goleiro_do_jogo = true);
    golsJogo.forEach(n => getStat(n).gol_do_jogo = true);

    try {
      await api.saveStats(Array.from(statsMap.values()));
      alert('Estatísticas salvas no Ranking com sucesso!');
      clearAll();
    } catch (error) {
      console.error(error);
      alert('Erro ao salvar estatísticas');
    }
  };

  const ListEditor = ({ title, items, setter, placeholder }: any) => {
    const [val, setVal] = useState('');
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
        <h3 className="font-bold mb-4">{title}</h3>
        <div className="flex gap-2 mb-4">
          <input 
            type="text" 
            placeholder={placeholder}
            value={val}
            onChange={e => setVal(e.target.value.toUpperCase())}
            disabled={!isDiretoria}
            className="flex-1 bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
          />
          <button 
            onClick={() => { handleAddList(setter, val); setVal(''); }}
            disabled={!isDiretoria || !val}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-3 py-2 rounded-lg text-sm"
          >
            Add
          </button>
        </div>
        <ul className="space-y-2">
          {items.map((item: string, i: number) => (
            <li key={i} className="flex justify-between items-center text-sm bg-zinc-950 p-2 rounded-lg border border-zinc-800">
              <span>{item}</span>
              {isDiretoria && (
                <button onClick={() => handleRemoveList(setter, i)} className="text-red-400 hover:text-red-300">
                  <Trash2 size={16} />
                </button>
              )}
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <h1 className="text-3xl font-bold">Gerador de Súmula</h1>
        {isDiretoria && (
          <button onClick={clearAll} className="flex items-center gap-2 bg-zinc-800 hover:bg-zinc-700 text-white px-4 py-2 rounded-lg transition-colors">
            <Trash2 size={20} />
            Limpar Campos
          </button>
        )}
      </div>

      {!isDiretoria && (
        <div className="bg-yellow-900/20 border border-yellow-700/50 text-yellow-400 p-4 rounded-lg flex items-center gap-3">
          <span>🔒</span> Apenas a Diretoria pode criar ou editar súmulas.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <label className="block text-sm font-medium text-zinc-400 mb-2">Data</label>
          <input type="date" value={date} onChange={e => setDate(e.target.value)} disabled={!isDiretoria} className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2" />
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <label className="block text-sm font-medium text-zinc-400 mb-2">Rodada</label>
          <input type="text" value={round} onChange={e => setRound(e.target.value)} disabled={!isDiretoria} className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2" />
        </div>
      </div>

      <h2 className="text-2xl font-bold mt-8">🏆 Destaques Individuais</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ListEditor title="⭐ Craque(s) do Jogo" items={craques} setter={setCraques} placeholder="Nome do craque" />
        <ListEditor title="🧤 Goleiro(s) do Jogo" items={goleiros} setter={setGoleiros} placeholder="Nome do goleiro" />
        <ListEditor title="⚽ Gol(s) do Jogo" items={golsJogo} setter={setGolsJogo} placeholder="Nome do autor" />
      </div>

      <h2 className="text-2xl font-bold mt-8">📝 Detalhes dos Times</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Time da Casa */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-6">
          <div className="flex justify-between items-center">
            <input type="text" value={homeName} onChange={e => setHomeName(e.target.value.toUpperCase())} disabled={!isDiretoria} className="bg-transparent text-2xl font-bold text-red-500 focus:outline-none w-1/2" />
            <div className="text-4xl font-black">{homeGoals.reduce((s, g) => s + g.qty, 0)}</div>
          </div>
          
          <div className="space-y-4">
            <h4 className="font-bold border-b border-zinc-800 pb-2">Gols</h4>
            {isDiretoria && (
              <form onSubmit={e => {
                e.preventDefault();
                const fd = new FormData(e.currentTarget);
                const name = fd.get('name') as string;
                const shirt = parseInt(fd.get('shirt') as string);
                const qty = parseInt(fd.get('qty') as string);
                if (name && shirt) {
                  setHomeGoals(prev => {
                    const existing = prev.find(g => g.name === name && g.shirt === shirt);
                    if (existing) return prev.map(g => g === existing ? {...g, qty: g.qty + qty} : g);
                    return [...prev, {name: name.toUpperCase(), shirt, qty}];
                  });
                  (e.target as HTMLFormElement).reset();
                }
              }} className="flex gap-2">
                <input name="name" placeholder="Nome" required className="flex-1 bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm" />
                <input name="shirt" type="number" placeholder="Nº" required className="w-16 bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm" />
                <input name="qty" type="number" defaultValue={1} min={1} required className="w-16 bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm" />
                <button type="submit" className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-2 rounded-lg text-sm">Add</button>
              </form>
            )}
            <ul className="space-y-2">
              {homeGoals.map((g, i) => (
                <li key={i} className="flex justify-between items-center text-sm bg-zinc-950 p-2 rounded-lg border border-zinc-800">
                  <span>⚽ {g.name} ({g.shirt}) - {g.qty} gol(s)</span>
                  {isDiretoria && <button onClick={() => setHomeGoals(prev => prev.filter((_, idx) => idx !== i))} className="text-red-400"><Trash2 size={16} /></button>}
                </li>
              ))}
            </ul>
          </div>

          <div className="space-y-4">
            <h4 className="font-bold border-b border-zinc-800 pb-2">Cartões</h4>
            {isDiretoria && (
              <form onSubmit={e => {
                e.preventDefault();
                const fd = new FormData(e.currentTarget);
                const name = (fd.get('name') as string).toUpperCase();
                const type = fd.get('type') as string;
                if (name) {
                  if (type === 'Y') setHomeYellow(prev => [...prev, name]);
                  else setHomeRed(prev => [...prev, name]);
                  (e.target as HTMLFormElement).reset();
                }
              }} className="flex gap-2">
                <input name="name" placeholder="Nome" required className="flex-1 bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm" />
                <select name="type" className="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm">
                  <option value="Y">🟨 Amarelo</option>
                  <option value="R">🟥 Vermelho</option>
                </select>
                <button type="submit" className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-2 rounded-lg text-sm">Add</button>
              </form>
            )}
            <ul className="space-y-2">
              {homeYellow.map((n, i) => (
                <li key={`y-${i}`} className="flex justify-between items-center text-sm bg-zinc-950 p-2 rounded-lg border border-zinc-800">
                  <span>🟨 {n}</span>
                  {isDiretoria && <button onClick={() => setHomeYellow(prev => prev.filter((_, idx) => idx !== i))} className="text-red-400"><Trash2 size={16} /></button>}
                </li>
              ))}
              {homeRed.map((n, i) => (
                <li key={`r-${i}`} className="flex justify-between items-center text-sm bg-zinc-950 p-2 rounded-lg border border-zinc-800">
                  <span>🟥 {n}</span>
                  {isDiretoria && <button onClick={() => setHomeRed(prev => prev.filter((_, idx) => idx !== i))} className="text-red-400"><Trash2 size={16} /></button>}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Time Visitante */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-6">
          <div className="flex justify-between items-center">
            <input type="text" value={awayName} onChange={e => setAwayName(e.target.value.toUpperCase())} disabled={!isDiretoria} className="bg-transparent text-2xl font-bold text-blue-500 focus:outline-none w-1/2" />
            <div className="text-4xl font-black">{awayGoals.reduce((s, g) => s + g.qty, 0)}</div>
          </div>
          
          <div className="space-y-4">
            <h4 className="font-bold border-b border-zinc-800 pb-2">Gols</h4>
            {isDiretoria && (
              <form onSubmit={e => {
                e.preventDefault();
                const fd = new FormData(e.currentTarget);
                const name = fd.get('name') as string;
                const shirt = parseInt(fd.get('shirt') as string);
                const qty = parseInt(fd.get('qty') as string);
                if (name && shirt) {
                  setAwayGoals(prev => {
                    const existing = prev.find(g => g.name === name && g.shirt === shirt);
                    if (existing) return prev.map(g => g === existing ? {...g, qty: g.qty + qty} : g);
                    return [...prev, {name: name.toUpperCase(), shirt, qty}];
                  });
                  (e.target as HTMLFormElement).reset();
                }
              }} className="flex gap-2">
                <input name="name" placeholder="Nome" required className="flex-1 bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm" />
                <input name="shirt" type="number" placeholder="Nº" required className="w-16 bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm" />
                <input name="qty" type="number" defaultValue={1} min={1} required className="w-16 bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm" />
                <button type="submit" className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-2 rounded-lg text-sm">Add</button>
              </form>
            )}
            <ul className="space-y-2">
              {awayGoals.map((g, i) => (
                <li key={i} className="flex justify-between items-center text-sm bg-zinc-950 p-2 rounded-lg border border-zinc-800">
                  <span>⚽ {g.name} ({g.shirt}) - {g.qty} gol(s)</span>
                  {isDiretoria && <button onClick={() => setAwayGoals(prev => prev.filter((_, idx) => idx !== i))} className="text-red-400"><Trash2 size={16} /></button>}
                </li>
              ))}
            </ul>
          </div>

          <div className="space-y-4">
            <h4 className="font-bold border-b border-zinc-800 pb-2">Cartões</h4>
            {isDiretoria && (
              <form onSubmit={e => {
                e.preventDefault();
                const fd = new FormData(e.currentTarget);
                const name = (fd.get('name') as string).toUpperCase();
                const type = fd.get('type') as string;
                if (name) {
                  if (type === 'Y') setAwayYellow(prev => [...prev, name]);
                  else setAwayRed(prev => [...prev, name]);
                  (e.target as HTMLFormElement).reset();
                }
              }} className="flex gap-2">
                <input name="name" placeholder="Nome" required className="flex-1 bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm" />
                <select name="type" className="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm">
                  <option value="Y">🟨 Amarelo</option>
                  <option value="R">🟥 Vermelho</option>
                </select>
                <button type="submit" className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-2 rounded-lg text-sm">Add</button>
              </form>
            )}
            <ul className="space-y-2">
              {awayYellow.map((n, i) => (
                <li key={`y-${i}`} className="flex justify-between items-center text-sm bg-zinc-950 p-2 rounded-lg border border-zinc-800">
                  <span>🟨 {n}</span>
                  {isDiretoria && <button onClick={() => setAwayYellow(prev => prev.filter((_, idx) => idx !== i))} className="text-red-400"><Trash2 size={16} /></button>}
                </li>
              ))}
              {awayRed.map((n, i) => (
                <li key={`r-${i}`} className="flex justify-between items-center text-sm bg-zinc-950 p-2 rounded-lg border border-zinc-800">
                  <span>🟥 {n}</span>
                  {isDiretoria && <button onClick={() => setAwayRed(prev => prev.filter((_, idx) => idx !== i))} className="text-red-400"><Trash2 size={16} /></button>}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <h2 className="text-2xl font-bold mt-8">📌 Ocorrências Gerais</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ListEditor title="🚫 Suspensos" items={suspensos} setter={setSuspensos} placeholder="Nome do jogador" />
        <ListEditor title="📌 Faltas não justificadas" items={faltasNao} setter={setFaltasNao} placeholder="Nome do jogador" />
        <ListEditor title="📆 Cumpriu Suspensão" items={cumpriu} setter={setCumpriu} placeholder="Nome do jogador" />
        <ListEditor title="✅ Faltas justificadas" items={faltasSim} setter={setFaltasSim} placeholder="Nome (motivo)" />
        <ListEditor title="🚑 Departamento Médico" items={medico} setter={setMedico} placeholder="Nome (lesão)" />
        <ListEditor title="🟨 Cartões (Mês)" items={cartoesMes} setter={setCartoesMes} placeholder="Nome (2 amarelos)" />
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-6">
        <h2 className="text-2xl font-bold">📄 Prévia e Finalização</h2>
        <pre className="bg-zinc-950 border border-zinc-800 p-4 rounded-lg overflow-x-auto text-sm text-zinc-300 whitespace-pre-wrap">
          {generateText()}
        </pre>

        <div className="flex flex-col md:flex-row gap-4">
          <button onClick={downloadTxt} className="flex-1 flex justify-center items-center gap-2 bg-zinc-800 hover:bg-zinc-700 text-white px-6 py-3 rounded-lg transition-colors font-medium">
            <Download size={20} />
            Baixar Súmula (TXT)
          </button>
          {isDiretoria && (
            <button onClick={saveStats} className="flex-1 flex justify-center items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-3 rounded-lg transition-colors font-medium">
              <Save size={20} />
              Salvar no Ranking e Limpar
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
}
