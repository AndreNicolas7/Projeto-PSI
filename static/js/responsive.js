function aplicarResponsividade() {
    const largura = window.innerWidth;
    const body = document.body;

    body.classList.remove("mobile", "tablet", "desktop");

    if (largura <= 600) {
        body.classList.add("mobile");
    } else if (largura <= 1024) {
        body.classList.add("tablet");
    } else {
        body.classList.add("desktop");
    }
}

aplicarResponsividade();

window.addEventListener("resize", aplicarResponsividade);