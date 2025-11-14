import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { botsService } from '../services/bots.service';
import { usePermissions } from '../hooks/usePermissions';
import type { Bot, BotCreate } from '../types/index';

export default function Bots() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingBot, setEditingBot] = useState<Bot | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const { canCreateBots, canEditBot, canDeleteBot } = usePermissions();

  const { data, isLoading } = useQuery({
    queryKey: ['bots'],
    queryFn: () => botsService.list(),
  });

  const { data: presets } = useQuery({
    queryKey: ['presets'],
    queryFn: () => botsService.getPresets(),
  });

  const createMutation = useMutation({
    mutationFn: botsService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bots'] });
      setShowCreateModal(false);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ botId, data }: { botId: string; data: any }) =>
      botsService.update(botId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bots'] });
      setEditingBot(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: botsService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bots'] });
      setShowDeleteConfirm(null);
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Bots</h1>
          <p className="mt-2 text-gray-600">
            Crea y configura tus chatbots con IA
          </p>
        </div>
        {canCreateBots && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
          >
            + Crear Bot
          </button>
        )}
      </div>

      {/* Bots Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {data?.bots.map((bot) => (
          <div
            key={bot.bot_id}
            className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {bot.name}
                  </h3>
                  <div
                    className={`w-2 h-2 rounded-full ${
                      bot.active ? 'bg-green-500' : 'bg-gray-300'
                    }`}
                  />
                </div>
                <p className="mt-1 text-sm text-gray-500">{bot.bot_id}</p>
                <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                  {bot.description || 'Sin descripción'}
                </p>
              </div>
            </div>

            <div className="mt-4 flex items-center space-x-4 text-xs text-gray-500">
              <span>Temp: {bot.temperature}</span>
              <span>K: {bot.retrieval_k}</span>
            </div>

            <div className="mt-4 flex items-center space-x-2">
              {canEditBot(bot.bot_id) && (
                <button
                  onClick={() => setEditingBot(bot)}
                  className="flex-1 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Editar
                </button>
              )}
              {canDeleteBot(bot.bot_id) && (
                <button
                  onClick={() => setShowDeleteConfirm(bot.bot_id)}
                  disabled={bot.bot_id === 'default'}
                  className="flex-1 px-3 py-2 text-sm bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Eliminar
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <CreateBotModal
          presets={presets}
          onClose={() => setShowCreateModal(false)}
          onSubmit={(data) => createMutation.mutate(data)}
          isLoading={createMutation.isPending}
        />
      )}

      {/* Edit Modal */}
      {editingBot && (
        <EditBotModal
          bot={editingBot}
          presets={presets}
          onClose={() => setEditingBot(null)}
          onSubmit={(data) =>
            updateMutation.mutate({ botId: editingBot.bot_id, data })
          }
          isLoading={updateMutation.isPending}
        />
      )}

      {/* Delete Confirm */}
      {showDeleteConfirm && (
        <DeleteConfirmModal
          botId={showDeleteConfirm}
          onClose={() => setShowDeleteConfirm(null)}
          onConfirm={() => deleteMutation.mutate(showDeleteConfirm)}
          isLoading={deleteMutation.isPending}
        />
      )}
    </div>
  );
}

// Create Bot Modal
function CreateBotModal({
  presets,
  onClose,
  onSubmit,
  isLoading,
}: {
  presets: any;
  onClose: () => void;
  onSubmit: (data: BotCreate) => void;
  isLoading: boolean;
}) {
  const [formData, setFormData] = useState<BotCreate>({
    bot_id: '',
    name: '',
    description: '',
    system_prompt: '',
    temperature: 0.7,
    retrieval_k: 4,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Crear Nuevo Bot</h2>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              ID del Bot *
            </label>
            <input
              type="text"
              required
              value={formData.bot_id}
              onChange={(e) =>
                setFormData({ ...formData, bot_id: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="mi-bot-soporte"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Bot de Soporte"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descripción
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Bot para atención al cliente..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Prompt del Sistema
            </label>
            <select
              onChange={(e) => {
                const preset = presets?.presets[e.target.value];
                if (preset) {
                  setFormData({ ...formData, system_prompt: preset });
                }
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent mb-2"
            >
              <option value="">Seleccionar preset...</option>
              {presets?.available.map((key: string) => (
                <option key={key} value={key}>
                  {key}
                </option>
              ))}
            </select>
            <textarea
              value={formData.system_prompt}
              onChange={(e) =>
                setFormData({ ...formData, system_prompt: e.target.value })
              }
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Eres un asistente útil que..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Temperatura
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="2"
                value={formData.temperature}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    temperature: parseFloat(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Retrieval K
              </label>
              <input
                type="number"
                min="1"
                max="20"
                value={formData.retrieval_k}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    retrieval_k: parseInt(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="flex items-center space-x-3 pt-4">
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Creando...' : 'Crear Bot'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Edit Bot Modal (similar structure)
function EditBotModal({
  bot,
  presets,
  onClose,
  onSubmit,
  isLoading,
}: {
  bot: Bot;
  presets: any;
  onClose: () => void;
  onSubmit: (data: any) => void;
  isLoading: boolean;
}) {
  const [formData, setFormData] = useState({
    name: bot.name,
    description: bot.description || '',
    system_prompt: bot.system_prompt,
    temperature: bot.temperature,
    retrieval_k: bot.retrieval_k,
    active: bot.active,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Editar Bot</h2>
          <p className="text-sm text-gray-500 mt-1">{bot.bot_id}</p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descripción
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Prompt del Sistema
            </label>
            <select
              onChange={(e) => {
                const preset = presets?.presets[e.target.value];
                if (preset) {
                  setFormData({ ...formData, system_prompt: preset });
                }
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent mb-2"
            >
              <option value="">Seleccionar preset...</option>
              {presets?.available.map((key: string) => (
                <option key={key} value={key}>
                  {key}
                </option>
              ))}
            </select>
            <textarea
              value={formData.system_prompt}
              onChange={(e) =>
                setFormData({ ...formData, system_prompt: e.target.value })
              }
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Temperatura
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="2"
                value={formData.temperature}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    temperature: parseFloat(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Retrieval K
              </label>
              <input
                type="number"
                min="1"
                max="20"
                value={formData.retrieval_k}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    retrieval_k: parseInt(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="active"
              checked={formData.active}
              onChange={(e) =>
                setFormData({ ...formData, active: e.target.checked })
              }
              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <label htmlFor="active" className="ml-2 text-sm text-gray-700">
              Bot activo
            </label>
          </div>

          <div className="flex items-center space-x-3 pt-4">
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Guardando...' : 'Guardar Cambios'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Delete Confirm Modal
function DeleteConfirmModal({
  botId,
  onClose,
  onConfirm,
  isLoading,
}: {
  botId: string;
  onClose: () => void;
  onConfirm: () => void;
  isLoading: boolean;
}) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-2">
          ¿Eliminar bot?
        </h3>
        <p className="text-sm text-gray-600 mb-6">
          Esta acción no se puede deshacer. El bot <strong>{botId}</strong> será
          eliminado permanentemente.
        </p>

        <div className="flex items-center space-x-3">
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Eliminando...' : 'Eliminar'}
          </button>
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
}
