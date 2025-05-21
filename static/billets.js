function printBillet(id) {
  const billet = document.getElementById(id);
  const originalContents = document.body.innerHTML;
  const printContents = billet.outerHTML;

  document.body.innerHTML = printContents;
  window.print();
  document.body.innerHTML = originalContents;

  // Recharger la page pour restaurer les barcodes
  location.reload();
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".barcode").forEach(svg => {
    const code = svg.dataset.code;
    if (code) {
      JsBarcode(svg, code, {
        format: "CODE128",
        lineColor: "#000",
        width: 2,
        height: 60,
        displayValue: true
      });
    }
  });
});
