export function login() {
    createModal();
    $("#myModal").on('hidden.bs.modal', () => window.location = "/");
}

function createModal() { $("#myModal").modal(); }
