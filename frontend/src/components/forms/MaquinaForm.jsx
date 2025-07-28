import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { Upload, X } from 'lucide-react';
import { maquinasService } from '@/services/maquinasService';
import { ESTADOS } from '@/config';

const TIPOS_MAQUINA = [
  'Tractor',
  'Cosechadora',
  'Implemento',
  'Pulverizadora',
  'Sembradora',
  'Arado',
  'Rastra',
  'Camión',
  'Pickup',
  'Otro'
];

const MaquinaForm = ({ maquina = null, onSuccess, onCancel }) => {
  const [uploading, setUploading] = useState(false);
  const [imagePreview, setImagePreview] = useState(maquina?.foto || null);
  const isEditing = !!maquina;

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm({
    defaultValues: {
      nombre: maquina?.nombre || '',
      marca: maquina?.marca || '',
      modelo: maquina?.modelo || '',
      numero_serie: maquina?.numero_serie || '',
      año: maquina?.año || new Date().getFullYear(),
      tipo: maquina?.tipo || '',
      estado: maquina?.estado || 'operativo',
      horas_trabajo: maquina?.horas_trabajo || 0,
      ubicacion: maquina?.ubicacion || '',
      observaciones: maquina?.observaciones || ''
    }
  });

  const handleImageChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast.error('Por favor selecciona una imagen válida');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      toast.error('La imagen debe ser menor a 5MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => setImagePreview(e.target.result);
    reader.readAsDataURL(file);

    if (isEditing) {
      try {
        setUploading(true);
        await maquinasService.uploadPhoto(maquina.id, file);
        toast.success('Imagen actualizada correctamente');
      } catch (error) {
        toast.error('Error al subir la imagen');
        setImagePreview(maquina?.foto || null);
      } finally {
        setUploading(false);
      }
    }
  };

  const onSubmit = async (data) => {
    try {
      const formData = {
        ...data,
        año: parseInt(data.año) || null,
        horas_trabajo: parseFloat(data.horas_trabajo) || 0
      };

      if (isEditing) {
        await maquinasService.update(maquina.id, formData);
        toast.success('Máquina actualizada correctamente');
      } else {
        const newMaquina = await maquinasService.create(formData);
        
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput?.files[0]) {
          await maquinasService.uploadPhoto(newMaquina.id, fileInput.files[0]);
        }
        
        toast.success('Máquina creada correctamente');
        reset();
        setImagePreview(null);
      }

      onSuccess?.();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Error al guardar la máquina');
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

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Marca
              </label>
              <input
                type="text"
                {...register('marca')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Modelo
              </label>
              <input
                type="text"
                {...register('modelo')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Número de Serie
            </label>
            <input
              type="text"
              {...register('numero_serie')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Año
              </label>
              <input
                type="number"
                min="1900"
                max={new Date().getFullYear() + 1}
                {...register('año')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Horas de Trabajo
              </label>
              <input
                type="number"
                min="0"
                step="0.1"
                {...register('horas_trabajo')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Tipo
              </label>
              <select
                {...register('tipo')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              >
                <option value="">Seleccionar tipo</option>
                {TIPOS_MAQUINA.map((tipo) => (
                  <option key={tipo} value={tipo}>{tipo}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Estado
              </label>
              <select
                {...register('estado')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              >
                <option value={ESTADOS.MAQUINA.OPERATIVO}>Operativo</option>
                <option value={ESTADOS.MAQUINA.MANTENIMIENTO}>Mantenimiento</option>
                <option value={ESTADOS.MAQUINA.FUERA_SERVICIO}>Fuera de Servicio</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Ubicación
            </label>
            <input
              type="text"
              {...register('ubicacion')}
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
        </div>

        {/* Imagen */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Imagen
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
              {imagePreview ? (
                <div className="relative">
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="max-h-64 mx-auto rounded"
                  />
                  <button
                    type="button"
                    onClick={() => setImagePreview(null)}
                    className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ) : (
                <div className="text-center">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-600">
                    Selecciona una imagen
                  </p>
                </div>
              )}
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="mt-2 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
                disabled={uploading}
              />
            </div>
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
          disabled={isSubmitting || uploading}
          className="px-4 py-2 bg-green-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
        >
          {isSubmitting ? 'Guardando...' : isEditing ? 'Actualizar' : 'Crear'}
        </button>
      </div>
    </form>
  );
};

export default MaquinaForm;