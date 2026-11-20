// Lógica pura: sin DOM ni red, para poder testearla aparte (tests.html).

// Tasa efectiva mensual de un plazo fijo a 30 días a partir de su TNA.
function temDesdeTna(tna) {
  return (tna * 30) / 365;
}

// Valor, en pesos de hoy, de pagar `precio × (1 + recargo)` en n cuotas iguales.
// La primera cuota se paga en el próximo resumen, dentro de un mes.
function valorPresenteCuotas(precio, n, tasaMensual, recargo = 0) {
  if (!(precio > 0) || !(n >= 1) || !Number.isInteger(n)) return NaN;
  if (!(tasaMensual > -1)) throw new RangeError("Tasa mensual inválida: " + tasaMensual);
  const cuota = (precio * (1 + recargo)) / n;
  let total = 0;
  for (let k = 1; k <= n; k++) total += cuota / (1 + tasaMensual) ** k;
  return total;
}

// Descuento por pago contado que deja empatadas las dos opciones.
// Si te ofrecen más que esto, conviene contado.
function descuentoQueEmpata(n, tasaMensual, recargo = 0) {
  return 1 - valorPresenteCuotas(1, n, tasaMensual, recargo);
}

function veredicto({ precio, descuento, n, tasaMensual, recargo = 0 }) {
  const contado = precio * (1 - descuento);
  const cuotas = valorPresenteCuotas(precio, n, tasaMensual, recargo);
  return {
    contado,
    cuotas,
    empate: descuentoQueEmpata(n, tasaMensual, recargo),
    conviene: Math.abs(contado - cuotas) < 0.005 * precio ? "empate" : contado < cuotas ? "contado" : "cuotas",
    ahorro: Math.abs(contado - cuotas),
  };
}

// Bancos que informan una TNA para clientes razonable (argentinadatos.com).
function tasasValidas(bancos) {
  return bancos.filter((b) => b && b.tnaClientes > 0 && b.tnaClientes < 2);
}

function mejorPlazoFijo(bancos) {
  const validos = tasasValidas(bancos);
  if (!validos.length) return null;
  return validos.reduce((a, b) => (b.tnaClientes > a.tnaClientes ? b : a));
}

// La mediana representa mejor "lo que paga un banco típico" que la mejor tasa.
function medianaPlazoFijo(bancos) {
  const t = tasasValidas(bancos).map((b) => b.tnaClientes).sort((a, b) => a - b);
  if (!t.length) return NaN;
  const m = Math.floor(t.length / 2);
  return t.length % 2 ? t[m] : (t[m - 1] + t[m]) / 2;
}

// Inflación mensual promedio (geométrica) de los últimos `meses`, como fracción.
function inflacionPromedio(serie, meses) {
  const ult = serie.slice(-meses);
  if (ult.length < meses) return NaN;
  const acum = ult.reduce((p, d) => p * (1 + d.valor / 100), 1);
  return acum ** (1 / meses) - 1;
}

if (typeof module !== "undefined") {
  module.exports = { temDesdeTna, valorPresenteCuotas, descuentoQueEmpata, veredicto, mejorPlazoFijo, medianaPlazoFijo, inflacionPromedio };
}
