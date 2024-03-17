function mostrarMensagem(msg) {
    Swal.fire({
        title: msg,
        //text: 'Operação realizada com sucesso! SweetAlert!',
        icon: 'success',
        confirmButtonText: 'OK'
    });
}