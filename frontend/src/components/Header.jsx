import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Truck,        // ✅ Camión
  Wrench,       // ✅ Herramienta
  Cog,          // ✅ Engranaje
  Package,      // ✅ Paquete
  Leaf,         // ✅ Hoja (naturaleza)
  Sun,          // ✅ Sol
  Cloud,        // ✅ Nube
  Zap,           // ✅ Energía
  Bell, User, ArrowLeft
 } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo y título */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-3">
              <Truck className="h-8 w-8 text-green-600" />
              <span className="text-xl font-bold text-gray-900">
                Sistema Agrícola Elorza
              </span>
            </Link>
          </div>

          {/* Navegación del header */}
          <div className="flex items-center space-x-4">
            {/* Notificaciones */}
            <button className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md">
              <Bell className="h-5 w-5" />
              <span className="absolute top-1 right-1 block h-2 w-2 rounded-full bg-red-400"></span>
            </button>

            {/* Usuario */}
            <button className="flex items-center space-x-2 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md">
              <User className="h-5 w-5" />
              <span className="text-sm font-medium">Admin</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;