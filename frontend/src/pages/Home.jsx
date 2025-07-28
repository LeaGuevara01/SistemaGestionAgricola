// filepath: d:\Code\elorza\frontend\src\pages\Home.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Package, 
  Truck, 
  ShoppingCart, 
  Users, 
  Warehouse,
  AlertTriangle,
  TrendingUp,
  DollarSign
} from 'lucide-react';
import { useApi } from '@/hooks/useApi';
import { stockService } from '@/services/stockService';

const StatCard = ({ title, value, icon: Icon, color, link }) => (
  <Link to={link} className="block">
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center">
        <div className={`flex-shrink-0 ${color}`}>
          <Icon className="h-8 w-8" />
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">
              {title}
            </dt>
            <dd className="text-lg font-medium text-gray-900">
              {value}
            </dd>
          </dl>
        </div>
      </div>
    </div>
  </Link>
);

const Home = () => {
  const { data: resumenStock } = useApi(
    ['stock-resumen'],
    () => stockService.getResumen()
  );

  const stats = [
    {
      title: 'Total Componentes',
      value: resumenStock?.total_componentes || 0,
      icon: Package,
      color: 'text-blue-600',
      link: '/componentes'
    },
    {
      title: 'Componentes Bajo Stock',
      value: resumenStock?.componentes_bajo_stock || 0,
      icon: AlertTriangle,
      color: 'text-red-600',
      link: '/stock'
    },
    {
      title: 'Valor Inventario',
      value: `$${(resumenStock?.valor_total_inventario || 0).toLocaleString()}`,
      icon: DollarSign,
      color: 'text-green-600',
      link: '/stock'
    },
    {
      title: 'Máquinas Registradas',
      value: '0', // Esto se actualizará cuando implementemos el endpoint
      icon: Truck,
      color: 'text-purple-600',
      link: '/maquinas'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900">
          Sistema de Gestión Agrícola
        </h1>
        <p className="mt-2 text-gray-600">
          Bienvenido al panel de control. Aquí puedes ver un resumen de tu inventario y operaciones.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatCard key={index} {...stat} />
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          Acciones Rápidas
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link
            to="/componentes/agregar"
            className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <Package className="h-8 w-8 text-blue-600 mb-2" />
            <span className="text-sm font-medium">Agregar Componente</span>
          </Link>
          <Link
            to="/compras/registrar"
            className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <ShoppingCart className="h-8 w-8 text-green-600 mb-2" />
            <span className="text-sm font-medium">Registrar Compra</span>
          </Link>
          <Link
            to="/stock/movimiento"
            className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <Warehouse className="h-8 w-8 text-purple-600 mb-2" />
            <span className="text-sm font-medium">Movimiento Stock</span>
          </Link>
          <Link
            to="/estadisticas"
            className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <TrendingUp className="h-8 w-8 text-orange-600 mb-2" />
            <span className="text-sm font-medium">Ver Estadísticas</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;