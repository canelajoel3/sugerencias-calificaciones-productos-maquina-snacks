// Variable global para capturar el estado del voto (1 = Like, 0 = Dislike)
let votoSeleccionado = null;

document.addEventListener("DOMContentLoaded", () => {
    // 1. Obtener el ID de la máquina directamente desde el atributo de Jinja2 en el body
    const idMaquina = document.body.getAttribute("data-maquina-id") || 1;

    // 2. Capturar los elementos del DOM usando tus IDs reales del HTML
    const productSelect = document.getElementById("productSelect");
    const likeBtn = document.getElementById("likeBtn");
    const dislikeBtn = document.getElementById("dislikeBtn");
    const ratingForm = document.getElementById("ratingForm");
    const submitRatingBtn = document.getElementById("submitRating");
    
    // Elementos añadidos para la gestión de sugerencias
    const suggestionForm = document.getElementById("suggestionForm");
    const suggestionInput = document.getElementById("suggestion");
    
    const confirmationMsg = document.getElementById("confirmation");

    // 3. Cargar automáticamente los productos al entrar a la página
    cargarProductosCatalog(productSelect);

    
    if (suggestionForm) {
        suggestionForm.addEventListener("submit", async (e) => {
            e.preventDefault(); // Evita que la página se recargue por defecto

            const textoSugerencia = suggestionInput.value.trim();
            if (!textoSugerencia) {
                alert("Por favor, ingresa un nombre de producto válido.");
                return;
            }

            // Construir el cuerpo en base al EsquemaSugerenciaCreate de schemas
            const payloadSugerencia = {
                producto_sugerido: textoSugerencia
            };

            try {
                // Petición POST exacta a tu endpoint de cliente.py
                const response = await fetch(`http://127.0.0.1:8000/clientes/maquina/${idMaquina}/sugerir`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payloadSugerencia)
                });

                if (response.status === 201) {
                    // Mostrar mensaje de éxito en pantalla
                    if (confirmationMsg) {
                        confirmationMsg.textContent = "¡Sugerencia enviada con éxito!";
                        confirmationMsg.style.display = "block";
                        setTimeout(() => { confirmationMsg.style.display = "none"; }, 4000);
                    }

                    // Limpiar el campo de texto
                    suggestionForm.reset();
                } else {
                    const errData = await response.json();
                    alert(`Error del servidor: ${errData.detail}`);
                }
            } catch (error) {
                console.error("Error al enviar sugerencia:", error);
                alert("No se pudo conectar con el servidor para registrar la sugerencia.");
            }
        });
    }

    
    if (likeBtn && dislikeBtn) {
        likeBtn.addEventListener("click", () => {
            votoSeleccionado = 1; // Formato requerido por tu FastAPI (1 = Like)
            likeBtn.classList.add("active"); 
            likeBtn.style.backgroundColor = "rgba(16, 185, 129, 0.2)"; // Color esmeralda suave
            likeBtn.style.borderColor = "#10b981";
            
            // Resetear el de dislike
            dislikeBtn.classList.remove("active");
            dislikeBtn.style.backgroundColor = "";
            dislikeBtn.style.borderColor = "";

            // Habilitar el botón de enviar
            if (submitRatingBtn) submitRatingBtn.disabled = false;
        });

        dislikeBtn.addEventListener("click", () => {
            votoSeleccionado = 0; // Formato requerido por tu FastAPI (0 = Dislike)
            dislikeBtn.classList.add("active");
            dislikeBtn.style.backgroundColor = "rgba(244, 63, 94, 0.2)"; // Color rosa/rojo suave
            dislikeBtn.style.borderColor = "#f43f5e";
            
            // Resetear el de like
            likeBtn.classList.remove("active");
            likeBtn.style.backgroundColor = "";
            likeBtn.style.borderColor = "";

            // Habilitar el botón de enviar
            if (submitRatingBtn) submitRatingBtn.disabled = false;
        });
    }

    if (ratingForm) {
        ratingForm.addEventListener("submit", async (e) => {
            e.preventDefault(); 

            if (!productSelect.value) {
                alert("Por favor, selecciona un producto válido.");
                return;
            }

            if (votoSeleccionado === null) {
                alert("Por favor, selecciona una calificación (👍 o 👎).");
                return;
            }

            const payload = {
                id_producto: parseInt(productSelect.value),
                voto: votoSeleccionado
            };

            try {
                const response = await fetch(`http://127.0.0.1:8000/clientes/maquina/${idMaquina}/calificar`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (response.status === 201) {
                    if (confirmationMsg) {
                        confirmationMsg.textContent = "¡Gracias por tu retroalimentación!";
                        confirmationMsg.style.display = "block";
                        setTimeout(() => { confirmationMsg.style.display = "none"; }, 4000);
                    }

                    // Resetear el formulario de calificaciones
                    votoSeleccionado = null;
                    ratingForm.reset();
                    if (submitRatingBtn) submitRatingBtn.disabled = true;
                    likeBtn.style.backgroundColor = ""; likeBtn.style.borderColor = "";
                    dislikeBtn.style.backgroundColor = ""; dislikeBtn.style.borderColor = "";
                } else {
                    const errData = await response.json();
                    alert(`Error: ${errData.detail}`);
                }
            } catch (error) {
                console.error("Error en la petición:", error);
                alert("No se pudo conectar con el servidor central.");
            }
        });
    }
});


async function cargarProductosCatalog() {
    // 1. Obtener el ID de la máquina desde el atributo del body
    const idMaquina = document.body.getAttribute("data-maquina-id");

    if (!idMaquina) {
        console.error("No se pudo obtener el ID de la máquina");
        return;
    }

    try {
        // 2. Corregimos la ruta: debe incluir '/clientes' y terminar en '/productos'
        // para que coincida con tu ruta de FastAPI
        const response = await fetch(`/clientes/maquina/${idMaquina}/productos`);
        
        if (!response.ok) throw new Error("Error al cargar el catálogo");

        const productos = await response.json();
        const select = document.getElementById('productSelect');
        
        // 3. Limpiamos y llenamos
        select.innerHTML = '<option value="" disabled selected>Selecciona un producto</option>';
        
        productos.forEach(p => {
            // Asegúrate de que el objeto productos contenga 'id_producto' y 'nombre'
            select.innerHTML += `<option value="${p.id_producto}">${p.nombre}</option>`;
        });
    } catch (error) {
        console.error("Error al cargar productos:", error);
        document.getElementById('productSelect').innerHTML = 
            '<option value="">Error al cargar catálogo</option>';
    }
}