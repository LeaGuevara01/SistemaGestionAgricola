import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useComponente } from '@/hooks/useApi';
import ComponenteForm from '@/components/forms/ComponenteForm';
import MaquinasComponenteWidget from '@/components/MaquinasComponenteWidget';

const EditarComponente = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: componente, loading, error } = useComponente(id);

  const handleSuccess = () => {
    navigate('/componentes');
  };

  const handleCancel = () => {
    navigate('/componentes');
  };

  if (loading) return <div className="text-center py-4">Cargando...</div>;
  if (error) return <div className="text-red-500 text-center py-4">Error: {error}</div>;
  if (!componente) return <div className="text-center py-4">Componente no encontrado</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/componentes')}
          className="p-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <h1 className="text-2xl font-bold text-gray-900">
          Editar Componente: {componente.nombre}
        </h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Formulario de edición */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg p-6">
            {componente.foto && (
              <img
                src={`/static/fotos/${componente.foto}`}
                alt={componente.nombre}
                className="w-32 h-32 object-cover rounded mb-4"
                onError={(e) => {
                  console.error('Error cargando imagen:', e.target.src);
                  // ✅ Mostrar placeholder en lugar de ocultar
                  e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik03NSA5MEM3NSA4Ni4xMzQgNzguMTM0IDgzIDgyIDgzSDExOEM5My44NjYgODMgOTcgODYuMTM0IDk3IDkwVjExMEM5NyAxMTMuODY2IDkzLjg2NiAxMTcgOTAgMTE3SDgyQzc4LjEzNCAxMTcgNzUgMTEzLjg2NiA3NSAxMTBWOTBaIiBzdHJva2U9IiM5Q0EzQUYiIHN0cm9rZS13aWR0aD0iMiIvPgo8cGF0aCBkPSJNMTM1IDkwQzEzNSA4Ni4xMzQgMTM4LjEzNCA4MyAxNDIgODNIMTU4QzE2MS44NjYgODMgMTY1IDg2LjEzNCAxNjUgOTBWMTEwQzE2NSAxMTMuODY2IDE2MS44NjYgMTE3IDE1OCAxMTdIMTQyQzEzOC4xMzQgMTE3IDEzNSAxMTMuODY2IDEzNSAxMTBWOTBaIiBzdHJva2U9IiM5Q0EzQUYiIHN0cm9rZS13aWR0aD0iMiIvPgo8L3N2Zz4K';
                  e.target.alt = 'Imagen no disponible';
                }}
              />
            )}
            <ComponenteForm
              componente={componente}
              onSuccess={handleSuccess}
              onCancel={handleCancel}
            />
          </div>
        </div>

        {/* Widget de máquinas */}
        <div className="lg:col-span-1">
          <MaquinasComponenteWidget componenteId={id} />
        </div>
      </div>
    </div>
  );
};

export default EditarComponente;