import React, { useState } from 'react';
import { Package, Plus, Minus, RotateCcw, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';
import { useApi } from '@/hooks/useApi';
import { stockService } from '@/services/stockService';
import { componentesService } from '@/services/componentesService';
import MovimientoStockForm from '@/components/forms/MovimientoStockForm';

const StockCard = ({ movimiento }) => {
  const getIconByType = (tipo) => {
    switch (tipo) {
      case 'entrada':
        return <TrendingUp className="h-5 w-5 text-green-600" />;
      case 'salida':
        return <TrendingDown className="h-5 w-5 text-red-600" />;
      case 'ajuste':
        return <RotateCcw className="h-5 w-5 text-blue-600" />;
      default:
        return <Package className="h-5 w-5 text-gray-600" />;
    }
  };

  const getColorByType = (tipo) => {
    switch (tipo) {
      case 'entrada':
        return 'bg-green-50 border-green-200';
      case 'salida':
        return 'bg-red-50 border-red-200';
      case 'ajuste':
        return 'bg-blue-50 border-blue-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className={`border rounded-lg p-4 ${getColorByType(movimiento.tipo_movimiento)}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          {getIconByType(movimiento.tipo_movimiento)}
          <div>
            <h4 className="font-medium text-gray-900">
              {movimiento.componente?.nombre}
            </h4>
            <p className="text-sm text-gray-500">
              {movimiento.componente?.numero_parte}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm font-medium text-gray-900">
            {movimiento.tipo_movimiento === 'salida' ? '-' : '+'}{movimiento.cantidad}
          </p>
          <p className="text-xs text-gray-500">
            {movimiento.cantidad_anterior} → {movimiento.cantidad_nueva}
          </p>
        </div>
      </div>
      
      {movimiento.motivo && (
        <p className="mt-2 text-sm text-gray-600">
          <strong>Motivo:</strong> {movimiento.motivo}
        </p>
      )}
      
      <div className="mt-2 flex justify-between text-xs text-gray-500">
        <span>{new Date(movimiento.fecha).toLocaleDateString()}</span>
        {movimiento.usuario && <span>Por: {movimiento.usuario}</span>}
      </div>
    </div>
  );
};

const ComponenteBajoStock = ({ componente }) => (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
    <div className="flex items-center space-x-3">
      <AlertTriangle className="h-5 w-5 text-red-600" />
      <div className="flex-1">
        <h4 className="font-medium text-red-900">{componente.nombre}</h4>
        <p className="text-sm text-red-700">
          Stock actual: {componente.stock_actual} | Mínimo: {componente.stock_minimo}
        </p>
      </div>
    </div>
  </div>
);

const Stock = () => {
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [filtros, setFiltros] = useState({
    componente_id: '',
    limit: 50
  });

  const { data: movimientos, loading: loadingMovimientos, refetch: refetchMovimientos } = useApi(
    ['stock-movimientos', filtros],
    () => stockService.getMovimientos(filtros)
  );

  const { data: resumen, loading: loadingResumen } = useApi(
    ['stock-resumen'],
    () => stockService.getResumen()
  );

  const { data: bajoStock, loading: loadingBajoStock } = useApi(
    ['stock-bajo-stock'],
    () => stockService.getBajoStock()
  );

  const { data: componentes } = useApi(
    ['componentes-activos'],
    () => componentesService.getAll({ activo: true })
  );

  const handleMovimientoSuccess = () => {
    setMostrarFormulario(false);
    refetchMovimientos();
  };

  if (loadingMovimientos || loadingResumen || loadingBajoStock) {
    return <div className="text-center py-8">Cargando información de stock...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Gestión de Stock</h1>
        <button
          onClick={() => setMostrarFormulario(true)}
          className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>Registrar Movimiento</span>
        </button>
      </div>

      {/* Resumen */}
      {resumen && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <Package className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Componentes</p>
                <p className="text-2xl font-bold text-gray-900">{resumen.total_componentes}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Bajo Stock</p>
                <p className="text-2xl font-bold text-gray-900">{resumen.componentes_bajo_stock}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">% Bajo Stock</p>
                <p className="text-2xl font-bold text-gray-900">{resumen.porcentaje_bajo_stock}%</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <Package className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Valor Inventario</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${resumen.valor_total_inventario?.toLocaleString() || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Alertas de bajo stock */}
      {bajoStock && bajoStock.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Componentes con Stock Bajo
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {bajoStock.map((componente) => (
              <ComponenteBajoStock key={componente.id} componente={componente} />
            ))}
          </div>
        </div>
      )}

      {/* Filtros */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filtrar por componente
            </label>
            <select
              value={filtros.componente_id}
              onChange={(e) => setFiltros(prev => ({ ...prev, componente_id: e.target.value }))}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Todos los componentes</option>
              {componentes?.map((componente) => (
                <option key={componente.id} value={componente.id}>
                  {componente.nombre} - {componente.numero_parte}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Límite de resultados
            </label>
            <select
              value={filtros.limit}
              onChange={(e) => setFiltros(prev => ({ ...prev, limit: parseInt(e.target.value) }))}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value={25}>25 movimientos</option>
              <option value={50}>50 movimientos</option>
              <option value={100}>100 movimientos</option>
            </select>
          </div>
        </div>
      </div>

      {/* Historial de movimientos */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Historial de Movimientos
        </h2>
        
        {movimientos && movimientos.length > 0 ? (
          <div className="space-y-4">
            {movimientos.map((movimiento) => (
              <StockCard key={movimiento.id} movimiento={movimiento} />
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Package className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              No hay movimientos registrados
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Los movimientos de stock aparecerán aquí.
            </p>
          </div>
        )}
      </div>

      {/* Modal de formulario */}
      {mostrarFormulario && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Registrar Movimiento de Stock
              </h3>
              <MovimientoStockForm
                onSuccess={handleMovimientoSuccess}
                onCancel={() => setMostrarFormulario(false)}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Stock;