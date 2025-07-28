import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { stockService } from '@/services/stockService';
import { componentesService } from '@/services/componentesService';
import { TIPOS_MOVIMIENTO } from '@/config';

const MovimientoStockForm = ({ onSuccess, onCancel }) => {
  const [componentes, setComponentes] = useState([]);
  const [componenteSeleccionado, setComponenteSeleccionado] = useState(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
    setValue
  } = useForm({
    defaultValues: {
      componente_id: '',
      tipo_movimiento: 'entrada',
      cantidad: 1,
      motivo: '',
      observaciones: '',
      usuario: 'Sistema'
    }
  });

  const tipoMovimiento = watch('tipo_movimiento');
  const componenteId = watch('componente_id');

  useEffect(() => {
    const fetchComponentes = async () => {
      try {
        const data = await componentesService.getAll({ activo: true });
        setComponentes(data);
      } catch (error) {
        toast.error('Error al cargar los componentes');
      }
    };

    fetchComponentes();
  }, []);

  useEffect(() => {
    if (componenteId) {
      const componente = componentes.find(c => c.id === parseInt(componenteId));
      setComponenteSeleccionado(componente);
    } else {
      setComponenteSeleccionado(null);
    }
  }, [componenteId, componentes]);

  const onSubmit = async (data) => {
    try {
      const formData = {
        ...data,
        componente_id: parseInt(data.componente_id),
        cantidad: parseInt(data.cantidad)
      };

      await stockService.registrarMovimiento(formData);
      toast.success('Movimiento registrado exitosamente');
      onSuccess?.();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Error al registrar el movimiento');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">
          Componente *
        </label>
        <select
          {...register('componente_id', { required: 'El componente es requerido' })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
        >
          <option value="">Seleccionar componente</option>
          {componentes.map((componente) => (
            <option key={componente.id} value={componente.id}>
              {componente.nombre} - {componente.numero_parte} (Stock: {componente.stock_actual})
            </option>
          ))}
        </select>
        {errors.componente_id && (
          <p className="mt-1 text-sm text-red-600">{errors.componente_id.message}</p>
        )}
      </div>

      {componenteSeleccionado && (
        <div className="bg-gray-50 p-3 rounded-md">
          <p className="text-sm text-gray-600">
            <strong>Stock actual:</strong> {componenteSeleccionado.stock_actual} unidades
          </p>
          <p className="text-sm text-gray-600">
            <strong>Stock mínimo:</strong> {componenteSeleccionado.stock_minimo} unidades
          </p>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Tipo de Movimiento *
        </label>
        <select
          {...register('tipo_movimiento', { required: 'El tipo de movimiento es requerido' })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
        >
          <option value={TIPOS_MOVIMIENTO.ENTRADA}>Entrada</option>
          <option value={TIPOS_MOVIMIENTO.SALIDA}>Salida</option>
          <option value={TIPOS_MOVIMIENTO.AJUSTE}>Ajuste</option>
        </select>
        {errors.tipo_movimiento && (
          <p className="mt-1 text-sm text-red-600">{errors.tipo_movimiento.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          {tipoMovimiento === 'ajuste' ? 'Nueva Cantidad *' : 'Cantidad *'}
        </label>
        <input
          type="number"
          min={tipoMovimiento === 'ajuste' ? '0' : '1'}
          {...register('cantidad', { 
            required: 'La cantidad es requerida',
            min: {
              value: tipoMovimiento === 'ajuste' ? 0 : 1,
              message: `La cantidad mínima es ${tipoMovimiento === 'ajuste' ? 0 : 1}`
            }
          })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
        />
        {errors.cantidad && (
          <p className="mt-1 text-sm text-red-600">{errors.cantidad.message}</p>
        )}
        {tipoMovimiento === 'ajuste' && (
          <p className="mt-1 text-sm text-gray-500">
            Para ajustes, ingresa la cantidad final que debe quedar en stock
          </p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Motivo
        </label>
        <input
          type="text"
          placeholder="Ej: Compra, Uso en reparación, Inventario, etc."
          {...register('motivo')}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Observaciones
        </label>
        <textarea
          rows={3}
          {...register('observaciones')}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Usuario
        </label>
        <input
          type="text"
          {...register('usuario')}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
        />
      </div>

      {/* Botones */}
      <div className="flex justify-end space-x-3 pt-4">
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
          {isSubmitting ? 'Registrando...' : 'Registrar Movimiento'}
        </button>
      </div>
    </form>
  );
};

export default MovimientoStockForm;