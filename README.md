# IPM – Juego de Conducción 3D Controlado con Gestos

¡Bienvenido a **IPM**!  
Un juego de carreras en 3D desarrollado con **Ursina**, donde el jugador controla un coche utilizando **gestos de las manos detectados con MediaPipe** para simular el giro del volante.

---

## 🎮 Descripción

En este juego:

- Conduces un coche en **primera persona**, con tablero y volante visibles.  
- Evitas **enemigos y obstáculos** generados dinámicamente.  
- Recolectas **power-ups**, incluyendo el `CoronaPower`, que te dan ventajas temporales.  
- El juego incluye un **ciclo día/noche**, con cambios de iluminación y shaders dinámicos.  
- La **dificultad aumenta progresivamente** según avanzas.  
- Puedes controlar el volante con **gestos de tu mano detectados en tiempo real** mediante **MediaPipe**, haciendo la experiencia más inmersiva.

---

## 🛠 Tecnologías utilizadas

- **Python 3.12+**  
- **Ursina Engine** (3D engine para Python)  
- **MediaPipe** (detección de gestos de mano para controlar el volante)  
- **OpenGL / Shaders** para iluminación y efectos de día/noche  

---

## 📥 Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/santvz6/IPM-main.git
cd IPM-main
```