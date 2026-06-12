const API_BASE_URL = '';

const token = localStorage.getItem('token_admin') || ""; 

async function request(endpoint, options = {}) {
    const headers = {
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };

    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    const config = {
        ...options,
        headers
    };

    const response = await fetch(endpoint, config);

    if (response.status === 401) {
        manejarSesionExpirada();
        throw new Error("Sesión expirada");
    }

    if (!response.ok) {
        throw new Error(`Error en la petición: ${response.statusText}`);
    }

    return response;
}

if (!token && window.location.pathname.includes('/admin/dashboard')) {
    window.location.href = '/login';
}

function manejarSesionExpirada() {
    alert("Tu sesión ha expirado o no tienes autorización. Inicia sesión nuevamente.");
    localStorage.removeItem('token_admin');
    window.location.href = '/login';
}


function cambiarPestana(pestana) {
    const secciones = ['panel', 'productos', 'maquinas', 'sugerencias', 'calificaciones'];
    
    secciones.forEach(sec => {
        const elemento = document.getElementById(`contenido-${sec}`);
        const boton = document.getElementById(`sidebar-${sec}`);
        
        if (elemento) {
            if (sec === pestana) {
                elemento.classList.remove('hidden');
            } else {
                elemento.classList.add('hidden');
            }
        }
        
        if (boton) {
            if (sec === pestana) {
                boton.classList.add('bg-gray-800', 'text-white');
                boton.classList.remove('text-gray-400', 'hover:bg-gray-800/50');
            } else {
                boton.classList.remove('bg-gray-800', 'text-white');
                boton.classList.add('text-gray-400', 'hover:bg-gray-800/50');
            }
        }
    });

    // 2. Actualizar encabezados
    const titulos = {
        'panel': { t: 'Panel de Control Global', s: 'Resumen analítico del estado del negocio' },
        'productos': { t: 'Catálogo de Productos', s: 'Gestión de artículos y precios base para códigos QR' },
        'maquinas': { t: 'Unidades Dispendedoras', s: 'Control de inventarios por punto de venta físico' },
        'sugerencias': { t: 'Sugerencias de Clientes', s: 'Análisis de demanda para nuevos artículos solicitados' },
        'calificaciones': { t: 'Historial de Calificaciones', s: 'Monitoreo de satisfacción y feedback directo' }
    };

    if (titulos[pestana]) {
        document.getElementById('titulo-vista').innerText = titulos[pestana].t;
        document.getElementById('subtitulo-vista').innerText = titulos[pestana].s;
    }

    switch(pestana) {
        case 'productos': 
            cargarProductos(); 
            break;
        case 'maquinas': 
            cargarMaquinas(); 
            break;
        case 'sugerencias': 
            cargarSugerencias(); 
            break;
        case 'calificaciones': 
            cargarCalificaciones(); 
            break;
        case 'panel':
            cargarMetricasDashboard();
            break;
    }
}

