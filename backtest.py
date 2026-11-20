"""Backtest: ¿convenían las cuotas sin interés, con la inflación que realmente pasó?

Para cada mes de compra t y cada plan de N cuotas sin interés, calcula cuánto valían
las cuotas en pesos del mes de compra, deflactando cada cuota por la inflación
efectivamente registrada:

    valor_real = sum_{k=1..N} (1/N) / prod_{j=1..k} (1 + inflacion[t+j])

El "descuento equivalente" es 1 - valor_real: si por pagar de contado te ofrecían
más que eso, convenía contado; si te ofrecían menos, convenían las cuotas.

Fuente: inflación mensual del INDEC vía api.argentinadatos.com.
Solo biblioteca estándar: se corre con `python backtest.py`.
"""

import csv
import json
import sys
import urllib.request
from pathlib import Path

URL = "https://api.argentinadatos.com/v1/finanzas/indices/inflacion"
DESDE = "2017-01"
PLANES = (3, 6, 12)
SALIDA = Path(__file__).with_name("backtest.csv")


def descargar():
    req = urllib.request.Request(URL, headers={"User-Agent": "cuotas-o-contado/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def serie_mensual(datos, desde=DESDE):
    """{'2017-01': 0.016, ...} con la inflación como fracción, ordenada y sin huecos."""
    serie = {}
    for d in datos:
        mes = d["fecha"][:7]
        if mes >= desde and d.get("valor") is not None:
            serie[mes] = d["valor"] / 100
    meses = sorted(serie)
    for a, b in zip(meses, meses[1:]):
        if siguiente_mes(a) != b:
            raise ValueError(f"Hueco en la serie de inflación entre {a} y {b}")
    return {m: serie[m] for m in meses}


def siguiente_mes(mes):
    y, m = int(mes[:4]), int(mes[5:])
    return f"{y + (m == 12)}-{1 if m == 12 else m + 1:02d}"


def valor_real_cuotas(inflaciones, n):
    """Valor de N cuotas de 1/N en pesos del mes de compra.

    inflaciones: las de los meses t+1, t+2, ... (al menos n valores).
    """
    if len(inflaciones) < n:
        raise ValueError(f"Hacen falta {n} meses de inflación, hay {len(inflaciones)}")
    total, deflactor = 0.0, 1.0
    for k in range(n):
        deflactor *= 1 + inflaciones[k]
        total += (1 / n) / deflactor
    return total


def descuento_equivalente(inflaciones, n):
    return 1 - valor_real_cuotas(inflaciones, n)


def backtest(serie, planes=PLANES):
    meses = list(serie)
    filas = []
    for i, mes in enumerate(meses):
        futuras = [serie[m] for m in meses[i + 1:]]
        fila = {"mes": mes, "inflacion": round(serie[mes], 4)}
        for n in planes:
            fila[f"cuotas_{n}"] = round(descuento_equivalente(futuras, n), 4) if len(futuras) >= n else ""
        filas.append(fila)
    return filas


def guardar(filas, ruta=SALIDA, planes=PLANES):
    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["mes", "inflacion"] + [f"cuotas_{n}" for n in planes], lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


def main():
    serie = serie_mensual(descargar())
    if len(serie) < 60:
        sys.exit(f"Muy pocos meses ({len(serie)}): no se pisa backtest.csv.")
    filas = backtest(serie)
    guardar(filas)
    print(f"{len(filas)} meses, {filas[0]['mes']} a {filas[-1]['mes']}")
    completas = [f for f in filas if f["cuotas_12"] != ""]
    pico = max(completas, key=lambda f: f["cuotas_12"])
    piso = min(completas, key=lambda f: f["cuotas_12"])
    print(f"12 cuotas: máximo {pico['cuotas_12']:.1%} ({pico['mes']}), mínimo {piso['cuotas_12']:.1%} ({piso['mes']}), "
          f"último completo {completas[-1]['cuotas_12']:.1%} ({completas[-1]['mes']})")


if __name__ == "__main__":
    main()
