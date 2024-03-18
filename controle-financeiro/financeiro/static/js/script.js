function mostrarMensagem(msg, icon) {
    Swal.fire({
        title: msg,
        //text: 'Operação realizada com sucesso! SweetAlert!',
        icon: icon,
        confirmButtonText: 'OK'
    });
}

function marcarPaginaSelecionada(){
    var urlAtual = window.location.pathname;
    var classeEspecifica = 'aselect';
    var elementosAntigos = document.querySelectorAll('.' + classeEspecifica);
    elementosAntigos.forEach(function(elementoAntigo) {
        elementoAntigo.classList.remove(classeEspecifica);
    });

    var paginas = {
        '/home/': 'nav1',
        '/origens/': 'nav2',
        '/categorias/': 'nav3',
        '/orcamentos/': 'nav4',
        '/rel-orctos/': 'nav5',
        '/lancamentos/': 'nav6',
        '/rel-lctos/': 'nav7',
        '/orc_real/': 'nav8',

    }
    
    for (var pagina in paginas){
        if (urlAtual.indexOf(pagina) !== -1) {
            var elementoNovo = document.getElementById(paginas[pagina]);
            if (elementoNovo) {
                elementoNovo.classList.add(classeEspecifica);
            }
            break
        }
    }    
}