async function cargarMetricasDashboard() {
    try {
        const response = await fetch('/admin/dashboard/metricas', {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.status === 401) return manejarSesionExpirada();
        if (!response.ok) throw new Error("Error al obtener métricas");

        const data = await response.json();

        document.getElementById('metrica-productos').innerText = data.total_productos;
        document.getElementById('metrica-maquinas').innerText = data.total_maquinas;
        document.getElementById('metrica-sugerencias').innerText = data.total_sugerencias;
        document.getElementById('metrica-calificaciones').innerText = `${data.satisfaccion}%`;

    } catch (error) {
        console.error("❌ Error en métricas:", error);
    }
}

async function cargarProductos() {
    try {
        const response = await fetch('/admin/productos', {
            headers: { 
                'Authorization': `Bearer ${token}` 
            }
        });
        
        if (!response.ok) throw new Error("Error al obtener productos");
        
        const productos = await response.json();
        const tbody = document.getElementById('tabla-productos-body');
        
        if (!tbody) return;
        
        tbody.innerHTML = '';

        productos.forEach(p => {
            const imagenUrl = (p.imagenes && p.imagenes.length > 0) ? p.imagenes[0].ruta_imagen : null;

                tbody.innerHTML += `
                    <tr class="hover:bg-gray-800/30 transition text-sm text-gray-300" 
                        data-id="${p.id_producto}" 
                        data-nombre="${p.nombre}"> 
                        
                        <td class="px-6 py-4 font-medium text-white">${p.nombre}</td>
                        
                        <td class="px-6 py-4">
                            ${imagenUrl ? `<img src="${imagenUrl}" class="w-10 h-10 rounded-lg object-cover" alt="${p.nombre}">` : '<span class="text-gray-500">-</span>'}
                        </td>
                        
                        <td class="px-6 py-4 text-center"> <div class="flex justify-center gap-3"> <button onclick="editarProducto(${p.id_producto})" 
                                        class="text-amber-500 hover:text-amber-400 font-medium transition">
                                    Editar
                                </button>
                                <button onclick="eliminarProducto(${p.id_producto})" 
                                        class="text-red-500 hover:text-red-400 font-medium transition">
                                    Borrar
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
        });
    } catch (error) {
        console.error("❌ Error al cargar productos:", error);
    }
}

async function cargarMaquinas() {
    try {
        const response = await fetch('/admin/maquinas', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error("Error en máquinas");

        const maquinas = await response.json();
        const tbody = document.getElementById('tabla-maquinas-body');
        if (!tbody) return;

        tbody.innerHTML = '';

        maquinas.forEach(m => {
            const estadoActual = m.estado || 'Operativa';
            
            let colorBadge = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'; // Operativa por defecto
            let iconoEstado = '🟢';

            if (estadoActual === 'Mantenimiento') {
                colorBadge = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
                iconoEstado = '🟡';
            } else if (estadoActual === 'Fuera de Servicio') {
                colorBadge = 'bg-rose-500/10 text-rose-400 border-rose-500/20';
                iconoEstado = '🔴';
            }

            tbody.innerHTML += `
                <tr class="hover:bg-gray-800/30 transition text-sm text-gray-300">
                    <td class="px-6 py-4 font-medium text-white">${m.nombre}</td>
                    <td class="px-6 py-4">
                        <span class="px-2.5 py-1 rounded-full text-[11px] font-bold ${colorBadge} border">
                            ${iconoEstado} ${estadoActual}
                        </span>
                    </td>
                    <td class="px-6 py-4 text-center flex justify-center gap-3">
                        <button onclick="editarMaquina(${m.id_maquina}, '${m.nombre}', '${estadoActual}')" 
                                class="text-xs bg-amber-500/10 hover:bg-amber-500 text-amber-400 hover:text-slate-900 px-3 py-1.5 rounded-lg transition font-medium">
                            ✏️ Modificar
                        </button>
                        <button onclick="eliminarMaquina(${m.id_maquina})" class="text-xs bg-red-500/10 hover:bg-red-500 text-red-400 hover:text-white px-3 py-1.5 rounded-lg transition font-medium">🗑️ Desactivar</button>
                    </td>
                </tr>
            `;
        });
    } catch (error) {
        console.error("❌ Error al cargar máquinas:", error);
    }
}

async function cargarSugerencias() {
    try {
        const response = await fetch('/admin/reporte/sugerencias', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error("Error en reporte de sugerencias");

        const sugerencias = await response.json();
        const tbody = document.getElementById('tabla-sugerencias-body');
        if (!tbody) return;

        tbody.innerHTML = sugerencias.map(s => `
            <tr class="hover:bg-gray-800/30 transition text-sm text-gray-300">
                <td class="px-6 py-4 font-medium text-white">${s.producto}</td>
                <td class="px-6 py-4 text-center font-bold text-purple-400">${s.votos} peticiones</td>
                <td class="px-6 py-4 text-gray-400">
                    ${s.fecha_creacion ? new Date(s.fecha_creacion).toLocaleDateString() : 'N/A'}
                </td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error("❌ Error al cargar sugerencias:", error);
    }
}

async function cargarCalificaciones() {
    try {
        const response = await fetch('/admin/reporte/calificaciones', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error("Error en calificaciones");

        const calificaciones = await response.json();
        const tbody = document.getElementById('tabla-calificaciones-body');
        if (!tbody) return;

        tbody.innerHTML = '';

        calificaciones.forEach(c => {
            const origen = c.origen || "Desconocido";
            const producto = c.producto_nombre || "Sin producto";
            const estrellaVisual = c.voto; 
            const colorVoto = c.voto.includes('Satisfactorio') ? 'text-emerald-400' : 'text-red-400';
            const fechaFormateada = c.fecha ? c.fecha.split('T')[0] : 'Hoy';

            tbody.innerHTML += `
                <tr class="hover:bg-gray-800/30 transition text-sm text-gray-300">
                    <td class="px-6 py-4 font-mono">${c.origen}</td>
                    <td class="px-6 py-4 font-medium text-white">${c.producto_nombre}</td>
                    <td class="px-6 py-4 font-semibold ${colorVoto}">${estrellaVisual}</td>
                    <td class="px-6 py-4 text-gray-400">${fechaFormateada}</td>
                    <td class="px-6 py-4 text-center">
                        <button onclick="eliminarCalificacion(${c.id})" 
                                class="text-xs bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white px-2 py-1 rounded transition">
                            🗑️ Remover
                        </button>
                    </td>
                </tr>
            `;
        });
    } catch (error) {
        console.error("❌ Error al cargar calificaciones:", error);
    }
}

async function guardarProducto(e) {
    e.preventDefault();
    const formData = new FormData(e.target);

    formData.append('nombre', document.getElementById('prod-nombre').value);
    formData.append('file', document.getElementById('prod-imagen').files[0]);

    try {
        const response = await fetch('/admin/productos', {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}` 
            },
            body: formData
        });

        if (!response.ok) throw new Error("Error al guardar producto");
        
        e.target.reset(); 
        cerrarModalEditarProducto(); 

        await cargarProductos();
        await cargarMetricasDashboard();
    } catch (error) {
        alert("Error al registrar el producto.");
    }
}

function editarProducto(idProducto) {
    const fila = document.querySelector(`tr[data-id="${idProducto}"]`);
    if (!fila) return;

    const nombre = fila.getAttribute('data-nombre');

    const inputId = document.getElementById('edit-prod-id');
    const inputNombre = document.getElementById('edit-prod-nombre');

    if (inputId) inputId.value = idProducto;
    if (inputNombre) inputNombre.value = nombre;

    if (window.abrirModalEditarProducto) window.abrirModalEditarProducto();
}

function editarMaquina(id, nombre, estado) {
    document.getElementById('edit-maq-id').value = id;
    document.getElementById('edit-maq-nombre').value = nombre;
    const select = document.getElementById('edit-maq-estado');
    if (select) select.value = estado;
    
    document.getElementById('modal-editar-maquina').classList.remove('hidden');
}

document.getElementById('form-editar-producto').addEventListener('submit', async (e) => {
    e.preventDefault();
    const idProducto = document.getElementById('edit-prod-id').value;
    const nombre = document.getElementById('edit-prod-nombre').value;

    try {
        const response = await fetch(`/admin/productos/${idProducto}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ nombre: nombre })
        });

        if (response.status === 401) return manejarSesionExpirada();
        if (!response.ok) throw new Error("No se pudo actualizar el producto");

        if (window.cerrarModalEditarProducto) window.cerrarModalEditarProducto();
        await cargarProductos();
        await cargarMetricasDashboard();
        
    } catch (error) {
        console.error(error);
        alert("Ocurrió un error al actualizar el producto.");
    }
});


