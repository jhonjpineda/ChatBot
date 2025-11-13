import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '../services/analytics.service';
import { botsService } from '../services/bots.service';
import type { BotAnalytics } from '../types';

export default function Analytics() {
  const [selectedBotId, setSelectedBotId] = useState<string>('');
  const [timeRange, setTimeRange] = useState<number>(7); // days

  // Fetch bots for selector
  const { data: botsData } = useQuery({
    queryKey: ['bots'],
    queryFn: () => botsService.list(),
  });

  const bots = botsData?.bots || [];

  // Fetch analytics data
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics', selectedBotId || 'global', timeRange],
    queryFn: () =>
      selectedBotId
        ? analyticsService.getBotAnalytics(selectedBotId)
        : analyticsService.getGlobalAnalytics(),
  });

  // Fetch popular questions
  const { data: popularQuestions = [] } = useQuery({
    queryKey: ['popular-questions', selectedBotId],
    queryFn: () => analyticsService.getPopularQuestions(selectedBotId || undefined, 10),
  });

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('es-ES').format(num);
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 90) return 'text-green-600';
    if (rate >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSuccessRateBg = (rate: number) => {
    if (rate >= 90) return 'bg-green-50';
    if (rate >= 70) return 'bg-yellow-50';
    return 'bg-red-50';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="mt-2 text-gray-600">
            Visualiza el rendimiento y estadísticas de tus bots
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Bot Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Seleccionar Bot
            </label>
            <select
              value={selectedBotId}
              onChange={(e) => setSelectedBotId(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Todos los bots (Global)</option>
              {bots.map((bot) => (
                <option key={bot.bot_id} value={bot.bot_id}>
                  {bot.name} ({bot.bot_id})
                </option>
              ))}
            </select>
          </div>

          {/* Time Range - Optional for future implementation */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Rango de Tiempo
            </label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              disabled
            >
              <option value={7}>Últimos 7 días</option>
              <option value={30}>Últimos 30 días</option>
              <option value={90}>Últimos 90 días</option>
            </select>
            <p className="mt-1 text-xs text-gray-500">
              (Filtro de tiempo próximamente)
            </p>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          Cargando analytics...
        </div>
      ) : !analytics ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No hay datos de analytics disponibles
        </div>
      ) : (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Total Interactions */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Total Interacciones
                  </p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {formatNumber(analytics.total_interactions)}
                  </p>
                </div>
                <div className="text-4xl">💬</div>
              </div>
            </div>

            {/* Success Rate */}
            <div className={`rounded-lg shadow p-6 ${getSuccessRateBg(analytics.success_rate)}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Tasa de Éxito
                  </p>
                  <p className={`text-3xl font-bold mt-2 ${getSuccessRateColor(analytics.success_rate)}`}>
                    {analytics.success_rate.toFixed(1)}%
                  </p>
                </div>
                <div className="text-4xl">
                  {analytics.success_rate >= 90 ? '✅' : analytics.success_rate >= 70 ? '⚠️' : '❌'}
                </div>
              </div>
            </div>

            {/* Avg Response Time */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Tiempo Promedio
                  </p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {formatDuration(analytics.avg_response_time_ms)}
                  </p>
                </div>
                <div className="text-4xl">⚡</div>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                Min: {formatDuration(analytics.min_response_time_ms)} |
                Max: {formatDuration(analytics.max_response_time_ms)}
              </div>
            </div>

            {/* Total Errors */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Total Errores
                  </p>
                  <p className="text-3xl font-bold text-red-600 mt-2">
                    {formatNumber(analytics.total_errors)}
                  </p>
                </div>
                <div className="text-4xl">🚨</div>
              </div>
            </div>
          </div>

          {/* Daily Breakdown */}
          {analytics.daily_breakdown && analytics.daily_breakdown.length > 0 && (
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  Desglose Diario
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Fecha
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Interacciones
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Éxitos
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Errores
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tasa Éxito
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tiempo Prom.
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {analytics.daily_breakdown.map((day: any) => {
                      const successRate = day.count > 0
                        ? ((day.count - day.errors) / day.count) * 100
                        : 0;
                      return (
                        <tr key={day.date} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {new Date(day.date).toLocaleDateString('es-ES', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                            })}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatNumber(day.count)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                            {formatNumber(day.count - day.errors)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                            {formatNumber(day.errors)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <span className={getSuccessRateColor(successRate)}>
                              {successRate.toFixed(1)}%
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatDuration(day.avg_response_time)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Popular Questions */}
          {popularQuestions.length > 0 && (
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  Preguntas Más Frecuentes
                  <span className="ml-2 text-sm font-normal text-gray-500">
                    (Top 10)
                  </span>
                </h2>
              </div>
              <div className="divide-y divide-gray-200">
                {popularQuestions.map((item: any, index: number) => (
                  <div key={index} className="p-6 hover:bg-gray-50">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center font-semibold">
                        {index + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900">
                          {item.question}
                        </p>
                        <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                          <span>🔢 {formatNumber(item.count)} veces</span>
                          {item.bot_id && (
                            <span>🤖 Bot: {item.bot_id}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
