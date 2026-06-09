
let votoSeleccionado = null;

document.addEventListener("DOMContentLoaded", () => {
    const idMaquina = document.body.getAttribute("data-maquina-id") || 1;

    const productSelect = document.getElementById("productSelect");
    const likeBtn = document.getElementById("likeBtn");
    const dislikeBtn = document.getElementById("dislikeBtn");
    const ratingForm = document.getElementById("ratingForm");
    const submitRatingBtn = document.getElementById("submitRating");
    
    const suggestionForm = document.getElementById("suggestionForm");
    const suggestionInput = document.getElementById("suggestion");
    
    const confirmationMsg = document.getElementById("confirmation");

    
    cargarProductosCatalog(productSelect);

    
    if (suggestionForm) {
        suggestionForm.addEventListener("submit", async (e) => {
            e.preventDefault(); 

            const textoSugerencia = suggestionInput.value.trim();
            if (!textoSugerencia) {
                alert("Por favor, ingresa un nombre de producto válido.");
                return;
            }

            const payloadSugerencia = {
                producto_sugerido: textoSugerencia
            };

            try {
                const response = await fetch(`/clientes/maquina/${idMaquina}/sugerir`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payloadSugerencia)
                });

                if (response.status === 201) {
                    if (confirmationMsg) {
                        confirmationMsg.textContent = "¡Sugerencia enviada con éxito!";
                        confirmationMsg.style.display = "block";
                        setTimeout(() => { confirmationMsg.style.display = "none"; }, 4000);
                    }

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
            votoSeleccionado = 1; 
            likeBtn.classList.add("active"); 
            likeBtn.style.backgroundColor = "rgba(16, 185, 129, 0.2)";
            likeBtn.style.borderColor = "#10b981";
            
            dislikeBtn.classList.remove("active");
            dislikeBtn.style.backgroundColor = "";
            dislikeBtn.style.borderColor = "";

            if (submitRatingBtn) submitRatingBtn.disabled = false;
        });

        dislikeBtn.addEventListener("click", () => {
            votoSeleccionado = 0; 
            dislikeBtn.classList.add("active");
            dislikeBtn.style.backgroundColor = "rgba(244, 63, 94, 0.2)"; 
            dislikeBtn.style.borderColor = "#f43f5e";
            
            likeBtn.classList.remove("active");
            likeBtn.style.backgroundColor = "";
            likeBtn.style.borderColor = "";

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
                const response = await fetch(`/clientes/maquina/${idMaquina}/calificar`, {
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
    const idMaquina = document.body.getAttribute("data-maquina-id");

    if (!idMaquina) {
        console.error("No se pudo obtener el ID de la máquina");
        return;
    }

    try {
        const response = await fetch(`/clientes/maquina/${idMaquina}/productos`);
        
        if (!response.ok) throw new Error("Error al cargar el catálogo");

        const productos = await response.json();
        const select = document.getElementById('productSelect');
        
        select.innerHTML = '<option value="" disabled selected>Selecciona un producto</option>';
        
        productos.forEach(p => {
            select.innerHTML += `<option value="${p.id_producto}">${p.nombre}</option>`;
        });
    } catch (error) {
        console.error("Error al cargar productos:", error);
        document.getElementById('productSelect').innerHTML = 
            '<option value="">Error al cargar catálogo</option>';
    }
}