function abrirModalEditarMaquina(id, nombre, estado) {
    document.getElementById('edit-maq-id').value = id;
    document.getElementById('edit-maq-nombre').value = nombre;
    document.getElementById('edit-maq-estado').value = estado;
    window.abrirModalEditarMaquina();
}

    document.getElementById('form-editar-producto').addEventListener('submit', async (e) => {
        e.preventDefault();
        const idProducto = document.getElementById('edit-prod-id').value;
        const nombre = document.getElementById('edit-prod-nombre').value;

        try {
            const response = await fetch(`/admin/productos/${idProducto}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ nombre: nombre })
            });

            if (response.status === 401) return manejarSesionExpirada();
            if (!response.ok) throw new Error("No se pudo actualizar el producto");

            if (window.cerrarModalEditarProducto) window.cerrarModalEditarProducto();

            await cargarProductos();
            await cargarMetricasDashboard(); 
            
        } catch (error) {
            console.error(error);
            alert("Ocurrió un error al actualizar el producto.");
        }
});

function eliminarProducto(idProducto) {
    if (window.abrirModalConfirmar) {
        window.abrirModalConfirmar(
            `¿Estás seguro de que deseas eliminar el producto #${idProducto} del catálogo?`,
            async () => {
                try {
                    const response = await fetch(`/admin/productos/${idProducto}`, {
                        method: 'DELETE',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    if (response.status === 401) return manejarSesionExpirada();
                    if (!response.ok) throw new Error("Fallo al eliminar");
                    
                    await cargarProductos();
                    await cargarMetricasDashboard();
                } catch (error) {
                    alert("No se pudo eliminar el producto.");
                }
            }
        );
    }
}

async function guardarMaquina(e) {
    e.preventDefault();
    const nombre = document.getElementById('maq-nombre').value;

    try {
        const response = await fetch('/admin/maquinas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ nombre: nombre })
        });

        if (!response.ok) throw new Error();
        
        document.getElementById('form-maquina').reset();
        if (window.cerrarModalMaquina) window.cerrarModalMaquina();

        await cargarProductos();
        await cargarMetricasDashboard();

    } catch (error) {
        alert("Error al registrar máquina. Valida que el nombre no esté duplicado.");
    }
}

function editarMaquina(id, nombre, estado) {
    document.getElementById('edit-maq-id').value = id;
    document.getElementById('edit-maq-nombre').value = nombre;
    const select = document.getElementById('edit-maq-estado');
    if (select) select.value = estado;
    document.getElementById('modal-editar-maquina').classList.remove('hidden');
}

document.getElementById('form-editar-maquina').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('edit-maq-id').value;
    const nombre = document.getElementById('edit-maq-nombre').value;
    const estado = document.getElementById('edit-maq-estado').value;
    try {
        const response = await fetch(`/admin/maquinas/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ nombre, estado })
        });
        if (!response.ok) throw new Error();
        document.getElementById('modal-editar-maquina').classList.add('hidden');
        
        await cargarMaquinas();
    } catch (error) { alert("Error al actualizar máquina."); }
});

function eliminarMaquina(idMaquina) {
    if (window.abrirModalConfirmar) {
        window.abrirModalConfirmar(
            `¿Estás seguro de que deseas eliminar la máquina #${idMaquina}? Esto puede afectar registros vinculados.`,
            async () => {
                try {
                    const response = await fetch(`/admin/maquinas/${idMaquina}`, {
                        method: 'DELETE',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    if (!response.ok) throw new Error();
                    
                    await cargarMaquinas();
                    await cargarMetricasDashboard();

                } catch (error) {
                    alert("No se pudo eliminar la máquina.");
                }
            }
        );
    }
}

function eliminarCalificacion(idCalificacion) {
    if (window.abrirModalConfirmar) {
        window.abrirModalConfirmar(
            "¿Deseas remover de manera permanente este voto del registro histórico?",
            async () => {
                try {
                    const response = await fetch(`/admin/eliminar_calificacion/${idCalificacion}`, {
                        method: 'DELETE',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    if (response.status === 401) return manejarSesionExpirada();
                    if (!response.ok) throw new Error("No se pudo remover la calificación");

                    await cargarCalificaciones();
                    await cargarMetricasDashboard();

                } catch (error) {
                    console.error("❌ Error al eliminar calificación:", error);
                    alert("No se pudo eliminar la calificación.");
                }
            }
        );
    }
}

async function ejecutarCargaCompleta() {
    const loader = document.getElementById('loader-global');
    
    try {
        await cargarMetricasDashboard();
        
        if (loader) loader.classList.add('hidden');
        
        document.getElementById('form-producto').addEventListener('submit', guardarProducto);
        document.getElementById('form-maquina').addEventListener('submit', guardarMaquina);
        
        const inputBuscador = document.getElementById('buscador-productos');
        const btnBuscar = document.getElementById('btn-ejecutar-busqueda');
        
        if (inputBuscador) {
            inputBuscador.addEventListener('keypress', (e) => { if (e.key === 'Enter') ejecutarBusqueda(); });
        }
        if (btnBuscar) {
            btnBuscar.addEventListener('click', ejecutarBusqueda);
        }

    } catch (error) {
        console.error("❌ Error en carga inicial:", error);
    }
}

function ejecutarBusqueda() {
    const input = document.getElementById('buscador-productos');
    const valor = input.value.toLowerCase();

    const filas = document.querySelectorAll('#tabla-productos-body tr');
    const mensajeNoResultados = document.getElementById('mensaje-no-resultados')

    let encontrados = 0; 

    filas.forEach(fila => {
        const nombre = fila.getAttribute('data-nombre')?.toLowerCase() || "";

        if (nombre.includes(valor)) {
            fila.style.display = "";
            encontrados++; 
        } else {
            fila.style.display = "none"; 
        }
    }); 

    if (mensajeNoResultados) {
        if (encontrados === 0) {
            mensajeNoResultados.classList.remove('hidden');
        } else {
            mensajeNoResultados.classList.add('hidden'); 
        }
    }
}

const inputBusqueda = document.getElementById('buscador-productos'); 

if (inputBusqueda) {
    inputBusqueda.addEventListener('keypress', function (e){
        if (e.key === 'Enter') {
            ejecutarBusqueda();
        }
    });
}


function cargarNombreAdmin() {
    const token = localStorage.getItem('token_admin');
    if (!token) return;

    try {
        const payload = token.split('.')[1];
        const datos = JSON.parse(atob(payload));
        
        const nombreCompleto = datos.nombre || datos.sub || "Usuario";
        
        const elNombre = document.getElementById('nombre-admin');
        if (elNombre) elNombre.innerText = nombreCompleto;

        const elInicial = document.getElementById('inicial-usuario');
        if (elInicial) {
            const partes = nombreCompleto.split(' ');
            let iniciales = partes[0][0]; 
            
            if (partes.length > 1) {
                iniciales += partes[partes.length - 1][0];
            }
            
            elInicial.innerText = iniciales.toUpperCase();
        }
    } catch (e) {
        console.error("Error al procesar nombre del usuario:", e);
    }
} 

function actualizarInfoServidor(){
    const infoServidor = document.getElementById('info-servidor'); 
    if (infoServidor) {
        infoServidor.innerHTML = window.location.host; 
    }
}

document.addEventListener('DOMContentLoaded', () => {
    cargarNombreAdmin();
    ejecutarCargaCompleta(); 
    actualizarInfoServidor(); 
});