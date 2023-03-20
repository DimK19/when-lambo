/* global bootstrap: false */
(function () {
  'use strict'
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    new bootstrap.Tooltip(tooltipTriggerEl)
  })
})()


// does not work because the page is reloaded
/*
let w = Document.getElementById('wallet');
w.addEventListener('click', (e) => {
    h.classList.remove('active');
    w.classList.add('active');
});
*/
