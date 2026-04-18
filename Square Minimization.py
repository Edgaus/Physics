import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



df = pd.read_csv('Physics\PL test.txt', sep=',')
print(df)


x_data = df['Energy'].to_numpy()
y_data = df['Signal eV'].to_numpy()

print(x_data, y_data)
# Datos
c_conocido = 5.0
y_modificado = y_data - c_conocido  # Restamos el término conocido

# Matriz de diseño reducida (solo columnas x^2 y x, sin la columna de 1s)
# X = [x^2, x]
X_reducida = np.vstack([x_data**2, x_data]).T

# Ajuste matricial estándar
# Resolvemos para [a, b]
beta = np.linalg.inv(X_reducida.T @ X_reducida) @ X_reducida.T @ y_modificado
a_fit, b_fit = beta

print(f"Ecuación: y = {a_fit}x^2 + {b_fit}x + {c_conocido}")


plot_x = np.linspace(min(x_data), max(x_data), 100)
plot_y = a_fit * plot_x**2 + b_fit * plot_x + c_conocido
plt.scatter(x_data, y_data, label='Datos experimentales', color='blue')
plt.plot(plot_x, plot_y, label='Ajuste cuadrático', color='red')
plt.xlabel('x') 
plt.ylabel('y')
plt.title('Ajuste cuadrático por mínimos cuadrados')
plt.legend()
plt.show()# Ajuste cuadrático por mínimos cuadrados con término constante conocido