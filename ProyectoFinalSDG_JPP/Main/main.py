import sys
import random
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from grafos_ui import Ui_MainWindow
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem

# Clase Nodo: representa los nodos del grafo, visualizados como círculos en la interfaz gráfica
class Nodo(QGraphicsEllipseItem):
    def __init__(self, x, y, radius, id, app):
        # Inicializa un nodo como un círculo con un radio especificado
        super().__init__(-radius, -radius, 2 * radius, 2 * radius)
        self.setBrush(QtGui.QBrush(QtGui.QColor("green")))  # Establece el color de relleno del nodo
        self.setPen(QtGui.QPen(QtCore.Qt.black))  # Establece el color del borde del nodo
        self.id = id  # Identificador único del nodo
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)  # Permite mover el nodo en la escena
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)  # Activa notificaciones al mover el nodo
        self.text_item = QGraphicsTextItem(f"Nodo {self.id}", self)  # Etiqueta para mostrar el ID del nodo
        self.text_item.setPos(-10, -10)  # Posición del texto dentro del nodo
        self.app = app  # Referencia a la aplicación principal
        self.aristas = []  # Lista para almacenar las aristas conectadas a este nodo

    def agregar_arista(self, arista):
        """Agrega una arista conectada al nodo."""
        self.aristas.append(arista)

    def itemChange(self, change, value):
        """Gestiona los cambios en la posición del nodo y actualiza las aristas conectadas."""
        if change == QGraphicsItem.ItemPositionChange:
            for arista in self.aristas:
                arista.actualizar_posiciones()  # Ajusta las posiciones de las aristas conectadas
        return super().itemChange(change, value)

# Clase Arista: representa las conexiones entre nodos, visualizadas como líneas
class Arista(QGraphicsLineItem):
    def __init__(self, nodo1, nodo2, peso, scene):
        # Inicializa una arista entre dos nodos con un peso específico
        super().__init__()
        self.nodo1 = nodo1  # Nodo de origen
        self.nodo2 = nodo2  # Nodo de destino
        self.peso = peso  # Peso asignado a la arista
        self.scene = scene  # Escena donde se representa la arista

        # Texto que muestra el peso de la arista, ubicado en el centro de la línea
        self.text_item = QGraphicsTextItem(str(self.peso))
        self.scene.addItem(self.text_item)  # Agrega el texto a la escena gráfica

        self.actualizar_posiciones()  # Calcula las posiciones iniciales de la arista

        self.setFlag(QGraphicsLineItem.ItemIsSelectable)  # Permite seleccionar la arista
        self.setPen(QtGui.QPen(QtCore.Qt.black))  # Establece el color de la línea

    def actualizar_posiciones(self):
        """Actualiza las coordenadas de la línea basándose en las posiciones actuales de los nodos."""
        x1, y1 = self.nodo1.scenePos().x(), self.nodo1.scenePos().y()  # Coordenadas del nodo 1
        x2, y2 = self.nodo2.scenePos().x(), self.nodo2.scenePos().y()  # Coordenadas del nodo 2

        self.setLine(x1, y1, x2, y2)  # Redibuja la línea
        self.text_item.setPos((x1 + x2) / 2, (y1 + y2) / 2)  # Posiciona el texto en el centro de la arista

    def mousePressEvent(self, event):
        """Destaca la arista y los nodos conectados cambiando su color al ser seleccionados."""
        self.setPen(QtGui.QPen(QtCore.Qt.red, 3))  # Cambia el color de la línea a rojo
        self.nodo1.setPen(QtGui.QPen(QtCore.Qt.red, 3))  # Resalta el nodo 1
        self.nodo2.setPen(QtGui.QPen(QtCore.Qt.red, 3))  # Resalta el nodo 2
        super().mousePressEvent(event)

