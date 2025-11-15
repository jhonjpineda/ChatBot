/**
 * Página de aprobación de usuarios pendientes
 * Solo accesible para ADMIN y OWNER
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { approvalService, type PendingUser } from '../services/approval.service';

export default function UserApproval() {
  const queryClient = useQueryClient();
  const [selectedUser, setSelectedUser] = useState<PendingUser | null>(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [modalAction, setModalAction] = useState<'approve' | 'reject'>('approve');

  // Query para obtener usuarios pendientes
  const {
    data: pendingUsers = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['pendingUsers'],
    queryFn: () => approvalService.getPendingUsers(),
    refetchInterval: 30000, // Refetch cada 30 segundos
  });

  // Query para contador (se usa en el badge del nav)
  useQuery({
    queryKey: ['pendingCount'],
    queryFn: () => approvalService.getPendingCount(),
    refetchInterval: 30000,
  });

  // Mutation para aprobar
  const approveMutation = useMutation({
    mutationFn: (userId: string) => approvalService.approveUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingUsers'] });
      queryClient.invalidateQueries({ queryKey: ['pendingCount'] });
      queryClient.invalidateQueries({ queryKey: ['users'] }); // Refresh users list
      setShowConfirmModal(false);
      setSelectedUser(null);
    },
  });

  // Mutation para rechazar
  const rejectMutation = useMutation({
    mutationFn: (userId: string) => approvalService.rejectUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingUsers'] });
      queryClient.invalidateQueries({ queryKey: ['pendingCount'] });
      setShowConfirmModal(false);
      setSelectedUser(null);
    },
  });

  const handleApprove = (user: PendingUser) => {
    setSelectedUser(user);
    setModalAction('approve');
    setShowConfirmModal(true);
  };

  const handleReject = (user: PendingUser) => {
    setSelectedUser(user);
    setModalAction('reject');
    setShowConfirmModal(true);
  };

  const handleConfirm = () => {
    if (!selectedUser) return;

    if (modalAction === 'approve') {
      approveMutation.mutate(selectedUser.user_id);
    } else {
      rejectMutation.mutate(selectedUser.user_id);
    }
  };

  const getRoleBadgeColor = (role: string) => {
    const colors: Record<string, string> = {
      admin: 'bg-purple-100 text-purple-800',
      owner: 'bg-blue-100 text-blue-800',
      editor: 'bg-green-100 text-green-800',
      viewer: 'bg-gray-100 text-gray-800',
    };
    return colors[role.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const formatWaitingTime = (hours: number) => {
    if (hours < 1) {
      return `${Math.round(hours * 60)} minutos`;
    } else if (hours < 24) {
      return `${Math.round(hours)} horas`;
    } else {
      const days = Math.floor(hours / 24);
      const remainingHours = Math.round(hours % 24);
      return `${days} día${days > 1 ? 's' : ''} ${remainingHours}h`;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        <p className="font-semibold">Error al cargar usuarios pendientes</p>
        <p className="text-sm">{(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Aprobación de Usuarios
            </h1>
            <p className="text-gray-600 mt-2">
              Revisa y aprueba nuevos usuarios registrados
            </p>
          </div>
          {pendingUsers.length > 0 && (
            <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full font-semibold">
              {pendingUsers.length} pendiente{pendingUsers.length !== 1 && 's'}
            </div>
          )}
        </div>
      </div>

      {/* Empty State */}
      {pendingUsers.length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="mt-2 text-lg font-medium text-gray-900">
            No hay usuarios pendientes
          </h3>
          <p className="mt-1 text-gray-500">
            Todos los usuarios han sido aprobados o rechazados
          </p>
        </div>
      )}

      {/* Users List */}
      {pendingUsers.length > 0 && (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usuario
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rol Solicitado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha de Registro
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tiempo Esperando
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {pendingUsers.map((user) => (
                <tr key={user.user_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {user.username}
                      </div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getRoleBadgeColor(
                        user.role
                      )}`}
                    >
                      {user.role.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(user.created_at).toLocaleDateString('es-ES', {
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`text-sm ${
                        user.hours_waiting > 24
                          ? 'text-red-600 font-semibold'
                          : user.hours_waiting > 12
                          ? 'text-orange-600'
                          : 'text-gray-500'
                      }`}
                    >
                      {formatWaitingTime(user.hours_waiting)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleApprove(user)}
                      disabled={approveMutation.isPending || rejectMutation.isPending}
                      className="text-green-600 hover:text-green-900 mr-4 disabled:opacity-50"
                    >
                      <svg
                        className="w-5 h-5 inline"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      Aprobar
                    </button>
                    <button
                      onClick={() => handleReject(user)}
                      disabled={approveMutation.isPending || rejectMutation.isPending}
                      className="text-red-600 hover:text-red-900 disabled:opacity-50"
                    >
                      <svg
                        className="w-5 h-5 inline"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      Rechazar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Confirmation Modal */}
      {showConfirmModal && selectedUser && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
          <div className="relative bg-white rounded-lg shadow-xl p-8 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {modalAction === 'approve' ? 'Aprobar Usuario' : 'Rechazar Usuario'}
            </h3>
            <p className="text-gray-600 mb-6">
              {modalAction === 'approve' ? (
                <>
                  ¿Estás seguro de aprobar a{' '}
                  <span className="font-semibold">{selectedUser.username}</span> (
                  {selectedUser.email})?
                  <br />
                  <br />
                  El usuario podrá iniciar sesión con rol de{' '}
                  <span className="font-semibold">{selectedUser.role.toUpperCase()}</span>.
                </>
              ) : (
                <>
                  ¿Estás seguro de rechazar a{' '}
                  <span className="font-semibold">{selectedUser.username}</span>?
                  <br />
                  <br />
                  <span className="text-red-600 font-semibold">
                    Esta acción eliminará permanentemente al usuario.
                  </span>
                </>
              )}
            </p>
            <div className="flex gap-4 justify-end">
              <button
                onClick={() => {
                  setShowConfirmModal(false);
                  setSelectedUser(null);
                }}
                disabled={approveMutation.isPending || rejectMutation.isPending}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirm}
                disabled={approveMutation.isPending || rejectMutation.isPending}
                className={`px-4 py-2 rounded-md text-white disabled:opacity-50 ${
                  modalAction === 'approve'
                    ? 'bg-green-600 hover:bg-green-700'
                    : 'bg-red-600 hover:bg-red-700'
                }`}
              >
                {approveMutation.isPending || rejectMutation.isPending
                  ? 'Procesando...'
                  : modalAction === 'approve'
                  ? 'Sí, Aprobar'
                  : 'Sí, Rechazar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
