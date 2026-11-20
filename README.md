# ¿Cuotas sin interés o descuento de contado?

Calculadora para el Black Friday (27/11/2026): ¿conviene pagar en cuotas sin interés o aprovechar el descuento por pagar de contado? Usa tasas de plazo fijo e inflación en vivo, y suma un backtest desde 2017 con la inflación que realmente pasó.

**Probala:** https://lucasselis.github.io/cuotas-o-contado/

## Qué responde

- Con el precio, el descuento y las cuotas que te ofrecen, ¿qué conviene hoy y cuánto te ahorrás?
- ¿Qué descuento de contado empata con 3, 6, 9, 12 o 18 cuotas sin interés? (el "machete")
- Mirando hacia atrás: ¿cuánto valían de verdad las cuotas sin interés en cada Black Friday desde 2017?

## Datos

| Dato | Fuente | Se actualiza |
|---|---|---|
| TNA de plazo fijo a 30 días por banco (31 entidades) | [argentinadatos.com](https://argentinadatos.com) `/v1/finanzas/tasas/plazoFijo` (datos del BCRA) | En vivo |
| Inflación mensual, INDEC | [argentinadatos.com](https://argentinadatos.com) `/v1/finanzas/indices/inflacion` | En vivo y en el backtest |

Si la API no responde, la página usa una copia del 20/11/2026 y lo avisa.

## Método

**Calculadora.** Las cuotas se pagan a futuro, así que se llevan a pesos de hoy:

```
valor_hoy = Σ cuota / (1 + r)^k     para k = 1 … N
```

La primera cuota cae en el próximo resumen, dentro de un mes. `r` es la tasa mensual que elijas:

- **Plazo fijo, banco típico:** mediana de la TNA de los bancos que informan tasa, pasada a mensual (TNA × 30 / 365). Es lo que ganarías con esa plata mientras pagás las cuotas.
- **Plazo fijo, mejor tasa:** el banco que más paga hoy.
- **Inflación del último mes** o **promedio de los últimos 3 meses** (geométrico).

El **descuento que empata** es `1 − valor_hoy / precio`. Si te ofrecen más que eso por pagar de contado, conviene contado.

**Backtest** (`backtest.py`, solo biblioteca estándar de Python). Para cada mes de compra desde 2017, deflacta cada cuota por la inflación que efectivamente se registró en los meses siguientes:

```
valor_real = Σ (1/N) / Π_{j=1..k} (1 + inflación[t+j])
```

Antes de calcular, verifica que la serie no tenga huecos. Si falta un mes, corta en vez de calcular mal. Escribe `backtest.csv`, que la página lee.

## Resultado

**Hoy (20/11/2026),** con el plazo fijo típico (20,5% TNA, 1,68% mensual), 12 cuotas sin interés equivalen a un **10,1% de descuento**. Si en el Black Friday te ofrecen 15% por pagar de contado, conviene contado.

**Backtest, 12 cuotas sin interés en cada Black Friday:**

| Black Friday | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|
| Descuento equivalente | 16% | 19% | 15% | 21% | 27% | 34% | **50%** | 14% |

En noviembre de 2023, 12 cuotas sin interés valían la mitad del precio: pagabas el 50% en términos reales. Un año después, con la inflación a la baja, valían 14% menos. Hoy el número que importa no es el de hace dos años.

## Tests

- `test_backtest.py`: 9 tests con `unittest` (porcentaje a fracción, detección de huecos, cambio de año, deflactado acumulado, más cuotas valen menos, meses sin datos futuros). Corren en GitHub Actions.
- `tests.html`: 13 tests de `calculo.js` en el navegador (tasa mensual, valor presente, recargo, veredicto, mediana y mejor tasa, inflación promedio).

## Límites

- No es asesoramiento financiero.
- La calculadora no contempla que las cuotas ocupen el límite de la tarjeta, ni reintegros o promociones bancarias.
- Si tenés que pedir un préstamo para pagar de contado, la tasa que corresponde es la de ese préstamo, no la de un plazo fijo.
- El backtest supone que cada cuota se paga a fin de los meses siguientes a la compra.

## Stack

Python (biblioteca estándar) para el backtest. HTML, CSS y JavaScript sin dependencias para la página, con gráficos en SVG dibujados a mano. GitHub Actions para tests y actualización. Publicado en GitHub Pages.

---

Lucas Selis · Data Analyst & BI · [LinkedIn](https://www.linkedin.com/in/lucas-selis/)
