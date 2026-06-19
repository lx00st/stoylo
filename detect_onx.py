import cv2
#from ultralytics import YOLO
import os
import numpy as np
import onnxruntime as ort
#import torch

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# 1. Загрузка предобученной модели YOLO
# Модель 'yolov8n.pt' - это самая легкая и быстрая версия.
# Для большей точности можно использовать 'yolov8s.pt' или 'yolov8x.pt'
MODEL_PATH = 'data/yolo26x.onnx'

if not os.path.exists(MODEL_PATH):
    print(f"Модель {MODEL_PATH} не найдена. Загрузка из интернета...")
    # Если файл не найден, конструктор автоматически скачает его [citation:1][citation:4]

    

def detect_vehicles(image_path, conf_threshold=0.5, output_path='output.jpg'):
    """
    Детектирует транспортные средства на изображении с помощью YOLO.
    
    Args:
        image_path (str): Путь к входному изображению.
        conf_threshold (float): Порог уверенности (0.0 - 1.0).
        output_path (str): Путь для сохранения результата.
    """
    
    # ID классов транспорта в COCO датасете:
    # 2: car, 3: motorcycle, 5: bus, 7: truck
    VEHICLE_CLASSES = {2.0, 3.0, 5.0, 7.0}  

    # 1. Инициализация сессии ONNX Runtime (с исправлением list-ошибки)
    session = ort.InferenceSession(MODEL_PATH)
    input_name = session.get_inputs()[0].name  # Исправлено на [0]

    # 2. Подготовка изображения
    img = cv2.imread(image_path)
    img_h, img_w, _ = img.shape
    img_resized = cv2.resize(img, (640, 640))
    img_data = img_resized.transpose(2, 0, 1)  # HWC -> CHW
    img_data = np.expand_dims(img_data, axis=0).astype(np.float32) / 255.0

    # 3. Инференс
    outputs = session.run(None, {input_name: img_data})

    # Убираем размерность батча: [1, 300, 6] -> [300, 6]
    output = np.squeeze(outputs[0]) 

    # 4. Подсчет объектов по новой структуре YOLO26
    total_vehicles = 0
    vehicle_details = []

    # Определяем, нормализованы ли координаты (обычно YOLO26 отдает в масштабе 640x640)
    # Коэффициенты для перевода в реальный размер картинки:
    x_factor = img_w / 640
    y_factor = img_h / 640

    for row in output:
        # Структура строки YOLO26: [x1, y1, x2, y2, confidence, class_id]
        confidence = row[4]
        class_id = row[5]
        
        # Проверяем порог и класс
        if confidence >= conf_threshold and class_id in VEHICLE_CLASSES:
            total_vehicles += 1
            
            # Получаем координаты (формат xyxy)
            x1, y1, x2, y2 = row[0:4]
            
            # Масштабируем под оригинальный размер вашего фото
            left = int(x1 * x_factor)
            top = int(y1 * y_factor)
            right = int(x2 * x_factor)
            bottom = int(y2 * y_factor)
            
            vehicle_details.append({
                "class_id": int(class_id),
                "confidence": float(confidence),
                "box": [left, top, right - left, bottom - top]
            })

    # 5. Вывод результатов в консоль
    print(f" Найдено транспортных средств (YOLO26): {total_vehicles}")

    # class_names = {2: "Car", 3: "Motorcycle", 5: "Bus", 7: "Truck"}
    # for vehicle in vehicle_details:
    #     print(f" - [{class_names[vehicle['class_id']]}]: Уверенность {vehicle['confidence']*100:.1f}%")

    return total_vehicles
