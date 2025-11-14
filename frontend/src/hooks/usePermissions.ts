import { useAuth } from '../contexts/AuthContext';
import { UserRole } from '../types/index';

export function usePermissions() {
  const { user } = useAuth();

  // Verificar si el usuario es admin
  const isAdmin = user?.role === UserRole.ADMIN;

  // Verificar si el usuario es owner
  const isOwner = user?.role === UserRole.OWNER;

  // Verificar si el usuario es editor
  const isEditor = user?.role === UserRole.EDITOR;

  // Verificar si el usuario es viewer
  const isViewer = user?.role === UserRole.VIEWER;

  // Permisos para crear/editar/eliminar bots
  const canCreateBots = isAdmin || isOwner;
  const canEditBots = isAdmin || isOwner || isEditor;
  const canDeleteBots = isAdmin || isOwner;

  // Permisos para gestionar documentos
  const canUploadDocuments = isAdmin || isOwner || isEditor;
  const canDeleteDocuments = isAdmin || isOwner || isEditor;

  // Permisos para gestionar usuarios
  const canManageUsers = isAdmin || isOwner;
  const canCreateUsers = isAdmin || isOwner;
  const canEditUsers = isAdmin || isOwner;
  const canDeleteUsers = isAdmin; // Solo admin puede eliminar

  // Permisos para analytics
  const canViewGlobalAnalytics = isAdmin;
  const canViewBotAnalytics = true; // Todos pueden ver analytics de sus bots

  // Verificar si el usuario tiene acceso a un bot específico
  const canAccessBot = (botId: string): boolean => {
    if (isAdmin) return true; // Admin tiene acceso a todo

    // Si allowed_bots es null, tiene acceso a todos los bots
    if (!user?.allowed_bots) return true;

    // Verificar si el bot está en la lista de allowed_bots
    return user.allowed_bots.includes(botId);
  };

  // Verificar si puede realizar una acción en un bot específico
  const canEditBot = (botId: string): boolean => {
    return canEditBots && canAccessBot(botId);
  };

  const canDeleteBot = (botId: string): boolean => {
    return canDeleteBots && canAccessBot(botId);
  };

  return {
    // Roles
    isAdmin,
    isOwner,
    isEditor,
    isViewer,

    // Permisos de bots
    canCreateBots,
    canEditBots,
    canDeleteBots,
    canEditBot,
    canDeleteBot,

    // Permisos de documentos
    canUploadDocuments,
    canDeleteDocuments,

    // Permisos de usuarios
    canManageUsers,
    canCreateUsers,
    canEditUsers,
    canDeleteUsers,

    // Permisos de analytics
    canViewGlobalAnalytics,
    canViewBotAnalytics,

    // Verificación de acceso
    canAccessBot,

    // Usuario actual
    user,
  };
}
