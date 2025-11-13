import { useQuery } from '@tanstack/react-query';
import { botsService } from '../services/bots.service';
import { analyticsService } from '../services/analytics.service';

export default function Dashboard() {
  const { data: botsData, isLoading: botsLoading } = useQuery({
    queryKey: ['bots'],
    queryFn: () => botsService.list(),
  });

  const { data: globalStats, isLoading: statsLoading } = useQuery({
    queryKey: ['globalStats', 7],
    queryFn: () => analyticsService.getGlobalStats(7),
  });

  if (botsLoading || statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const activeBots = botsData?.bots.filter((b) => b.active).length || 0;
  const totalBots = botsData?.total || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Vista general del sistema de chatbots RAG
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Bots Activos</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{activeBots}</p>
              <p className="mt-1 text-xs text-gray-500">de {totalBots} total</p>
            </div>
            <div className="flex items-center justify-center w-12 h-12 bg-primary-100 rounded-lg">
              <span className="text-2xl">🤖</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Interacciones</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {globalStats?.total_interactions || 0}
              </p>
              <p className="mt-1 text-xs text-gray-500">últimos 7 días</p>
            </div>
            <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg">
              <span className="text-2xl">💬</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tasa de Éxito</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {globalStats?.success_rate.toFixed(1) || 0}%
              </p>
              <p className="mt-1 text-xs text-gray-500">promedio</p>
            </div>
            <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg">
              <span className="text-2xl">✓</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tiempo Resp.</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {Math.round(globalStats?.avg_response_time_ms || 0)}
              </p>
              <p className="mt-1 text-xs text-gray-500">ms promedio</p>
            </div>
            <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg">
              <span className="text-2xl">⚡</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bots List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Tus Bots</h2>
        </div>
        <div className="p-6">
          {totalBots === 0 ? (
            <div className="text-center py-12">
              <span className="text-6xl">🤖</span>
              <h3 className="mt-4 text-lg font-medium text-gray-900">
                No hay bots todavía
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Crea tu primer bot para comenzar
              </p>
              <button className="mt-6 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
                Crear Bot
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {botsData?.bots.slice(0, 6).map((bot) => (
                <div
                  key={bot.bot_id}
                  className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{bot.name}</h3>
                      <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                        {bot.description || 'Sin descripción'}
                      </p>
                    </div>
                    <div
                      className={`ml-2 w-2 h-2 rounded-full ${
                        bot.active ? 'bg-green-500' : 'bg-gray-300'
                      }`}
                    />
                  </div>
                  <div className="mt-4 flex items-center space-x-4 text-xs text-gray-500">
                    <span>temp: {bot.temperature}</span>
                    <span>k: {bot.retrieval_k}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <a
          href="/bots"
          className="block p-6 bg-white rounded-lg shadow-sm border border-gray-200 hover:border-primary-300 transition-colors"
        >
          <div className="flex items-center space-x-4">
            <div className="flex items-center justify-center w-12 h-12 bg-primary-100 rounded-lg">
              <span className="text-2xl">🤖</span>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Gestionar Bots</h3>
              <p className="mt-1 text-sm text-gray-500">
                Crear, editar y configurar bots
              </p>
            </div>
          </div>
        </a>

        <a
          href="/documents"
          className="block p-6 bg-white rounded-lg shadow-sm border border-gray-200 hover:border-primary-300 transition-colors"
        >
          <div className="flex items-center space-x-4">
            <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg">
              <span className="text-2xl">📄</span>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Documentos</h3>
              <p className="mt-1 text-sm text-gray-500">
                Subir y gestionar documentos
              </p>
            </div>
          </div>
        </a>

        <a
          href="/analytics"
          className="block p-6 bg-white rounded-lg shadow-sm border border-gray-200 hover:border-primary-300 transition-colors"
        >
          <div className="flex items-center space-x-4">
            <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg">
              <span className="text-2xl">📈</span>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Analytics</h3>
              <p className="mt-1 text-sm text-gray-500">Ver métricas y reportes</p>
            </div>
          </div>
        </a>
      </div>
    </div>
  );
}
