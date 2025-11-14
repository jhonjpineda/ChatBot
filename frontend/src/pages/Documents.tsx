import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsService } from '../services/documents.service';
import { botsService } from '../services/bots.service';
import { usePermissions } from '../hooks/usePermissions';
import type { Document } from '../types/index';

export default function Documents() {
  const queryClient = useQueryClient();
  const { canUploadDocuments, canDeleteDocuments, canAccessBot } = usePermissions();
  const [selectedBotId, setSelectedBotId] = useState<string>('default');
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{[key: string]: number}>({});
  const [moveModalOpen, setMoveModalOpen] = useState(false);
  const [documentToMove, setDocumentToMove] = useState<Document | null>(null);
  const [targetBotId, setTargetBotId] = useState<string>('');

  // Fetch bots for selector
  const { data: botsData } = useQuery({
    queryKey: ['bots'],
    queryFn: () => botsService.list(true),
  });

  const bots = botsData?.bots || [];

  // Fetch documents for selected bot
  const { data: documents = [], isLoading } = useQuery({
    queryKey: ['documents', selectedBotId],
    queryFn: () => documentsService.list(selectedBotId),
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: ({ file, botId }: { file: File; botId: string }) =>
      documentsService.upload(file, botId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', selectedBotId] });
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (docId: string) => documentsService.delete(docId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', selectedBotId] });
    },
  });

  // Move mutation
  const moveMutation = useMutation({
    mutationFn: ({ docId, newBotId }: { docId: string; newBotId: string }) =>
      documentsService.moveToBot(docId, newBotId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', selectedBotId] });
      queryClient.invalidateQueries({ queryKey: ['documents', targetBotId] });
      setMoveModalOpen(false);
      setDocumentToMove(null);
      setTargetBotId('');
      alert('Documento movido exitosamente');
    },
    onError: (error: any) => {
      console.error('Move error:', error);
      let errorMessage = 'Error al mover el documento';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = `Error: ${error.message}`;
      }
      alert(errorMessage);
    },
  });

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (files: FileList) => {
    Array.from(files).forEach((file) => {
      // Validate file type
      const validTypes = ['.pdf', '.docx', '.txt'];
      const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();

      if (!validTypes.includes(fileExt)) {
        alert(`Tipo de archivo no válido: ${file.name}. Solo se permiten PDF, DOCX y TXT.`);
        return;
      }

      // Upload file
      setUploadProgress(prev => ({ ...prev, [file.name]: 0 }));
      uploadMutation.mutate(
        { file, botId: selectedBotId },
        {
          onSuccess: () => {
            setUploadProgress(prev => {
              const newProgress = { ...prev };
              delete newProgress[file.name];
              return newProgress;
            });
          },
          onError: (error: any) => {
            console.error('Upload error:', error);
            setUploadProgress(prev => {
              const newProgress = { ...prev };
              delete newProgress[file.name];
              return newProgress;
            });

            // Extraer mensaje de error específico
            let errorMessage = `Error al subir ${file.name}`;
            if (error.response?.data?.detail) {
              errorMessage = error.response.data.detail;
            } else if (error.message) {
              errorMessage = `Error: ${error.message}`;
            }

            alert(errorMessage);
          },
        }
      );
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleMoveDocument = (doc: Document) => {
    setDocumentToMove(doc);
    // Set default target bot to first available bot that's not the current one
    const otherBots = bots.filter(b => b.bot_id !== doc.bot_id);
    if (otherBots.length > 0) {
      setTargetBotId(otherBots[0].bot_id);
    }
    setMoveModalOpen(true);
  };

  const confirmMove = () => {
    if (documentToMove && targetBotId) {
      moveMutation.mutate({
        docId: documentToMove.doc_id,
        newBotId: targetBotId,
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Documentos</h1>
          <p className="mt-2 text-gray-600">
            Sube y gestiona los documentos para tus bots
          </p>
        </div>
      </div>

      {/* Bot Selector */}
      <div className="bg-white rounded-lg shadow p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Seleccionar Bot
        </label>
        <select
          value={selectedBotId}
          onChange={(e) => setSelectedBotId(e.target.value)}
          className="w-full md:w-64 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          {bots.map((bot) => (
            <option key={bot.bot_id} value={bot.bot_id}>
              {bot.name} ({bot.bot_id})
            </option>
          ))}
        </select>
      </div>

      {/* Upload Area */}
      {canUploadDocuments ? (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Subir Documentos
          </h2>

          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
          <input
            type="file"
            id="file-upload"
            multiple
            accept=".pdf,.docx,.txt"
            onChange={handleFileInput}
            className="hidden"
          />

          <div className="space-y-3">
            <div className="text-4xl">📄</div>
            <div>
              <label
                htmlFor="file-upload"
                className="cursor-pointer text-primary-600 hover:text-primary-700 font-medium"
              >
                Haz clic para seleccionar
              </label>
              <span className="text-gray-600"> o arrastra archivos aquí</span>
            </div>
            <p className="text-sm text-gray-500">
              Formatos soportados: PDF, DOCX, TXT
            </p>
          </div>
        </div>

        {/* Upload Progress */}
        {Object.keys(uploadProgress).length > 0 && (
          <div className="mt-4 space-y-2">
            {Object.entries(uploadProgress).map(([filename]) => (
              <div key={filename} className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                <div className="animate-spin h-5 w-5 border-2 border-primary-500 border-t-transparent rounded-full"></div>
                <span className="text-sm text-gray-700">Subiendo {filename}...</span>
              </div>
            ))}
          </div>
        )}
        </div>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-center space-x-3">
            <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <h3 className="text-sm font-medium text-yellow-800">Sin permisos para subir documentos</h3>
              <p className="text-sm text-yellow-700 mt-1">
                Solo usuarios con rol Editor, Owner o Admin pueden subir documentos.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Documents List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Documentos Cargados
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({documents.length} documento{documents.length !== 1 ? 's' : ''})
            </span>
          </h2>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-gray-500">
            Cargando documentos...
          </div>
        ) : documents.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No hay documentos cargados para este bot.
            <br />
            <span className="text-sm">Sube tu primer documento arriba.</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Nombre del Archivo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID Documento
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Bot
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Chunks
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fecha de Carga
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {documents.map((doc: Document) => (
                  <tr key={doc.doc_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="mr-2">
                          {doc.filename.endsWith('.pdf') && '📕'}
                          {doc.filename.endsWith('.docx') && '📘'}
                          {doc.filename.endsWith('.txt') && '📄'}
                        </span>
                        <span className="text-sm font-medium text-gray-900">
                          {doc.filename}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-500 font-mono">
                        {doc.doc_id.substring(0, 12)}...
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">{doc.bot_id}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">{doc.chunks_count}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-500">
                        {formatDate(doc.uploaded_at)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex gap-3">
                        {canUploadDocuments && (
                          <button
                            onClick={() => handleMoveDocument(doc)}
                            disabled={moveMutation.isPending || bots.length <= 1}
                            className="text-blue-600 hover:text-blue-900 disabled:opacity-50 disabled:cursor-not-allowed"
                            title={bots.length <= 1 ? 'Necesitas al menos 2 bots para mover documentos' : 'Mover a otro bot'}
                          >
                            Mover
                          </button>
                        )}
                        {canDeleteDocuments ? (
                          <button
                            onClick={() => {
                              if (confirm(`¿Eliminar "${doc.filename}"?`)) {
                                deleteMutation.mutate(doc.doc_id);
                              }
                            }}
                            disabled={deleteMutation.isPending}
                            className="text-red-600 hover:text-red-900 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Eliminar
                          </button>
                        ) : (
                          <span className="text-gray-400 text-sm italic">Sin permisos</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Move Document Modal */}
      {moveModalOpen && documentToMove && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Mover Documento
            </h3>

            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                Documento: <span className="font-medium">{documentToMove.filename}</span>
              </p>
              <p className="text-sm text-gray-600 mb-4">
                Bot actual: <span className="font-medium">{documentToMove.bot_id}</span>
              </p>

              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mover a:
              </label>
              <select
                value={targetBotId}
                onChange={(e) => setTargetBotId(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                {bots
                  .filter(bot => bot.bot_id !== documentToMove.bot_id)
                  .map((bot) => (
                    <option key={bot.bot_id} value={bot.bot_id}>
                      {bot.name} ({bot.bot_id})
                    </option>
                  ))}
              </select>
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setMoveModalOpen(false);
                  setDocumentToMove(null);
                  setTargetBotId('');
                }}
                disabled={moveMutation.isPending}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={confirmMove}
                disabled={moveMutation.isPending || !targetBotId}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {moveMutation.isPending ? 'Moviendo...' : 'Mover Documento'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
