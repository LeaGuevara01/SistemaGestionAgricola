import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Package, 
  Truck, 
  ShoppingCart, 
  Users, 
  Warehouse,
  BarChart3,
  CreditCard 
} from 'lucide-react';
import { clsx } from 'clsx';

const navigation = [
  { name: 'Inicio', href: '/', icon: Home },
  { name: 'Componentes', href: '/componentes', icon: Package },
  { name: 'Máquinas', href: '/maquinas', icon: Truck },
  { name: 'Compras', href: '/compras', icon: ShoppingCart },
  { name: 'Proveedores', href: '/proveedores', icon: Users },
  { name: 'Stock', href: '/stock', icon: Warehouse },
  { name: 'Estadísticas', href: '/estadisticas', icon: BarChart3 },
  { name: 'Pagos', href: '/pagos', icon: CreditCard },
];

const Sidebar = () => {
  const location = useLocation();

  return (
    <div className="w-64 bg-white shadow-sm h-screen sticky top-16">
      <nav className="mt-5 px-2">
        <div className="space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={clsx(
                  'group flex items-center px-2 py-2 text-sm font-medium rounded-md',
                  isActive
                    ? 'bg-green-100 text-green-900'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )}
              >
                <item.icon
                  className={clsx(
                    'mr-3 h-5 w-5',
                    isActive ? 'text-green-500' : 'text-gray-400 group-hover:text-gray-500'
                  )}
                />
                {item.name}
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
};

export default Sidebar;