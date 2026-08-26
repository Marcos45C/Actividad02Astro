# Actividad 02 — Representaciones web con Astro

## Pregunta del laboratorio

> ¿Dónde y cuándo se produce cada parte de la interfaz, y qué evidencia permite comprobarlo?

Esta actividad usa el mismo contrato HTTP ya construido (`GET /activities`, `GET /activities/{id}`,
`GET /me/enrollments`, `PUT /me/enrollments/{id}`) para observar qué contenido se genera en
**build time (SSG)** y qué contenido se actualiza en el **navegador (client island)**.

---

## Parte A · Representación estática (SSG)

### 1. Evidencia de build

Comando ejecutado:

```bash
pnpm build
```

<img width="913" height="458" alt="pnpmbuild" src="https://github.com/user-attachments/assets/0853a012-8a86-4d9c-a59b-3a2e27aba307" />


Listado de páginas generadas por actividad:

```bash
ls dist/activities/
```
<img width="1491" height="377" alt="lsactivitis" src="https://github.com/user-attachments/assets/5672aa54-6ece-4014-b6b7-f976cb2337c6" />



### 2. Evidencia de HTML

Comando para inspeccionar el HTML ya generado, sin necesidad de servidor corriendo:

```bash
cat dist/activities/<uuid-de-una-actividad>/index.html
```

Confirmar en el HTML crudo:

- [ ] El `<h1>` con el título de la actividad **ya está presente**.
- [ ] La fecha y la capacidad **ya están presentes**.
- [ ] El color de build (banda de color arriba de la página) **ya está presente**, con un valor `hsl(...)` fijo.
- [ ] **NO** aparece el texto "Cargando estado de inscripción..." ni "Estás inscripto"/"No estás inscripto" en ningún lado del HTML crudo.

<img width="1881" height="518" alt="3-codigo" src="https://github.com/user-attachments/assets/30649026-8d93-4b17-ac1f-793a08a5dc39" />


---

## Parte B · Isla de cliente

### 3. Evidencia de Network + JS

Con `pnpm preview` corriendo y DevTools abierto (pestaña **Network**, filtro **Fetch/XHR**):

1. Recargar `/activities/<id>/`.
2. Confirmar que aparece un request `GET` a `/api/v1/me/enrollments` **después** de que
   el documento HTML ya se cargó.
3. Hacer clic en "Inscribirme" (o "Cancelar inscripción") y confirmar que dispara un
   `PUT` (o `DELETE`) a `/api/v1/me/enrollments/{activity_id}`.

<img width="1773" height="641" alt="04-recarga" src="https://github.com/user-attachments/assets/84ee3a39-2a2f-44bc-9c52-deb134e3dbbb" />


### 4. Evidencia de cambio de datos — la prueba de los dos colores

Para hacer visualmente observable qué región se actualiza y cuál no, se agregaron dos
marcadores de color aleatorio:

| Color | Dónde se genera | Cuándo cambia |
|---|---|---|
| **Color de build** | Frontmatter de `[id].astro`, en build time | Solo con un nuevo `pnpm build` |
| **Color de cliente** | `useState(randomColor)` dentro de `EnrollmentStatus.tsx`, al montar en el navegador | Cada vez que se recarga la página completa (remount) |

<img width="1731" height="469" alt="05-cancelarInscripcion" src="https://github.com/user-attachments/assets/a76898c5-7ed9-4658-8e76-2ff705a9f0d8" />

**Secuencia de prueba y resultado esperado:**

| Acción | Color de build | Color de cliente | Estado de inscripción |
|---|---|---|---|
| Carga inicial | Color A | Color X | según backend |
| Recargar la página (F5) | Color A (igual) | Color Y (**cambió**) | vuelve a consultarse |
| Clic en "Inscribirme"/"Cancelar" (sin recargar) | Color A (igual) | Color Y (**igual**, no hubo remount) | cambia de "no inscripto" a "inscripto" (o viceversa) |
| `pnpm build` de nuevo + recargar | Color B (**cambió**) | Color Z (cambió) | según backend |

- [ ] Captura: color de build y de cliente en la carga inicial.
- [ ] Captura: después de recargar — el color de build es igual, el de cliente cambió.
- [ ] Captura: después de clickear el botón sin recargar — ambos colores iguales a la captura anterior, pero el texto de inscripción cambió.

