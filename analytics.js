/* Statistiche di visita — GoatCounter (gratuito, senza cookie)
 *
 * DA FARE UNA VOLTA SOLA: registrarsi su https://www.goatcounter.com,
 * scegliere un nome (es. "ctmwebbrowser") e scriverlo qui sotto al posto
 * di INSERIRE_CODICE. Finché resta così non viene caricato nulla.
 * Le visite si leggono su https://ctmbrowser.goatcounter.com
 */
(function () {
  var CODE = 'ctmbrowser';
  if (!CODE || CODE.indexOf('INSERIRE') === 0) return;
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://gc.zgo.at/count.js';
  s.setAttribute('data-goatcounter', 'https://' + CODE + '.goatcounter.com/count');
  document.head.appendChild(s);
})();
