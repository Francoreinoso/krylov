// La copia en TypeScript de la capa de decisión da lo mismo que la de Python, caso por caso.
// Correr: npm run prueba

import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { decidirEspacial, decidirTabla } from '../src/decision.ts'

const ruta = new URL('../../contratos/ejemplos/decision_prueba.json', import.meta.url)
const { tolerancia, casos } = JSON.parse(readFileSync(ruta, 'utf-8'))

casos.forEach((caso: any, i: number) => {
  test(`caso ${i} (${caso.regla})`, () => {
    const r =
      caso.regla === 'tabla'
        ? decidirTabla(caso.muestras_p, caso.c_si, caso.c_no)
        : decidirEspacial(caso.p, caso.c_si, caso.c_no)
    assert.equal(r.estado, caso.espera.estado)
    assert.ok(Math.abs(r.duda - caso.espera.duda) <= tolerancia, `duda ${r.duda} ≠ ${caso.espera.duda}`)
    if (caso.espera.p !== undefined) {
      assert.ok(Math.abs(r.p - caso.espera.p) <= tolerancia, `p ${r.p} ≠ ${caso.espera.p}`)
    }
  })
})
