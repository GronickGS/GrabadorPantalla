from tqdm import tqdm
import time

# Número de iteraciones
total_iterations = 100

# Usando tqdm en un bucle
for i in tqdm(range(total_iterations)):
    time.sleep(0.05)  # Simula un trabajo en proceso
