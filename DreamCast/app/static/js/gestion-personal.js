let personaIdDespido = null;

window.confirmarDespido = function(id, nombre, valorBase, penalizacion, total) {

    personaIdDespido = id;

    const nombreEl = document.getElementById('modal-nombre-despido');
    if (nombreEl) {
        nombreEl.textContent = nombre;
    }

    const fmt = (num) => new Intl.NumberFormat('es-ES').format(num);

    const baseEl = document.getElementById('modal-valor-base');
    if (baseEl) {
        baseEl.textContent = fmt(valorBase);
    }

    const penaEl = document.getElementById('modal-penalizacion');
    if (penaEl) {
        penaEl.textContent = fmt(penalizacion);
    }

    const totalEl = document.getElementById('modal-total');
    if (totalEl) {
        totalEl.textContent = fmt(total);
    }

    const modalElement = document.getElementById('modalDespido');
    if (modalElement && window.bootstrap) {
        const myModal = new window.bootstrap.Modal(modalElement);
        myModal.show();
    } else {
        console.error("Bootstrap modal instance not found or bootstrap library missing.");
    }
};

// 6. Event Listener for the Final "Confirmar y Cobrar" button
document.addEventListener('DOMContentLoaded', function() {

    const btnConfirmar = document.getElementById('btn-confirmar-despido');

    if (btnConfirmar) {
        btnConfirmar.addEventListener('click', function() {
            if (personaIdDespido) {
                console.log("Submitting form for ID:", personaIdDespido);

                // Find the specific form for this person
                const form = document.getElementById('form-fire-' + personaIdDespido);
                if (form) {
                    form.submit();
                } else {
                    console.error("Form not found for ID:", personaIdDespido);
                }
            }
        });
    }
});