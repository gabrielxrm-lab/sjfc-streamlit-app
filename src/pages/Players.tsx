import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api, Player, AppData } from '../lib/api';
import { v4 as uuidv4 } from 'uuid';
import { motion } from 'motion/react';
import { Search, Plus, Edit2, Trash2, Save, X } from 'lucide-react';

export function Players() {
  const { role } = useAuth();
  const [data, setData] = useState<AppData | null>(null);
  const [search, setSearch] = useState('');
  const [editingPlayer, setEditingPlayer] = useState<Player | null>(null);
  const [isAdding, setIsAdding] = useState(false);

  const isDiretoria = role === 'Diretoria';

  const loadData = () => {
    api.getData().then(setData).catch(console.error);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingPlayer) return;

    try {
      await api.savePlayer(editingPlayer);
      setEditingPlayer(null);
      setIsAdding(false);
      loadData();
    } catch (error) {
      console.error(error);
      alert('Erro ao salvar jogador');
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Tem certeza que deseja excluir este jogador?')) return;
    try {
      await api.deletePlayer(id);
      loadData();
    } catch (error) {
      console.error(error);
      alert('Erro ao excluir jogador');
    }
  };

  const startAdd = () => {
    setIsAdding(true);
    setEditingPlayer({
      id: uuidv4(),
      name: '',
      position: 'MEIO-CAMPO',
      shirt_number: '',
      date_of_birth: '',
      phone: '',
      photo_file: 'Nenhuma',
      team_start_date: new Date().toLocaleDateString('pt-BR')
    });
  };

  const filteredPlayers = data?.players.filter(p => 
    p.name.toLowerCase().includes(search.toLowerCase())
  ) || [];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <h1 className="text-3xl font-bold">Gerenciamento de Jogadores</h1>
        {isDiretoria && !isAdding && !editingPlayer && (
          <button 
            onClick={startAdd}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus size={20} />
            Novo Jogador
          </button>
        )}
      </div>

      {!isDiretoria && (
        <div className="bg-yellow-900/20 border border-yellow-700/50 text-yellow-400 p-4 rounded-lg flex items-center gap-3">
          <span>🔒</span> Modo de visualização. Para editar, acesse como Diretoria na página principal.
        </div>
      )}

      {(isAdding || editingPlayer) && isDiretoria && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold">{isAdding ? 'Cadastrar Novo Jogador' : 'Editar Jogador'}</h2>
            <button 
              onClick={() => { setEditingPlayer(null); setIsAdding(false); }}
              className="text-zinc-400 hover:text-white"
            >
              <X size={24} />
            </button>
          </div>

          <form onSubmit={handleSave} className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-400">Nome do Jogador</label>
              <input 
                required
                type="text" 
                value={editingPlayer?.name || ''}
                onChange={e => setEditingPlayer(prev => prev ? {...prev, name: e.target.value.toUpperCase()} : null)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500 uppercase"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-400">Posição</label>
              <select 
                value={editingPlayer?.position || 'MEIO-CAMPO'}
                onChange={e => setEditingPlayer(prev => prev ? {...prev, position: e.target.value} : null)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500"
              >
                <option value="GOLEIRO">GOLEIRO</option>
                <option value="ZAGUEIRO">ZAGUEIRO</option>
                <option value="LATERAL">LATERAL</option>
                <option value="MEIO-CAMPO">MEIO-CAMPO</option>
                <option value="ATACANTE">ATACANTE</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-400">Nº da Camisa</label>
              <input 
                type="text" 
                value={editingPlayer?.shirt_number || ''}
                onChange={e => setEditingPlayer(prev => prev ? {...prev, shirt_number: e.target.value} : null)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-400">Data Nasc. (DD/MM/AAAA)</label>
              <input 
                type="text" 
                placeholder="DD/MM/AAAA"
                value={editingPlayer?.date_of_birth || ''}
                onChange={e => setEditingPlayer(prev => prev ? {...prev, date_of_birth: e.target.value} : null)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-400">Telefone</label>
              <input 
                type="text" 
                value={editingPlayer?.phone || ''}
                onChange={e => setEditingPlayer(prev => prev ? {...prev, phone: e.target.value} : null)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-400">Foto (Nome do arquivo no GitHub)</label>
              <input 
                type="text" 
                placeholder="Ex: joao.jpg ou Nenhuma"
                value={editingPlayer?.photo_file || 'Nenhuma'}
                onChange={e => setEditingPlayer(prev => prev ? {...prev, photo_file: e.target.value} : null)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="md:col-span-2 flex justify-end gap-4 mt-4">
              <button 
                type="button"
                onClick={() => { setEditingPlayer(null); setIsAdding(false); }}
                className="px-6 py-2 rounded-lg border border-zinc-700 hover:bg-zinc-800 transition-colors"
              >
                Cancelar
              </button>
              <button 
                type="submit"
                className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg transition-colors"
              >
                <Save size={20} />
                Salvar Jogador
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-zinc-800 flex items-center gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={20} />
            <input 
              type="text" 
              placeholder="Buscar jogador..." 
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg pl-10 pr-4 py-2 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-zinc-950 text-zinc-400 uppercase tracking-wider text-xs">
              <tr>
                <th className="px-6 py-4 font-medium">Nome</th>
                <th className="px-6 py-4 font-medium">Posição</th>
                <th className="px-6 py-4 font-medium">Camisa</th>
                <th className="px-6 py-4 font-medium">Idade/Nasc.</th>
                {isDiretoria && <th className="px-6 py-4 font-medium text-right">Ações</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {filteredPlayers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-zinc-500">
                    Nenhum jogador encontrado.
                  </td>
                </tr>
              ) : (
                filteredPlayers.map(player => (
                  <tr key={player.id} className="hover:bg-zinc-800/50 transition-colors">
                    <td className="px-6 py-4 font-medium text-white flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-zinc-800 overflow-hidden flex-shrink-0">
                        <img 
                          src={player.photo_file && player.photo_file !== 'Nenhuma' 
                            ? `https://raw.githubusercontent.com/gabrielxrm-lab/sjfc-streamlit-app/main/player_photos/${player.photo_file}`
                            : 'https://via.placeholder.com/100x100.png?text=SJFC'}
                          alt={player.name}
                          className="w-full h-full object-cover"
                          onError={(e) => { (e.target as HTMLImageElement).src = 'https://via.placeholder.com/100x100.png?text=SJFC'; }}
                        />
                      </div>
                      {player.name}
                    </td>
                    <td className="px-6 py-4 text-zinc-400">{player.position}</td>
                    <td className="px-6 py-4 text-zinc-400">{player.shirt_number || '-'}</td>
                    <td className="px-6 py-4 text-zinc-400">{player.date_of_birth || '-'}</td>
                    {isDiretoria && (
                      <td className="px-6 py-4 text-right space-x-2">
                        <button 
                          onClick={() => { setEditingPlayer(player); setIsAdding(false); }}
                          className="p-2 text-zinc-400 hover:text-indigo-400 hover:bg-indigo-400/10 rounded-lg transition-colors"
                          title="Editar"
                        >
                          <Edit2 size={18} />
                        </button>
                        <button 
                          onClick={() => handleDelete(player.id)}
                          className="p-2 text-zinc-400 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors"
                          title="Excluir"
                        >
                          <Trash2 size={18} />
                        </button>
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}
