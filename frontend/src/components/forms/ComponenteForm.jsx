import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { Upload, X } from 'lucide-react';
import { componentesService } from '@/services/componentesService';
import { CATEGORIAS_COMPONENTES } from '@/utils/constants';

const ComponenteForm = ({ componente = null, onSuccess, onCancel }) => {
  const [uploading, setUploading] = useState(false);
  const [imagePreview, setImagePreview] = useState(componente?.foto || null);
  const isEditing = !!componente;

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm({
    defaultValues: {
      nombre: componente?.nombre || '',
      descripcion: componente?.descripcion || '',
      numero_parte: componente?.numero_parte || '',
      categoria: componente?.categoria || '',
      precio_unitario: componente?.precio_unitario || '',
      stock_minimo: componente?.stock_minimo || 0
    }
  });

  const handleImageChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validar tipo de archivo
    if (!file.type.startsWith('image/')) {
      toast.error('Por favor selecciona una imagen válida');
      return;
    }

    // Validar tamaño (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('La imagen debe ser menor a 5MB');
      return;
    }

    // Preview local
    const reader = new FileReader();
    reader.onload = (e) => setImagePreview(e.target.result);
    reader.readAsDataURL(file);

    // Subir si estamos editando
    if (isEditing) {
      try {
        setUploading(true);
        await componentesService.uploadPhoto(componente.id, file);
        toast.success('Imagen actualizada correctamente');
      } catch (error) {
        toast.error('Error al subir la imagen');
        setImagePreview(componente?.foto || null);
      } finally {
        setUploading(false);
      }
    }
  };

  const onSubmit = async (data) => {
    try {
      const formData = {
        ...data,
        precio_unitario: parseFloat(data.precio_unitario) || 0,
        stock_minimo: parseInt(data.stock_minimo) || 0
      };

      if (isEditing) {
        await componentesService.update(componente.id, formData);
        toast.success('Componente actualizado correctamente');
      } else {
        const newComponente = await componentesService.create(formData);
        
        // Subir imagen si se seleccionó una
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput?.files[0]) {
          await componentesService.uploadPhoto(newComponente.id, fileInput.files[0]);
        }
        
        toast.success('Componente creado correctamente');
        reset();
        setImagePreview(null);
      }

      onSuccess?.();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Error al guardar el componente');
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
              Número de Parte
            </label>
            <input
              type="text"
              {...register('numero_parte')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Categoría
            </label>
            <select
              {...register('categoria')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Seleccionar categoría</option>
              {CATEGORIAS_COMPONENTES.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Descripción
            </label>
            <textarea
              rows={3}
              {...register('descripcion')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>
        </div>

        {/* Imagen y datos numéricos */}
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
                    className="max-h-48 mx-auto rounded"
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

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Precio Unitario
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                {...register('precio_unitario')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Stock Mínimo
              </label>
              <input
                type="number"
                min="0"
                {...register('stock_minimo')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
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

export default ComponenteForm;