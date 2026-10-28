// 1. Define the variable globally
let personaIdSeleccionada = null;

// 2. Define the function and attach it explicitly to 'window'
// This ensures the HTML onclick="..." can find it.
window.confirmarContrato = function(id, nombre, costo) {
    console.log("Abriendo modal para:", nombre); // For debugging

    // Save ID
    personaIdSeleccionada = id;

    // Update Text
    // Note: In your HTML you used 'modal-coste' (ending in e)
    const nombreEl = document.getElementById('modal-nombre-persona');
    const costeEl = document.getElementById('modal-coste');

    if (nombreEl) nombreEl.textContent = nombre;
    if (costeEl) costeEl.textContent = costo; // You can add format logic here if needed

    // Show Modal
    // We create a new Bootstrap Modal instance from the ID
    const modalElement = document.getElementById('modalConfirmacion');
    if (modalElement) {
        const myModal = new bootstrap.Modal(modalElement);
        myModal.show();
    } else {
        console.error("No se encontró el modal con id 'modalConfirmacion'");
    }
};

// 3. Set up the final confirmation button listener
// We use DOMContentLoaded to make sure the HTML exists before looking for the button
document.addEventListener('DOMContentLoaded', function() {

    const btnConfirmarFinal = document.getElementById('btn-confirmar-final');

    if (btnConfirmarFinal) {
        btnConfirmarFinal.addEventListener('click', function() {
            if (personaIdSeleccionada) {
                console.log("Enviando formulario para ID:", personaIdSeleccionada);

                // Find the specific form for this person
                const form = document.getElementById('form-hire-' + personaIdSeleccionada);
                if (form) {
                    form.submit();
                } else {
                    console.error("No se encontró el formulario form-hire-" + personaIdSeleccionada);
                }
            }
        });
    }
});