import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { Upload, X } from 'lucide-react';
import { componentesService } from '@/services/componentesService';
import { CATEGORIAS_COMPONENTES } from '@/utils/constants';

const ComponenteForm = ({ componente = null, onSuccess, onCancel }) => {
  const [uploading, setUploading] = useState(false);
  const [imagePreview, setImagePreview] = useState(null); // ✅ Solo para preview local
  const [uploadedImage, setUploadedImage] = useState(componente?.foto || null); // ✅ Para imagen del servidor
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState('');
  const [subcategoriaSeleccionada, setSubcategoriaSeleccionada] = useState('');
  const isEditing = !!componente;

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    setValue,
    watch
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

  // ✅ Inicializar categorías si estamos editando
  React.useEffect(() => {
    if (componente?.categoria) {
      // Buscar la categoría principal que contiene la subcategoría
      const categoriaEncontrada = CATEGORIAS_COMPONENTES.find(cat => 
        cat.subcategorias.includes(componente.categoria)
      );
      
      if (categoriaEncontrada) {
        setCategoriaSeleccionada(categoriaEncontrada.categoria);
        setSubcategoriaSeleccionada(componente.categoria);
      }
    }
  }, [componente]);

  // ✅ Obtener subcategorías disponibles
  const subcategoriasDisponibles = CATEGORIAS_COMPONENTES.find(
    c => c.categoria === categoriaSeleccionada
  )?.subcategorias || [];

  // ✅ Manejar cambio de categoría principal
  const handleCategoriaChange = (categoria) => {
    setCategoriaSeleccionada(categoria);
    setSubcategoriaSeleccionada(''); // Reset subcategoría
    setValue('categoria', ''); // Reset valor del formulario
  };

  // ✅ Manejar cambio de subcategoría
  const handleSubcategoriaChange = (subcategoria) => {
    setSubcategoriaSeleccionada(subcategoria);
    setValue('categoria', subcategoria); // Guardar subcategoría como categoría final
  };

  // ✅ Helper para URLs de imagen - usar la misma ruta que el listado
  const getImageUrl = (filename) => {
    if (!filename) return null;
    if (filename.startsWith('blob:') || filename.startsWith('data:')) return filename;
    
    // ✅ Usar la ruta que funciona en el listado (sin subdirectorio)
    return `/static/fotos/${filename}`;
  };

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
        const response = await componentesService.uploadPhoto(componente.id, file);
        
        console.log('📸 Respuesta completa del upload:', response);
        
        // ✅ Manejo robusto de la respuesta
        const fotoFilename = response?.data?.foto || response?.foto || `componente_${componente.id}.jpg`;
        setUploadedImage(fotoFilename);
        setImagePreview(null); // Limpiar preview local
        toast.success('Imagen actualizada correctamente');
      } catch (error) {
        console.error('Error al subir imagen:', error);
        console.error('Response details:', error.response);
        toast.error('Error al subir la imagen');
        setImagePreview(null);
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
        setUploadedImage(null);
      }

      onSuccess?.();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Error al guardar el componente');
    }
  };

  // ✅ Determinar qué imagen mostrar
  const currentImage = imagePreview || uploadedImage;

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
              Categoría Principal
            </label>
            <select
              value={categoriaSeleccionada}
              onChange={(e) => handleCategoriaChange(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Seleccionar categoría principal</option>
              {CATEGORIAS_COMPONENTES.map((cat) => (
                <option key={cat.categoria} value={cat.categoria}>
                  {cat.categoria}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Subcategoría
            </label>
            <select
              value={subcategoriaSeleccionada}
              onChange={(e) => handleSubcategoriaChange(e.target.value)}
              disabled={!categoriaSeleccionada}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="">
                {categoriaSeleccionada ? 'Seleccionar subcategoría' : 'Selecciona primero una categoría principal'}
              </option>
              {subcategoriasDisponibles.map((sub) => (
                <option key={sub} value={sub}>
                  {sub}
                </option>
              ))}
            </select>
            {subcategoriaSeleccionada && (
              <p className="mt-1 text-sm text-green-600">
                Categoría seleccionada: {categoriaSeleccionada} → {subcategoriaSeleccionada}
              </p>
            )}
            {/* Campo oculto para el formulario */}
            <input
              type="hidden"
              {...register('categoria')}
              value={subcategoriaSeleccionada}
            />
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
              {currentImage ? (
                <div className="relative">
                  <img
                    src={imagePreview || getImageUrl(uploadedImage)}
                    alt="Preview"
                    className="max-h-48 mx-auto rounded"
                    onError={(e) => {
                      console.error('Error cargando imagen:', e.target.src);
                      // ✅ Mostrar placeholder en lugar de ocultar
                      e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik03NSA5MEM3NSA4Ni4xMzQgNzguMTM0IDgzIDgyIDgzSDExOEM5My44NjYgODMgOTcgODYuMTM0IDk3IDkwVjExMEM5NyAxMTMuODY2IDkzLjg2NiAxMTcgOTAgMTE3SDgyQzc4LjEzNCAxMTcgNzUgMTEzLjg2NiA3NSAxMTBWOTBaIiBzdHJva2U9IiM5Q0EzQUYiIHN0cm9rZS13aWR0aD0iMiIvPgo8cGF0aCBkPSJNMTM1IDkwQzEzNSA4Ni4xMzQgMTM4LjEzNCA4MyAxNDIgODNIMTU4QzE2MS44NjYgODMgMTY1IDg2LjEzNCAxNjUgOTBWMTEwQzE2NSAxMTMuODY2IDE2MS44NjYgMTE3IDE1OCAxMTdIMTQyQzEzOC4xMzQgMTE3IDEzNSAxMTMuODY2IDEzNSAxMTBWOTBaIiBzdHJva2U9IiM5Q0EzQUYiIHN0cm9rZS13aWR0aD0iMiIvPgo8L3N2Zz4K';
                      e.target.alt = 'Imagen no disponible';
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setImagePreview(null);
                      if (!isEditing) setUploadedImage(null);
                    }}
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
              {uploading && (
                <p className="mt-1 text-sm text-blue-600">Subiendo imagen...</p>
              )}
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