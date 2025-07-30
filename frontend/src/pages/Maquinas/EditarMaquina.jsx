import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useMaquina } from '@/hooks/useApi';
import MaquinaForm from '@/components/forms/MaquinaForm';
import ComponentesMaquinaWidget from '@/components/ComponentesMaquinaWidget';

const EditarMaquina = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: maquina, loading, error } = useMaquina(id);

  const handleSuccess = () => {
    navigate('/maquinas');
  };

  const handleCancel = () => {
    navigate('/maquinas');
  };

  if (loading) return <div className="text-center py-4">Cargando...</div>;
  if (error) return <div className="text-red-500 text-center py-4">Error: {error}</div>;
  if (!maquina) return <div className="text-center py-4">Máquina no encontrada</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/maquinas')}
          className="p-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <h1 className="text-2xl font-bold text-gray-900">
          Editar Máquina: {maquina.nombre}
        </h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Formulario de edición */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg p-6">
            <MaquinaForm
              maquina={maquina}
              onSuccess={handleSuccess}
              onCancel={handleCancel}
            />
          </div>
        </div>

        {/* Widget de componentes */}
        <div className="lg:col-span-1">
          <ComponentesMaquinaWidget maquinaId={id} />
        </div>
      </div>
    </div>
  );
};

export default EditarMaquina;