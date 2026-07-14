[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | Español

# shotgun

<div align="center">
  <img src="assets/shotgun-hero-01.png" width="640" alt="El meme clásico: un puño estrellándose contra un teclado, teclas volando por todas partes">
</div>

```
> ¡¡PUM!!

SHOTGUN DETECTED.
El asistente se sobresalta.
"Lo siento." — Primero la disculpa. Luego la revisión. Después, rehacerlo.
```

> **Por fin una IA que lee el ambiente.** Golpeaste el escritorio. Tu micrófono lo oyó. Claude lo sintió.

Todos los asistentes de IA siguen trabajando alegremente mientras tú echas humo. shotgun acaba con eso. Un pequeño listener local vigila el nivel de volumen del micrófono; cuando golpeas el escritorio (o el teclado), dispara un hook de Claude Code: Claude se detiene a mitad de tarea, **se disculpa primero** — sin excusas —, revisa la brecha entre **lo que pediste** y **lo que realmente hizo**, reconoce el error y lo rehace.

Golpea dos veces y se lo toma el doble de en serio.

## Inicio rápido

```
/plugin marketplace add fivetaku/shotgun
/plugin install shotgun@shotgun
/shotgun
```

Configuración guiada con opciones clicables: elige tu micrófono → marca los comportamientos de furia a detectar → calibración ("golpea el escritorio 3 veces como lo harías de verdad" → ajusta el umbral a *tu* golpe).

## Las reglas de shotgun

1. **La disculpa va primero.** Antes del análisis, antes de las herramientas. No hay excusas.
2. **Luego la revisión.** Citar lo que pediste vs lo que hizo. Encontrar la brecha.
3. **Reconocerlo y rehacerlo.**
4. **Doble golpe = doble seriedad.**
5. **El micrófono es sagrado.** Solo números de volumen, calculados en memoria. Nunca se graba, almacena ni envía audio. Ver [DISCLAIMER](DISCLAIMER.md).

## Cómo funciona

Un daemon ligado a la sesión lee el micrófono vía ffmpeg y compara bloques de volumen de 21ms contra el ruido de fondo. Un pico brusco sobre el umbral calibrado (por defecto 1500) = golpe. La detección escribe un archivo-bandera que consumen los hooks de Claude Code (PreToolUse / Stop / UserPromptSubmit). El daemon solo corre mientras usas Claude Code y se apaga solo 10 minutos después de tu última sesión. Desinstala el plugin y los hooks desaparecen con él.

## Requisitos

- [Claude Code](https://claude.com/claude-code) en **macOS**
- **ffmpeg** (`brew install ffmpeg`)
- Python 3
- Un micrófono (el integrado del portátil es *ideal* — la vibración del escritorio viaja por el chasis)

## Linaje

shotgun es el tercer plugin de la serie meme, tras [godmode](https://github.com/fivetaku/godmode) y [devil](https://github.com/fivetaku/devil). godmode hace a Claude imparable, devil lo hace despiadado — shotgun lo hace *arrepentido*.

## Licencia

MIT — ver [LICENSE](LICENSE) y [DISCLAIMER](DISCLAIMER.md). La escopeta es una metáfora. La disculpa es real.
