window.showPopup = function(message, timeout = 8000) {
    const popup = document.getElementById('popup-alert');
    const popupMessage = document.getElementById('popup-alert-message');
    
    popupMessage.textContent = message;  // Asigna el mensaje al popup
    
    // Muestra el popup
    popup.classList.remove('hide');
    popup.classList.add('show');
    
    // Después de 3 segundos, lo oculta
    setTimeout(() => {
        popup.classList.add('hide');
        popup.classList.remove('show');
    }, timeout);  // El pop-up desaparecerá después de 3 segundos
}