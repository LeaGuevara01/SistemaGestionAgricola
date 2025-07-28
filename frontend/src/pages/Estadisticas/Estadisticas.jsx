import React, { useState } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  DollarSign, 
  Package, 
  Truck,
  ShoppingCart,
  Calendar,
  AlertTriangle 
} from 'lucide-react';
import { useApi } from '@/hooks/useApi';
import { estadisticasService } from '@/services/estadisticasService';

const StatCard = ({ title, value, icon: Icon, color, change, changeType }) => (
  <div className="bg-white rounded-lg shadow p-6">
    <div className="flex items-center">
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon className="h-6 w-6 text-white" />
      </div>
      <div className="ml-4 flex-1">
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        {change && (
          <div className={`flex items-center text-sm ${
            changeType === 'positive' ? 'text-green-600' : 'text-red-600'
          }`}>
            <TrendingUp className="h-4 w-4 mr-1" />
            <span>{change}</span>
          </div>
        )}
      </div>
    </div>
  </div>
);

const Estadisticas = () => {
  const [periodo, setPeriodo] = useState('mes');

  const { data: resumen, loading: loadingResumen } = useApi(
    ['estadisticas-resumen'],
    () => estadisticasService.getResumenGeneral()
  );

  const { data: comprasPeriodo, loading: loadingCompras } = useApi(
    ['estadisticas-compras', periodo],
    () => estadisticasService.getComprasPorPeriodo(periodo)
  );

  const { data: stockCritico, loading: loadingStock } = useApi(
    ['estadisticas-stock-critico'],
    () => estadisticasService.getStockCritico()
  );

  const { data: topProveedores, loading: loadingProveedores } = useApi(
    ['estadisticas-top-proveedores', periodo],
    () => estadisticasService.getTopProveedores(periodo)
  );

  if (loadingResumen || loadingCompras || loadingStock || loadingProveedores) {
    return <div className="text-center py-8">Cargando estadísticas...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Estadísticas</h1>
        <select
          value={periodo}
          onChange={(e) => setPeriodo(e.target.value)}
          className="rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
        >
          <option value="semana">Última semana</option>
          <option value="mes">Último mes</option>
          <option value="trimestre">Último trimestre</option>
          <option value="año">Último año</option>
        </select>
      </div>

      {/* Tarjetas de resumen */}
      {resumen && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Componentes"
            value={resumen.total_componentes}
            icon={Package}
            color="bg-blue-500"
          />
          <StatCard
            title="Total Máquinas"
            value={resumen.total_maquinas}
            icon={Truck}
            color="bg-green-500"
          />
          <StatCard
            title="Compras este mes"
            value={resumen.compras_mes}
            icon={ShoppingCart}
            color="bg-purple-500"
            change={`${resumen.cambio_compras}%`}
            changeType={resumen.cambio_compras > 0 ? 'positive' : 'negative'}
          />
          <StatCard
            title="Valor inventario"
            value={`$${resumen.valor_inventario?.toLocaleString() || 0}`}
            icon={DollarSign}
            color="bg-yellow-500"
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de compras por período */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <BarChart3 className="h-5 w-5 mr-2" />
            Compras por {periodo}
          </h2>
          {comprasPeriodo && comprasPeriodo.length > 0 ? (
            <div className="space-y-3">
              {comprasPeriodo.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                    <span className="text-sm text-gray-600">{item.fecha}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">{item.cantidad} compras</div>
                    <div className="text-xs text-gray-500">${item.total}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No hay datos para mostrar</p>
          )}
        </div>

        {/* Top proveedores */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Top Proveedores - {periodo}
          </h2>
          {topProveedores && topProveedores.length > 0 ? (
            <div className="space-y-3">
              {topProveedores.map((proveedor, index) => (
                <div key={proveedor.id} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                      index === 0 ? 'bg-yellow-500' :
                      index === 1 ? 'bg-gray-400' :
                      index === 2 ? 'bg-orange-500' :
                      'bg-gray-300'
                    }`}>
                      {index + 1}
                    </div>
                    <div className="ml-3">
                      <div className="text-sm font-medium">{proveedor.nombre}</div>
                      <div className="text-xs text-gray-500">{proveedor.total_compras} compras</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-green-600">
                      ${proveedor.total_gastado?.toLocaleString() || 0}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No hay datos para mostrar</p>
          )}
        </div>
      </div>

      {/* Stock crítico */}
      {stockCritico && stockCritico.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2 text-red-500" />
            Componentes con Stock Crítico
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {stockCritico.map((componente) => (
              <div key={componente.id} className="border border-red-200 rounded-lg p-4 bg-red-50">
                <h3 className="font-medium text-gray-900">{componente.nombre}</h3>
                <p className="text-sm text-gray-600">{componente.numero_parte}</p>
                <div className="mt-2 flex justify-between text-sm">
                  <span className="text-red-600">Stock: {componente.stock_actual}</span>
                  <span className="text-gray-500">Mín: {componente.stock_minimo}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Estadisticas;