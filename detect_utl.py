import cv2
from ultralytics import YOLO
import os
import torch

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
torch.set_num_threads(1)

# 1. Загрузка предобученной модели YOLO
# Модель 'yolov8n.pt' - это самая легкая и быстрая версия.
# Для большей точности можно использовать 'yolov8s.pt' или 'yolov8x.pt'
MODEL_PATH = 'yolo26n.pt'

if not os.path.exists(MODEL_PATH):
    print(f"Модель {MODEL_PATH} не найдена. Загрузка из интернета...")
    # Если файл не найден, конструктор автоматически скачает его [citation:1][citation:4]
    
model = YOLO(MODEL_PATH)

def detect_vehicles(image_path, conf_threshold=0.5, output_path='output.jpg'):
    """
    Детектирует транспортные средства на изображении с помощью YOLO.
    
    Args:
        image_path (str): Путь к входному изображению.
        conf_threshold (float): Порог уверенности (0.0 - 1.0).
        output_path (str): Путь для сохранения результата.
    """
    # Загружаем изображение с помощью OpenCV
    # BGR - стандартная цветовая схема OpenCV
    img_bgr = cv2.imread(image_path)
    
    if img_bgr is None:
        #print(f"Ошибка: не удалось загрузить изображение по пути {image_path}")
        return

    # Конвертируем BGR в RGB, так как YOLO обучен на RGB
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    # Выполняем инференс (детекцию)
    # results содержит список объектов Result (по одному на каждое изображение)
    # results = model(img_rgb, conf=conf_threshold)[0]
    # Улучшенные параметры детекции
    results = model(
        img_rgb,
        
        # Основные параметры
        conf=conf_threshold,      # Снижаем порог уверенности (по умолч. 0.25)
        iou=0.45,       # IoU для NMS (Non-Maximum Suppression)
        
        # Улучшение качества
        agnostic_nms=True,      # NMS для всех классов вместе
        max_det=300,            # Максимум объектов на изображение
        
        # Увеличение размера изображения (важно для маленьких объектов!)
        imgsz=1280,             # По умолчанию 640, увеличение улучшает детекцию
        
        # Аугментация при инференсе (улучшает для сложных случаев)
        augment=True,           # Включение тестовой аугментации
        
        # Получение сегментов (если нужно)
        #visualize=False,
        #verbose=True
    )[0]
    
    # Список ID классов, которые мы считаем "транспортными средствами" (стандартный COCO датасет)
    # Согласно спецификации COCO [citation:8]
    VEHICLE_CLASSES = {
        2: 'car',       # автомобиль
        3: 'motorcycle',# мотоцикл
        5: 'bus',       # автобус
        7: 'truck'      # грузовик
        # Примечание: Bicycle (1) часто тоже детектится отдельно при необходимости
    }
    
    detected_count = 0
    
    # Обрабатываем результаты
    if results.boxes is not None:
        for box in results.boxes:
            # Получаем координаты ограничивающей рамки (bounding box)
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            
            # Проверяем, является ли найденный объект нужным типом транспорта
            if class_id in VEHICLE_CLASSES:
                detected_count += 1
                class_name = VEHICLE_CLASSES[class_id]
                label = f"{class_name} {confidence:.2f}"
                
                # Рисуем прямоугольник на ИСХОДНОМ изображении (BGR) [citation:1]
                # cv2.rectangle(img_bgr, (x1, y1), (x2, y2), (0, 255, 255), 2) # Желтый цвет
                # cv2.putText(img_bgr, label, (x1, y1 - 10), 
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    
    print(f"Статистика: Обнаружено {detected_count} транспортных средств. Уверенность > {conf_threshold}")
    
    # Сохраняем результат
    #cv2.imwrite(output_path, img_bgr)
    #print(f"Результат сохранен в {output_path}")
    
    #(Опционально) Показать изображение в окне
    # cv2.imshow('Detection Result', img_bgr)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return detected_count