<img width="1731" height="469" alt="05-cancelarInscripcion" src="https://github.com/user-attachments/assets/1b426bc4-9081-4c98-ac26-59c218b96956" />


**Conclusión que demuestra esta evidencia:** al hacer clic en el botón, solo se actualiza la
región manejada por React (el estado de inscripción); el resto de la página —incluido el color
de build y hasta el propio color de cliente, que no vuelve a generarse sin un remount— permanece
sin cambios. Esto es la diferencia entre *re-render* (cambia el estado dentro del mismo
componente montado) y *remount* (el componente se vuelve a montar desde cero, como ocurre en
cada recarga completa de página).

### 5. Caso de error — 409 Conflict

Pasos para reproducirlo:

1. Elegir una actividad con `capacity` baja (ej. 1) en el fixture.
2. Inscribir a un participante en esa actividad (vía Postman o curl).
3. Cambiar `PUBLIC_DEMO_PARTICIPANT_ID` en el `.env` a otro participante, rebuildear y volver
   a intentar "Inscribirme" en la misma actividad desde la isla de cliente.
4. Confirmar que aparece el mensaje "No quedan cupos disponibles." en la UI.

**Captura sugerida:** el mensaje de error en pantalla + la pestaña Network mostrando el `PUT`
con status `409`.

---

## Checkpoint conceptual

> ¿Qué datos quedaron "congelados" en el resultado del build y qué tendría que ocurrir para que cambien?

_(completar con la redacción del equipo — como guía)_

Quedan congelados en el HTML generado por `pnpm build`: el título, la fecha de inicio, la
capacidad total y el color de build de cada actividad. Estos valores reflejan el estado de la
base de datos **en el momento del build**, no el estado actual. Para que cambien, hace falta un
nuevo `pnpm build` (rebuild manual, o algún mecanismo de revalidación/regeneración como el que
usan otros frameworks — ISR, por ejemplo — que acá no está implementado).

En cambio, el estado de inscripción del participante actual **no** se congela: se resuelve en
el navegador, después de la hidratación, con un `fetch` a `/api/v1/me/enrollments`. Por eso
puede reflejar cambios hechos por fuera de Astro (por ejemplo, una inscripción hecha directo
contra la API con Postman) sin necesidad de ningún rebuild — el HTML no sabe nada de eso, pero
la isla sí, porque consulta el estado real en cada carga.

> ¿Qué evidencia prueba dónde y cuándo se produjo esta interfaz?

_(completar)_ — Referencia cruzada a las secciones 1 a 4 de este documento: el build (sección 1)
prueba el "cuándo" del contenido estático; el HTML crudo (sección 2) prueba que ese contenido
ya estaba resuelto antes de cualquier JavaScript; Network (sección 3) prueba cuándo se dispara
la consulta dinámica; y los dos colores (sección 4) hacen visible, sin necesidad de leer código,
la frontera exacta entre lo que quedó fijo del build y lo que se resuelve en cada carga del
cliente.

---

## Decisiones de diseño (para justificar en la entrega)

- **`client:load` en vez de `client:visible`:** el estado de inscripción es la única región
  interactiva de la página y está visible de entrada (no más abajo, fuera del viewport inicial),
  así que no tiene sentido demorar su hidratación esperando a que entre en pantalla.
- **No se convirtió toda la página en SPA:** solo `EnrollmentStatus.tsx` corre en el cliente;
  el resto (título, fecha, capacidad) sigue siendo HTML puro generado en build, sin JavaScript
  asociado.
- **Operación idempotente en el PUT:** reintentar la inscripción de un participante ya inscripto
  devuelve 200 con los datos existentes en lugar de duplicar o fallar — así el formulario puede
  reintentarse sin necesidad de que el cliente sepa de antemano si ya estaba inscripto.

---

## Explicación de tablas involucradas (heredado de la Actividad 01)

- **Al inscribirse:** se inserta una fila en `activities_enrollment` (participante + actividad +
  fecha). `Activity` no cambia — `available_slots` es un valor calculado, no una columna.
- **Al cancelar:** se borra esa fila de `activities_enrollment`. De nuevo, `Activity` no cambia
  directamente; el recálculo de `available_slots` es lo que refleja la diferencia.
