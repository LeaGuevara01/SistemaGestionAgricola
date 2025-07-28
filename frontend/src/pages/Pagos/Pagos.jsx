import React, { useState } from 'react';
import { 
  CreditCard, 
  Calendar, 
  DollarSign, 
  Clock, 
  CheckCircle, 
  XCircle,
  AlertTriangle,
  Plus,
  Search,
  Filter
} from 'lucide-react';
import { useApi } from '@/hooks/useApi';
import { pagosService } from '@/services/pagosService';
import { comprasService } from '@/services/comprasService';
import { toast } from 'react-hot-toast';

const ESTADOS_PAGO = {
  PENDIENTE: 'pendiente',
  PAGADO: 'pagado',
  VENCIDO: 'vencido'
};

const PagoCard = ({ pago, onUpdate }) => {
  const [pagando, setPagando] = useState(false);

  const getEstadoIcon = (estado) => {
    switch (estado) {
      case ESTADOS_PAGO.PAGADO:
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case ESTADOS_PAGO.VENCIDO:
        return <XCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Clock className="h-5 w-5 text-yellow-600" />;
    }
  };

  const getEstadoColor = (estado) => {
    switch (estado) {
      case ESTADOS_PAGO.PAGADO:
        return 'bg-green-100 text-green-800';
      case ESTADOS_PAGO.VENCIDO:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const marcarComoPagado = async () => {
    setPagando(true);
    try {
      await pagosService.marcarComoPagado(pago.id);
      toast.success('Pago marcado como pagado');
      onUpdate();
    } catch (error) {
      toast.error('Error al marcar el pago');
    } finally {
      setPagando(false);
    }
  };

  const diasVencimiento = Math.ceil((new Date(pago.fecha_vencimiento) - new Date()) / (1000 * 60 * 60 * 24));

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
            <CreditCard className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {pago.proveedor?.nombre}
            </h3>
            <p className="text-sm text-gray-500">
              Compra #{pago.compra?.id}
            </p>
            {pago.compra?.numero_factura && (
              <p className="text-xs text-gray-400">
                Factura: {pago.compra.numero_factura}
              </p>
            )}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {getEstadoIcon(pago.estado)}
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getEstadoColor(pago.estado)}`}>
            {pago.estado?.charAt(0).toUpperCase() + pago.estado?.slice(1)}
          </span>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between">
          <span className="text-sm text-gray-500">Monto:</span>
          <span className="text-lg font-bold text-gray-900 flex items-center">
            <DollarSign className="h-4 w-4" />
            {pago.monto}
          </span>
        </div>

        <div className="flex justify-between">
          <span className="text-sm text-gray-500">Fecha de vencimiento:</span>
          <span className="text-sm font-medium flex items-center">
            <Calendar className="h-4 w-4 mr-1" />
            {new Date(pago.fecha_vencimiento).toLocaleDateString()}
          </span>
        </div>

        {pago.estado === ESTADOS_PAGO.PENDIENTE && (
          <div className="flex justify-between">
            <span className="text-sm text-gray-500">Días para vencimiento:</span>
            <span className={`text-sm font-medium ${
              diasVencimiento < 0 ? 'text-red-600' : 
              diasVencimiento <= 3 ? 'text-yellow-600' : 
              'text-green-600'
            }`}>
              {diasVencimiento < 0 ? `${Math.abs(diasVencimiento)} días vencido` : `${diasVencimiento} días`}
            </span>
          </div>
        )}

        {pago.fecha_pago && (
          <div className="flex justify-between">
            <span className="text-sm text-gray-500">Fecha de pago:</span>
            <span className="text-sm font-medium text-green-600">
              {new Date(pago.fecha_pago).toLocaleDateString()}
            </span>
          </div>
        )}

        {pago.observaciones && (
          <div className="pt-2 border-t">
            <p className="text-sm text-gray-600">{pago.observaciones}</p>
          </div>
        )}
      </div>

      {pago.estado === ESTADOS_PAGO.PENDIENTE && (
        <div className="mt-4 pt-4 border-t">
          <button
            onClick={marcarComoPagado}
            disabled={pagando}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {pagando ? 'Procesando...' : 'Marcar como Pagado'}
          </button>
        </div>
      )}
    </div>
  );
};

const Pagos = () => {
  const [filtros, setFiltros] = useState({
    estado: '',
    proveedor_id: '',
    fecha_desde: '',
    fecha_hasta: ''
  });

  const { data: pagos, loading, error, refetch } = useApi(
    ['pagos', filtros],
    () => pagosService.getAll(filtros)
  );

  const { data: resumen, loading: loadingResumen } = useApi(
    ['pagos-resumen'],
    () => pagosService.getResumen()
  );

  const { data: comprasPendientes, loading: loadingCompras } = useApi(
    ['compras-sin-pago'],
    () => comprasService.getSinPago()
  );

  const [mostrandoFormulario, setMostrandoFormulario] = useState(false);

  const handleFilterChange = (key, value) => {
    setFiltros(prev => ({ ...prev, [key]: value }));
  };

  const generarPagosAutomaticos = async () => {
    try {
      await pagosService.generarPagosAutomaticos();
      toast.success('Pagos generados automáticamente');
      refetch();
    } catch (error) {
      toast.error('Error al generar pagos automáticos');
    }
  };

  if (loading || loadingResumen) {
    return <div className="text-center py-8">Cargando información de pagos...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center py-8">Error: {error}</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Gestión de Pagos</h1>
        <div className="flex space-x-3">
          <button
            onClick={generarPagosAutomaticos}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg flex items-center space-x-2"
          >
            <Plus className="h-5 w-5" />
            <span>Generar Pagos</span>
          </button>
        </div>
      </div>

      {/* Resumen */}
      {resumen && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Pendientes</p>
                <p className="text-2xl font-bold text-gray-900">{resumen.pendientes || 0}</p>
                <p className="text-sm text-gray-600">${resumen.monto_pendiente || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <XCircle className="h-8 w-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Vencidos</p>
                <p className="text-2xl font-bold text-gray-900">{resumen.vencidos || 0}</p>
                <p className="text-sm text-gray-600">${resumen.monto_vencido || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Pagados este mes</p>
                <p className="text-2xl font-bold text-gray-900">{resumen.pagados_mes || 0}</p>
                <p className="text-sm text-gray-600">${resumen.monto_pagado_mes || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Próximos a vencer</p>
                <p className="text-2xl font-bold text-gray-900">{resumen.proximos_vencer || 0}</p>
                <p className="text-sm text-gray-600">Próximos 7 días</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filtros */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estado
            </label>
            <select
              value={filtros.estado}
              onChange={(e) => handleFilterChange('estado', e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Todos los estados</option>
              <option value={ESTADOS_PAGO.PENDIENTE}>Pendiente</option>
              <option value={ESTADOS_PAGO.PAGADO}>Pagado</option>
              <option value={ESTADOS_PAGO.VENCIDO}>Vencido</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha desde
            </label>
            <input
              type="date"
              value={filtros.fecha_desde}
              onChange={(e) => handleFilterChange('fecha_desde', e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha hasta
            </label>
            <input
              type="date"
              value={filtros.fecha_hasta}
              onChange={(e) => handleFilterChange('fecha_hasta', e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={() => setFiltros({
                estado: '',
                proveedor_id: '',
                fecha_desde: '',
                fecha_hasta: ''
              })}
              className="w-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Limpiar Filtros
            </button>
          </div>
        </div>
      </div>

      {/* Lista de pagos */}
      {pagos && pagos.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {pagos.map((pago) => (
            <PagoCard
              key={pago.id}
              pago={pago}
              onUpdate={refetch}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <CreditCard className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No hay pagos registrados
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Los pagos aparecerán aquí una vez que registres compras.
          </p>
        </div>
      )}
    </div>
  );
};

export default Pagos;