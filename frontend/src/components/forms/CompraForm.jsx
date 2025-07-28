import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { comprasService } from '@/services/comprasService';
import { componentesService } from '@/services/componentesService';
import { maquinasService } from '@/services/maquinasService';
import { proveedoresService } from '@/services/proveedoresService';
import { ESTADOS } from '@/config';

const CompraForm = ({ compra = null, onSuccess, onCancel }) => {
  const [componentes, setComponentes] = useState([]);
  const [maquinas, setMaquinas] = useState([]);
  const [proveedores, setProveedores] = useState([]);
  const [tipoItem, setTipoItem] = useState(compra?.componente_id ? 'componente' : 'maquina');
  const [precioCalculado, setPrecioCalculado] = useState(0);
  const isEditing = !!compra;

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
    setValue,
    reset
  } = useForm({
    defaultValues: {
      numero_factura: compra?.numero_factura || '',
      fecha_compra: compra?.fecha_compra || new Date().toISOString().split('T')[0],
      fecha_entrega: compra?.fecha_entrega || '',
      cantidad: compra?.cantidad || 1,
      precio_unitario: compra?.precio_unitario || 0,
      iva: compra?.iva || 21,
      descuento: compra?.descuento || 0,
      estado: compra?.estado || 'pendiente',
      observaciones: compra?.observaciones || '',
      componente_id: compra?.componente_id || '',
      maquina_id: compra?.maquina_id || '',
      proveedor_id: compra?.proveedor_id || ''
    }
  });

  // Observar cambios en los valores para calcular precio total
  const cantidad = watch('cantidad');
  const precioUnitario = watch('precio_unitario');
  const iva = watch('iva');
  const descuento = watch('descuento');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [componentesData, maquinasData, proveedoresData] = await Promise.all([
          componentesService.getAll({ activo: true }),
          maquinasService.getAll({ activo: true }),
          proveedoresService.getAll({ activo: true })
        ]);
        
        setComponentes(componentesData);
        setMaquinas(maquinasData);
        setProveedores(proveedoresData);
      } catch (error) {
        toast.error('Error al cargar los datos');
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    // Calcular precio total
    const cant = parseFloat(cantidad) || 0;
    const precioUnit = parseFloat(precioUnitario) || 0;
    const ivaVal = parseFloat(iva) || 0;
    const descuentoVal = parseFloat(descuento) || 0;

    const subtotal = cant * precioUnit;
    const totalDescuento = subtotal * (descuentoVal / 100);
    const subtotalConDescuento = subtotal - totalDescuento;
    const totalIva = subtotalConDescuento * (ivaVal / 100);
    const total = subtotalConDescuento + totalIva;

    setPrecioCalculado(total);
  }, [cantidad, precioUnitario, iva, descuento]);

  const onSubmit = async (data) => {
    try {
      const formData = {
        ...data,
        cantidad: parseInt(data.cantidad),
        precio_unitario: parseFloat(data.precio_unitario),
        iva: parseFloat(data.iva),
        descuento: parseFloat(data.descuento),
        componente_id: tipoItem === 'componente' ? data.componente_id || null : null,
        maquina_id: tipoItem === 'maquina' ? data.maquina_id || null : null,
        fecha_entrega: data.fecha_entrega || null
      };

      if (isEditing) {
        await comprasService.update(compra.id, formData);
        toast.success('Compra actualizada correctamente');
      } else {
        await comprasService.create(formData);
        toast.success('Compra registrada correctamente');
        reset();
        setPrecioCalculado(0);
      }

      onSuccess?.();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Error al guardar la compra');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Información básica */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Proveedor *
            </label>
            <select
              {...register('proveedor_id', { required: 'El proveedor es requerido' })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Seleccionar proveedor</option>
              {proveedores.map((proveedor) => (
                <option key={proveedor.id} value={proveedor.id}>
                  {proveedor.nombre}
                </option>
              ))}
            </select>
            {errors.proveedor_id && (
              <p className="mt-1 text-sm text-red-600">{errors.proveedor_id.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Tipo de Item *
            </label>
            <div className="mt-2 space-x-4">
              <label className="inline-flex items-center">
                <input
                  type="radio"
                  value="componente"
                  checked={tipoItem === 'componente'}
                  onChange={(e) => {
                    setTipoItem(e.target.value);
                    setValue('maquina_id', '');
                  }}
                  className="form-radio text-green-600"
                />
                <span className="ml-2">Componente</span>
              </label>
              <label className="inline-flex items-center">
                <input
                  type="radio"
                  value="maquina"
                  checked={tipoItem === 'maquina'}
                  onChange={(e) => {
                    setTipoItem(e.target.value);
                    setValue('componente_id', '');
                  }}
                  className="form-radio text-green-600"
                />
                <span className="ml-2">Máquina</span>
              </label>
            </div>
          </div>

          {tipoItem === 'componente' && (
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Componente *
              </label>
              <select
                {...register('componente_id', { 
                  required: tipoItem === 'componente' ? 'El componente es requerido' : false 
                })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              >
                <option value="">Seleccionar componente</option>
                {componentes.map((componente) => (
                  <option key={componente.id} value={componente.id}>
                    {componente.nombre} - {componente.numero_parte}
                  </option>
                ))}
              </select>
              {errors.componente_id && (
                <p className="mt-1 text-sm text-red-600">{errors.componente_id.message}</p>
              )}
            </div>
          )}

          {tipoItem === 'maquina' && (
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Máquina *
              </label>
              <select
                {...register('maquina_id', { 
                  required: tipoItem === 'maquina' ? 'La máquina es requerida' : false 
                })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              >
                <option value="">Seleccionar máquina</option>
                {maquinas.map((maquina) => (
                  <option key={maquina.id} value={maquina.id}>
                    {maquina.nombre} - {maquina.marca} {maquina.modelo}
                  </option>
                ))}
              </select>
              {errors.maquina_id && (
                <p className="mt-1 text-sm text-red-600">{errors.maquina_id.message}</p>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Número de Factura
            </label>
            <input
              type="text"
              {...register('numero_factura')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Fecha de Compra *
              </label>
              <input
                type="date"
                {...register('fecha_compra', { required: 'La fecha de compra es requerida' })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
              {errors.fecha_compra && (
                <p className="mt-1 text-sm text-red-600">{errors.fecha_compra.message}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Fecha de Entrega
              </label>
              <input
                type="date"
                {...register('fecha_entrega')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Estado
            </label>
            <select
              {...register('estado')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value={ESTADOS.COMPRA.PENDIENTE}>Pendiente</option>
              <option value={ESTADOS.COMPRA.ENTREGADO}>Entregado</option>
              <option value={ESTADOS.COMPRA.CANCELADO}>Cancelado</option>
            </select>
          </div>
        </div>

        {/* Información de precios */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Cantidad *
            </label>
            <input
              type="number"
              min="1"
              {...register('cantidad', { required: 'La cantidad es requerida', min: 1 })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
            {errors.cantidad && (
              <p className="mt-1 text-sm text-red-600">{errors.cantidad.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Precio Unitario *
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              {...register('precio_unitario', { required: 'El precio unitario es requerido', min: 0 })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
            {errors.precio_unitario && (
              <p className="mt-1 text-sm text-red-600">{errors.precio_unitario.message}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Descuento (%)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="100"
                {...register('descuento')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                IVA (%)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="100"
                {...register('iva')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
          </div>

          {/* Resumen de precios */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Resumen</h4>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span>Subtotal:</span>
                <span>${((cantidad || 0) * (precioUnitario || 0)).toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>Descuento:</span>
                <span>-${(((cantidad || 0) * (precioUnitario || 0)) * ((descuento || 0) / 100)).toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>IVA:</span>
                <span>${((((cantidad || 0) * (precioUnitario || 0)) - (((cantidad || 0) * (precioUnitario || 0)) * ((descuento || 0) / 100))) * ((iva || 0) / 100)).toFixed(2)}</span>
              </div>
              <div className="flex justify-between font-bold text-lg border-t pt-1">
                <span>Total:</span>
                <span>${precioCalculado.toFixed(2)}</span>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Observaciones
            </label>
            <textarea
              rows={4}
              {...register('observaciones')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
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
          {isSubmitting ? 'Guardando...' : isEditing ? 'Actualizar' : 'Registrar'}
        </button>
      </div>
    </form>
  );
};

export default CompraForm;