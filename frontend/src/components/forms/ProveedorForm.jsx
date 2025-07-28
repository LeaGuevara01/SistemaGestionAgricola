import React from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { proveedoresService } from '@/services/proveedoresService';

const CONDICIONES_IVA = [
  'Responsable Inscripto',
  'Monotributista',
  'Exento',
  'Consumidor Final',
  'No Responsable'
];

const FORMAS_PAGO = [
  'Contado',
  'Cuenta Corriente',
  '30 días',
  '60 días',
  '90 días',
  'Cheque',
  'Transferencia'
];

const PROVINCIAS = [
  'Buenos Aires', 'Catamarca', 'Chaco', 'Chubut', 'Córdoba', 'Corrientes',
  'Entre Ríos', 'Formosa', 'Jujuy', 'La Pampa', 'La Rioja', 'Mendoza',
  'Misiones', 'Neuquén', 'Río Negro', 'Salta', 'San Juan', 'San Luis',
  'Santa Cruz', 'Santa Fe', 'Santiago del Estero', 'Tierra del Fuego',
  'Tucumán', 'CABA'
];

const ProveedorForm = ({ proveedor = null, onSuccess, onCancel }) => {
  const isEditing = !!proveedor;

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm({
    defaultValues: {
      nombre: proveedor?.nombre || '',
      razon_social: proveedor?.razon_social || '',
      cuit: proveedor?.cuit || '',
      telefono: proveedor?.telefono || '',
      email: proveedor?.email || '',
      direccion: proveedor?.direccion || '',
      ciudad: proveedor?.ciudad || '',
      provincia: proveedor?.provincia || '',
      codigo_postal: proveedor?.codigo_postal || '',
      contacto: proveedor?.contacto || '',
      condicion_iva: proveedor?.condicion_iva || '',
      forma_pago: proveedor?.forma_pago || ''
    }
  });

  const onSubmit = async (data) => {
    try {
      if (isEditing) {
        await proveedoresService.update(proveedor.id, data);
        toast.success('Proveedor actualizado correctamente');
      } else {
        await proveedoresService.create(data);
        toast.success('Proveedor creado correctamente');
        reset();
      }

      onSuccess?.();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Error al guardar el proveedor');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Información básica */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Nombre *
            </label>
            <input
              type="text"
              {...register('nombre', { required: 'El nombre es requerido' })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
            {errors.nombre && (
              <p className="mt-1 text-sm text-red-600">{errors.nombre.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Razón Social
            </label>
            <input
              type="text"
              {...register('razon_social')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              CUIT
            </label>
            <input
              type="text"
              placeholder="XX-XXXXXXXX-X"
              {...register('cuit', {
                pattern: {
                  value: /^\d{2}-\d{8}-\d{1}$/,
                  message: 'Formato de CUIT inválido (XX-XXXXXXXX-X)'
                }
              })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
            {errors.cuit && (
              <p className="mt-1 text-sm text-red-600">{errors.cuit.message}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Teléfono
              </label>
              <input
                type="tel"
                {...register('telefono')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                type="email"
                {...register('email', {
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Email inválido'
                  }
                })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Contacto
            </label>
            <input
              type="text"
              placeholder="Nombre del contacto"
              {...register('contacto')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>
        </div>

        {/* Dirección e información comercial */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Dirección
            </label>
            <input
              type="text"
              {...register('direccion')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Ciudad
              </label>
              <input
                type="text"
                {...register('ciudad')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Código Postal
              </label>
              <input
                type="text"
                {...register('codigo_postal')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Provincia
            </label>
            <select
              {...register('provincia')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Seleccionar provincia</option>
              {PROVINCIAS.map((provincia) => (
                <option key={provincia} value={provincia}>{provincia}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Condición IVA
            </label>
            <select
              {...register('condicion_iva')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Seleccionar condición</option>
              {CONDICIONES_IVA.map((condicion) => (
                <option key={condicion} value={condicion}>{condicion}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Forma de Pago
            </label>
            <select
              {...register('forma_pago')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Seleccionar forma de pago</option>
              {FORMAS_PAGO.map((forma) => (
                <option key={forma} value={forma}>{forma}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Botones */}
      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 bg-green-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
        >
          {isSubmitting ? 'Guardando...' : isEditing ? 'Actualizar' : 'Crear'}
        </button>
      </div>
    </form>
  );
};

export default ProveedorForm;