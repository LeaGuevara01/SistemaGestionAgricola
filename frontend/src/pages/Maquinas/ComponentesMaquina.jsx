import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Plus, Search, Package, Trash2, AlertCircle } from 'lucide-react';
import { useMaquina, useMaquinaComponentes } from '@/hooks/useApi';
import { maquinasComponentesService } from '@/services/maquinasComponentesService';
import { toast } from 'react-hot-toast';
import AsignarComponentesModal from '@/components/modals/AsignarComponentesModal';

const ComponenteCard = ({ componente, maquinaId, onDesasignar }) => {
  const handleDesasignar = async () => {
    if (window.confirm('¿Estás seguro de que quieres desasignar este componente de la máquina?')) {
      try {
        await maquinasComponentesService.desasignarComponente(maquinaId, componente.id);
        toast.success('Componente desasignado correctamente');
        onDesasignar();
      } catch (error) {
        console.error('Error al desasignar componente:', error);
        toast.error('Error al desasignar el componente');
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center">
          {componente.foto ? (
            <img
              src={`/static/fotos/${componente.foto}`}
              alt={componente.nombre}
              className="w-16 h-16 rounded-lg object-cover mr-4"
            />
          ) : (
            <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center mr-4">
              <Package className="h-8 w-8 text-gray-400" />
            </div>
          )}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {componente.nombre}
            </h3>
            <p className="text-sm text-gray-500">
              {componente.categoria || 'Sin categoría'}
            </p>
            {componente.numero_parte && (
              <p className="text-xs text-gray-400">
                P/N: {componente.numero_parte}
              </p>
            )}
          </div>
        </div>
        
        <div className="flex space-x-2">
          <Link
            to={`/componentes/editar/${componente.id}`}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded"
            title="Editar componente"
          >
            <Package className="h-4 w-4" />
          </Link>
          <button
            onClick={handleDesasignar}
            className="p-2 text-red-600 hover:bg-red-50 rounded"
            title="Desasignar de la máquina"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      <p className="text-gray-600 mb-3 text-sm line-clamp-2">
        {componente.descripcion}
      </p>

      <div className="grid grid-cols-2 gap-3 text-sm">
        {componente.precio && (
          <div className="flex justify-between">
            <span className="text-gray-500">Precio:</span>
            <span className="font-medium">${componente.precio}</span>
          </div>
        )}
        
        {componente.stock_actual !== undefined && (
          <div className="flex justify-between">
            <span className="text-gray-500">Stock:</span>
            <span className={`font-medium ${componente.stock_actual <= 0 ? 'text-red-600' : 'text-green-600'}`}>
              {componente.stock_actual}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

const ComponentesMaquina = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [filtros, setFiltros] = useState({
    search: ''
  });
  const [showAsignarModal, setShowAsignarModal] = useState(false);

  const { data: maquina, loading: loadingMaquina, error: errorMaquina } = useMaquina(id);
  const { 
    data: componentesData, 
    loading: loadingComponentes, 
    error: errorComponentes, 
    refetch 
  } = useMaquinaComponentes(id, filtros);

  const handleFilterChange = (key, value) => {
    setFiltros(prev => ({ ...prev, [key]: value }));
  };

  const handleAsignarSuccess = () => {
    refetch();
    setShowAsignarModal(false);
  };

  if (loadingMaquina || loadingComponentes) {
    return <div className="text-center py-8">Cargando...</div>;
  }

  if (errorMaquina || errorComponentes) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="mx-auto h-12 w-12 text-red-400" />
        <h3 className="mt-2 text-sm font-medium text-red-800">Error al cargar los datos</h3>
        <p className="mt-1 text-sm text-red-600">
          {errorMaquina || errorComponentes}
        </p>
      </div>
    );
  }

  const componentes = componentesData?.data || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/maquinas')}
          className="p-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Componentes de {maquina?.nombre}
          </h1>
          <p className="text-sm text-gray-500">
            {maquina?.marca} {maquina?.modelo} - {componentes.length} componente(s) asignado(s)
          </p>
        </div>
      </div>

      {/* Acciones */}
      <div className="flex justify-between items-center">
        <div className="flex space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar componentes..."
              value={filtros.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="pl-10 w-64 rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>
        </div>

        <button
          onClick={() => setShowAsignarModal(true)}
          className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>Asignar Componentes</span>
        </button>
      </div>

      {/* Lista de componentes */}
      {componentes.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {componentes.map((componente) => (
            <ComponenteCard
              key={componente.id}
              componente={componente}
              maquinaId={id}
              onDesasignar={refetch}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Package className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No hay componentes asignados
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Comienza asignando componentes a esta máquina.
          </p>
          <div className="mt-6">
            <button
              onClick={() => setShowAsignarModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              <Plus className="h-5 w-5 mr-2" />
              Asignar Componentes
            </button>
          </div>
        </div>
      )}

      {/* Modal para asignar componentes */}
      {showAsignarModal && (
        <AsignarComponentesModal
          maquina={maquina}
          onClose={() => setShowAsignarModal(false)}
          onSuccess={handleAsignarSuccess}
        />
      )}
    </div>
  );
};

export default ComponentesMaquina;