# Clase principal: gestiona la interfaz gráfica y las operaciones relacionadas con el grafo
class GrafoApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(GrafoApp, self).__init__()
        self.ui = Ui_MainWindow()  # Carga la interfaz de usuario
        self.ui.setupUi(self)

        self.graphicsView = self.ui.graphicsView  # Contenedor para la representación gráfica
        self.scene = QGraphicsScene()  # Escena donde se dibujan nodos y aristas
        self.graphicsView.setScene(self.scene)  # Vincula la escena a la vista

        # Conexiones entre botones y sus funciones correspondientes
        self.ui.btnPintarGrafo.clicked.connect(self.dibujar_grafo)
        self.ui.tableWidget.horizontalHeader().sectionClicked.connect(self.llenar_matriz_aleatoria)
        self.ui.btntablaAdyasencia.clicked.connect(self.generar_matriz_adyacencia)
        self.ui.btntablak2.clicked.connect(lambda: self.calcular_potencia_matriz(2))
        self.ui.btntablak3.clicked.connect(lambda: self.calcular_potencia_matriz(3))

        self.nodos = []  # Lista para almacenar nodos del grafo
        self.aristas = []  # Lista para almacenar aristas del grafo

    def dibujar_grafo(self):
        """Construye el grafo en la escena gráfica basado en la matriz de adyacencia."""
        try:
            self.scene.clear()  # Limpia la escena
            self.nodos.clear()  # Reinicia la lista de nodos
            self.aristas.clear()  # Reinicia la lista de aristas

            matriz = self.obtener_matriz()  # Obtiene la matriz de adyacencia desde la interfaz
            self.dibujar_nodos_y_aristas(matriz)  # Crea nodos y aristas en base a la matriz
        except Exception as e:
            print(f"Error al dibujar el grafo: {e}")

    def obtener_matriz(self):
        """Extrae la matriz de adyacencia desde la tabla de la interfaz gráfica."""
        try:
            filas = self.ui.tableWidget.rowCount()  # Número de filas en la tabla
            columnas = self.ui.tableWidget.columnCount()  # Número de columnas en la tabla
            matriz = []
            for i in range(filas):
                fila = []
                for j in range(columnas):
                    item = self.ui.tableWidget.item(i, j)
                    valor = int(item.text()) if item and item.text().isdigit() else 0  # Convierte el texto a entero
                    fila.append(valor)
                matriz.append(fila)
            return matriz
        except Exception as e:
            print(f"Error al obtener la matriz: {e}")
            return []


    def dibujar_nodos_y_aristas(self, matriz):
        """Dibuja los nodos y las aristas en la escena según la matriz de adyacencia."""
        try:
            num_nodos = len(matriz)  # Número de nodos
            radius = 20  # Radio de los nodos
            width = self.graphicsView.width() - 100  # Ancho de la vista (con margen)
            height = self.graphicsView.height() - 100  # Alto de la vista (con margen)

            # Dibuja los nodos en posiciones aleatorias dentro de la vista
            for i in range(num_nodos):
                x = random.randint(50, width)  # Posición aleatoria en el eje X
                y = random.randint(50, height)  # Posición aleatoria en el eje Y
                nodo = Nodo(x, y, radius, i + 1, self)
                nodo.setPos(x, y)
                self.scene.addItem(nodo)
                self.nodos.append(nodo)  # Añade el nodo a la lista

            # Dibuja las aristas entre los nodos según los valores de la matriz de adyacencia
            for i in range(num_nodos):
                for j in range(i + 1, num_nodos):
                    peso = matriz[i][j]  # Obtiene el peso de la arista
                    if peso > 0:  # Si hay una conexión (peso > 0)
                        nodo1 = self.nodos[i]
                        nodo2 = self.nodos[j]
                        arista = Arista(nodo1, nodo2, peso, self.scene)
                        self.aristas.append(arista)
                        self.scene.addItem(arista)  # Añade la arista a la escena
                        nodo1.agregar_arista(arista)  # Añade la arista al nodo 1
                        nodo2.agregar_arista(arista)  # Añade la arista al nodo 2
        except Exception as e:
            print(f"Error al dibujar nodos y aristas: {e}")

    def llenar_matriz_aleatoria(self, index):
        """Llena la matriz de adyacencia con valores aleatorios, asegurando que todos los nodos tengan al menos una conexión."""
        try:
            filas = self.ui.tableWidget.rowCount()
            columnas = self.ui.tableWidget.columnCount()

            probabilidad_conexion = 0.5  # Probabilidad de conexión entre nodos

            for i in range(filas):
                for j in range(columnas):
                    if i == j:
                        self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem('0'))  # No se conecta a sí mismo
                    else:
                        # Determina si debe haber conexión entre los nodos i y j
                        if random.random() < probabilidad_conexion:
                            valor_aleatorio = random.randint(1, 100)
                            self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(valor_aleatorio)))
                        else:
                            self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem('0'))

            # Asegurarse de que cada nodo tenga al menos una conexión
            for i in range(filas):
                conexiones = sum(1 for j in range(columnas) if self.ui.tableWidget.item(i, j) and int(self.ui.tableWidget.item(i, j).text()) > 0)

                # Si el nodo `i` no tiene conexiones, fuerza una conexión aleatoria
                if conexiones == 0:
                    j = random.choice([x for x in range(columnas) if x != i])
                    valor_aleatorio = random.randint(1, 100)
                    self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(valor_aleatorio)))
                    # Hacer la conexión bidireccional
                    self.ui.tableWidget.setItem(j, i, QtWidgets.QTableWidgetItem(str(valor_aleatorio)))
        except Exception as e:
            print(f"Error al llenar la matriz: {e}")

    def generar_matriz_adyacencia(self):
        """Genera la matriz de adyacencia a partir de la matriz de pesos y la muestra en una tabla."""
        matriz_pesos = self.obtener_matriz()
        matriz_adyacencia = [[1 if valor > 0 else 0 for valor in fila] for fila in matriz_pesos]  # Transforma los pesos en 1 o 0
        self.mostrar_en_tabla(self.ui.tablaAdyasencia, matriz_adyacencia)  # Muestra la matriz de adyacencia

    def calcular_potencia_matriz(self, k):
        """Calcula la potencia k-ésima de la matriz de adyacencia."""
        matriz_adyacencia = np.array(self.obtener_matriz_adyacencia())
        matriz_k = np.linalg.matrix_power(matriz_adyacencia, k)  # Calcula la potencia de la matriz
        if k == 2:
            self.mostrar_en_tabla(self.ui.tablak2, matriz_k.tolist())  # Muestra la potencia k=2
        elif k == 3:
            self.mostrar_en_tabla(self.ui.tablak3, matriz_k.tolist())  # Muestra la potencia k=3

    def obtener_matriz_adyacencia(self):
        """Convierte la matriz de pesos a una matriz de adyacencia (1 o 0)."""
        matriz_pesos = self.obtener_matriz()
        return [[1 if valor > 0 else 0 for valor in fila] for fila in matriz_pesos]

    def mostrar_en_tabla(self, tabla, matriz):
        """Muestra una matriz en una tabla de la interfaz gráfica."""
        tabla.setRowCount(len(matriz))
        tabla.setColumnCount(len(matriz[0]))
        for i in range(len(matriz)):
            for j in range(len(matriz[i])):
                tabla.setItem(i, j, QtWidgets.QTableWidgetItem(str(matriz[i][j])))

if __name__ == "__main__":
    # Código principal que inicializa la aplicación y la muestra en pantalla
    app = QtWidgets.QApplication(sys.argv)
    window = GrafoApp()
    window.show()
    sys.exit(app.exec_())
