class EventListenerManager {
    constructor() {
        this.listeners = [];
    }

    addEventListener(element, type, listener, options) {
        element.addEventListener(type, listener, options);
        this.listeners.push({ element, type, listener, options });
    }

    removeAllEventListeners() {
        for (const { element, type, listener, options } of this.listeners) {
            element.removeEventListener(type, listener, options);
        }
        this.listeners = [];
    }
}

export default EventListenerManager;