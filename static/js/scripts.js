//inicio de animaciones
AOS.init();


//inicializar carrusel
document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('.carousel');
    var instances = M.Carousel.init(elems, options);
});



var options = {
    indicator: true,
    numVisible: 5,
    padding: 200
};

document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('.collapsible');
    var instances = M.Collapsible.init(elems, options);
});