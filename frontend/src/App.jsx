import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';

// Páginas principales
import Home from './pages/Home';

// Componentes
import ListarComponentes from './pages/Componentes/ListarComponentes';
import AgregarComponentes from './pages/Componentes/AgregarComponentes'; // ✅ CORREGIDO
import EditarComponente from './pages/Componentes/EditarComponente';

// Máquinas
import ListarMaquinas from './pages/Maquinas/ListarMaquinas'; // ✅ CORREGIDO
import AgregarMaquina from './pages/Maquinas/AgregarMaquina';
import EditarMaquina from './pages/Maquinas/EditarMaquina';

// Compras
import ListarCompras from './pages/Compras/ListarCompras'; // ✅ CORREGIDO
import RegistrarCompra from './pages/Compras/RegistrarCompra';
import EditarCompra from './pages/Compras/EditarCompra';

// Proveedores
import ListarProveedores from './pages/Proveedores/ListarProveedores'; // ✅ CORREGIDO
import AgregarProveedor from './pages/Proveedores/AgregarProveedor';
import EditarProveedor from './pages/Proveedores/EditarProveedor';

// Stock
import Stock from './pages/Stock/Stock'; // ✅ CORREGIDO

// Estadísticas
import Estadisticas from './pages/Estadisticas/Estadisticas'; // ✅ CORREGIDO

// Pagos
import Pagos from './pages/Pagos/Pagos'; // ✅ CORREGIDO

// Crear cliente de React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutos
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Layout>
            <Routes>
              {/* Página principal */}
              <Route path="/" element={<Home />} />

              {/* Rutas de Componentes */}
              <Route path="/componentes" element={<ListarComponentes />} />
              <Route path="/componentes/agregar" element={<AgregarComponentes />} />
              <Route path="/componentes/editar/:id" element={<EditarComponente />} />

              {/* Rutas de Máquinas */}
              <Route path="/maquinas" element={<ListarMaquinas />} />
              <Route path="/maquinas/agregar" element={<AgregarMaquina />} />
              <Route path="/maquinas/editar/:id" element={<EditarMaquina />} />

              {/* Rutas de Compras */}
              <Route path="/compras" element={<ListarCompras />} />
              <Route path="/compras/registrar" element={<RegistrarCompra />} />
              <Route path="/compras/editar/:id" element={<EditarCompra />} />

              {/* Rutas de Proveedores */}
              <Route path="/proveedores" element={<ListarProveedores />} />
              <Route path="/proveedores/agregar" element={<AgregarProveedor />} />
              <Route path="/proveedores/editar/:id" element={<EditarProveedor />} />

              {/* Rutas de Stock */}
              <Route path="/stock" element={<Stock />} />

              {/* Rutas de Estadísticas */}
              <Route path="/estadisticas" element={<Estadisticas />} />

              {/* Rutas de Pagos */}
              <Route path="/pagos" element={<Pagos />} />

              {/* Ruta 404 */}
              <Route path="*" element={
                <div className="text-center py-12">
                  <h2 className="text-2xl font-bold text-gray-900">Página no encontrada</h2>
                  <p className="mt-2 text-gray-600">La página que buscas no existe.</p>
                </div>
              } />
            </Routes>
          </Layout>
        </div>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </Router>
    </QueryClientProvider>
  );
}

export default App;