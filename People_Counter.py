## Работа ведется HydroslidE и ostapella
import numpy as np
import cv2, time
from datetime import datetime
import Person

##############
## Функции ##
#############
# Записываем в лог файл чтобы далее оперировать этими данными. Файлы  составляются таким образом, чтобы их смогла прочитать 1С, а так же чтобы поменять американский обычай записи месяц\число\год
def Save_log(direction, date_now):
    try:
        if direction == "up": # Если движение шло вверх, то сохраняем одни данные. Если нет - другие
            direct = ["1","2"]
        else:
            direct = ["1","1"]
#        date_now = datetime.now() # Текущая дата и время
        ms_now = str(int(time.time()/1000)) # Время в миллисекундах, начиная с 12 часов 1 января 1970
        log_file = open(date_now.strftime("%d%m%y%H") + ".txt", "a") #Добавить номер файлов
        log_file.write( date_now.strftime("%d.%m.%Y") + "|" + ms_now + "|" + direct[0] + "|" + direct[1] + "|PCCapture|"+"0" + "|\n")
        log_file.close();

        return True
    except:
        return False

def nothing(x): # Обязательная функция, которая вызывается при движении трекпада.
    pass # В нашем случае функция не должна ничего делать, так что пропускаем действие.

################################
## Область основной программы ##
################################
#Счетчики входа и выхода
cnt_up   = 0
cnt_down = 0

#Захват видео
cap = cv2.VideoCapture("http://192.168.1.35//video.cgi")
if not cap.isOpened(): #Подключение по айпи, если не удается, то попытка переключения на камеру по умолчанию
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print( "Video Capture error: Can't find camera.")

#Загружаем сохраненные настройки
setting = []
try:
    setting_file = open("Setting", "r")
    for line in setting_file:
        setting.append(int(line))
    setting_file.close()

    if( len(setting) != 5 or min(setting) <= 0): # Вызываем исключение если по какой-то причине в файле были повреждены данные
        raise

    print("Load setting from file")
except:
    # При возникновении ошибки чтения присваиваем стандартные значения
    setting = [30, 215, 252,288,192]
    print("Load default setting")
"""
Памятка по значениям настроек:
setting[0] - min threshold
setting[1] - min object
setting[2] - max object
setting[3] - down line
setting[4] - top line
setting[5] - visible_frame - пока что нет
"""

frame_width = cap.get(3) # Получаем длину кадра
frame_height = cap.get(4) # Получаем высоту кадра
res = ( frame_height * frame_width )
min_areaTH = res / 40  # Делим высоту и длину кадра на выбранный коэфициент. Его мы подбираем из соображений наилучшего обнаружения
print ('Min area Threshold', min_areaTH) # Минимальный азмер объекта
max_areaTH = res / 3
print ('Max area Threshold', max_areaTH) # Максимальный размер объекта

# Расчет первоначальных настроек
line_down = int(3*(frame_height/5)) # Строим линию на уровне 3\5 Экрана
print ("Red line y:",str(line_down) ) # Выводим в консольно координату по высоте
pt1 =  [0, line_down]; # координаты крайних точек линий" линии
pt2 =  [frame_width, line_down];
pts_L1 = np.array([pt1,pt2], np.int32) # собираем все в матрицу
pts_L1 = pts_L1.reshape((-1,1,2)) # трансформирует матрицу чисел по виду 1 строка, 2 столбика для дальнейшей работы.
line_down_color = (255,0,0) # Задаем цвет линии

line_up = int(2*(frame_height/5)) # Аналогичные операции для 2\5 экрана
print ("Blue line y:", str(line_up) )
pt3 =  [0, line_up];
pt4 =  [frame_width, line_up];
pts_L2 = np.array([pt3,pt4], np.int32)
pts_L2 = pts_L2.reshape((-1,1,2))
line_up_color = (0,0,255)

#Структурируем элементы морфографических фильтров
kernelOp = np.ones((3,3),np.uint8) # Создает новый массив заданного размера и типа(В данном случае восьмибитный unsigned int)
kernelOp2 = np.ones((5,5),np.uint8)
kernelCl = np.ones((11,11),np.uint8)

#Переменные для дальнейшей работы
font = cv2.FONT_HERSHEY_SIMPLEX # Задаем шрифты для корректного отображения текста. Векторные шрифты Херши распространены за счет легкого преобразования в любую плоскость, угол и так далее.
persons = [] # Создаем массив для детектора движения

#Объявление ползунков
Panel = np.zeros([1,256], np.uint8)
cv2.namedWindow("Panel", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Panel", int(frame_width), 720)

# Создаем трекбары. Последим аргументом идет пропусск действия при изменении трекбара. Их значения мы будет получать позже
cv2.createTrackbar("THRSH_MIN", "Panel", setting[0], 255, nothing)
cv2.createTrackbar("MIN OBJ", "Panel", setting[1], 255, nothing)
cv2.createTrackbar("MAX OBJ", "Panel", setting[2], 255, nothing)
cv2.createTrackbar("DWN_LINE", "Panel", setting[3], int(frame_height), nothing)
cv2.createTrackbar("TOP_LINE", "Panel", setting[4], int(frame_height), nothing)
#cv2.createTrackbar("VISIBLE_FRAME", "Panel", setting[5], 1, nothing)

iteration_counter = 0
now_setting = [1,1,1,1,1]

ret, mask_frame = cap.read() # Читаем кадр для сравнения
while(cap.isOpened()): # Пока камера передает изображения
    ret, frame = cap.read()  #Считываем изображение с камеры
    frame_ABS =  cv2.absdiff(frame, mask_frame) # Производим чистое вычитание из "первого" кажра текущего. Таким образом, имея эталонный кадр без движения мы получим в разнице все движение на кадре.
#    cv2.imshow('ADS',frame_ABS)
#    gray_frame = cv2.cvtColor(frame_ABS, cv2.COLOR_BGR2GRAY) # Переводим результат вычитания в оттенки серого
    gray_frame = cv2.cvtColor(frame_ABS, cv2.COLOR_BGR2GRAY)

    cv2.imshow("Panel", Panel)
    # Работа с ползунками. Читаем значение ползунков
    now_setting[0] = cv2.getTrackbarPos("THRSH_MIN", "Panel")
    now_setting[1] = cv2.getTrackbarPos("MIN OBJ", "Panel")
    now_setting[2] = cv2.getTrackbarPos("MAX OBJ", "Panel")
    now_setting[3] = cv2.getTrackbarPos("DWN_LINE", "Panel")
    now_setting[4] = cv2.getTrackbarPos("TOP_LINE", "Panel")
#    now_setting[5] = cv2.getTrackbarPos("VISIBLE_FRAME", "Panel")

    if not np.array_equal(now_setting, setting): # Если положение трекбаров не совпадает, то пересчитываем переменные и сохраняем новые настройки
        for i in range(0,5):
            setting[i] = now_setting[i]

        # Расчитываем параметры из значений
        min_areaTH = res / (255-setting[1]+1)
        max_areaTH = res / (255-setting[2]+1)
#        line_down = int(setting[4])
#        line_up = int(setting[5])

        if (line_down != int(setting[3])): #Если линии не совпадают, то перестраиваем
            line_down = int(setting[3])
            print("Red line y:", str(line_down))  # Выводим в консольно координату по высоте
            pt1 = [0, line_down];  # координаты крайних точек линий" линии
            pt2 = [frame_width, line_down];
            pts_L1 = np.array([pt1, pt2], np.int32)  # собираем все в матрицу
            pts_L1 = pts_L1.reshape((-1, 1, 2))  # трансформирует матрицу чисел по виду 1 строка, 2 столбика для дальнейшей работы.
            line_down_color = (255, 0, 0)  # Задаем цвет линии

        if (line_up != int(setting[4])):
            line_up = int(setting[4])
            print("Blue line y:", str(line_up))
            pt3 = [0, line_up];
            pt4 = [frame_width, line_up];
            pts_L2 = np.array([pt3, pt4], np.int32)
            pts_L2 = pts_L2.reshape((-1, 1, 2))
            line_up_color = (0, 0, 255)

        setting_file = open("Setting", "w")
        setting_file.write(str(setting[0]) +  "\n" + str(setting[1]) + "\n" + str(setting[2]) + "\n" + str(setting[3]) + "\n" + str(setting[4]))
        setting_file.close();
        print("Saved in file")

    try:
        ret,imBin= cv2.threshold(gray_frame, setting[0], 255, cv2.THRESH_BINARY)  # Бинаризация изображения (Перевод изображний в черно-белые оттенки)
#        cv2.imshow('threshold',imBin)
        morphology_mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernelOp)   # "Открытие" Морфологической трансформирмации (эрозия -> растяжение). Позволяет удалить посторонние шумы вокруг объекта.
        morphology_mask =  cv2.morphologyEx(morphology_mask , cv2.MORPH_CLOSE, kernelCl)  # "Закрытие" (растяжение -> эрозия) для соединения областей внутри объекта.
        cv2.imshow('morphologyEx', morphology_mask )
    except:
        # При возникновении любой ошибки завершать выполнение программы
        print('Error threshold or morphology. End of programm.')
        print ('UP:',cnt_up)
        print ('DOWN:',cnt_down )
        break

    img_, contours0, hierarchy_ = cv2.findContours( #Ищем контуры на изображении
        morphology_mask, #Бинарное изображение, где ищутся контуры
        cv2.RETR_EXTERNAL, # Извлекает только крайние внешние контуры
        cv2.CHAIN_APPROX_SIMPLE) # Сжимает все сегменты контура и оставляет только крайние точки.

    for cnt in contours0: # Для каждого контура
        area = cv2.contourArea(cnt) # Вычисляет положение контура
        if area > min_areaTH and area < max_areaTH: # При условии что объект больше заданного  начале происходит отслеживание
            # Вычисление Момента изображения, т.е. суммарной характеристики контура(площади или длины)
            M = cv2.moments(cnt)
            cx = int(M['m10']/M['m00']) # Сохранияем крайние точки
            cy = int(M['m01']/M['m00'])
            x,y,w,h = cv2.boundingRect(cnt) # получаем координаты прямоугольника

            #Проверка всех обнаруженных контуров.
            new = True
            # Работа с ранее обнаружеранее объектами
            for i in persons:
                # Если объект близок с предыдущим уже найденым объектом, то это один объект
                if abs(cx-i.getX()) <= w and abs(cy-i.getY()) <= h:
                    new = False
                    i.updateCoords(cx,cy) # Обновляем координаты объекта, проверяем пересек ли он линии

                    date_now = datetime.now()
                    # Если объек прошел через проверочные линии
                    if i.going_UP(line_down, line_up) == True:
                        cnt_up += 1;
                        # Записываем в лог файл чтобы далее оперировать этими данными. Файлы так составлены чтобы их смогла прочитать 1С
                        print ("Person crossed going up at", str(date_now.strftime("%d.%m.%Y")) )
                        if not Save_log(i.dir,date_now):
                            print("Logfile save error")
                        break
                        
                    elif i.going_DOWN(line_down, line_up) == True:
                        cnt_down += 1;
                        print ("Person crossed going down at", str(date_now.strftime("%d.%m.%Y")) )
                        if not Save_log(i.dir,date_now):
                            print("Logfile save error")
                        break
              

                # Удаляем экземпляр из отслеживания если работа с ними закончена
                if i.timedOut():
                    index = persons.index(i)
                    persons.pop(index)
                    del i

            # Если обнаружен новый объект
            if new == True:
                p = Person.MyPerson(cx,cy) # создаем новый экземпляр класса
                persons.append(p) # добавляем новый объект в отслеживание

            cv2.circle(frame,(cx,cy), 5, (0,0,255), -1) # ставим красную точку в центре зоны
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2) # строим квадрат вокруг объекта
            # cv2.drawContours(frame, cnt, -1, (0,255,0), 3) # Выделяем цветом контур объекта
            iteration_counter = 0 # Обнуляем счетчик итераций при появлении нового объекта
        else:
            iteration_counter +=1; #Считаем итерации для обновления
            #print("Strange object!" + str(iteration_counter))
            if iteration_counter > 10000: # Если какой-то объект, не подходящий по размерам под искомый объект, например световое пятно, держится больше 10к кадров, то обновляем маску
                ret, mask_frame = cap.read()
                iteration_counter = 0

    # Рисуем на кадре все линии, надписи и так далее
    str_up = 'UP: '+ str(cnt_up)
    str_down = 'DOWN: '+ str(cnt_down)
    frame = cv2.polylines(frame,[pts_L1], False, line_down_color, thickness=2)
    frame = cv2.polylines(frame,[pts_L2], False, line_up_color,thickness=2)
    # Добавляем надписи на кадры
    cv2.putText(frame, str_up, (10,40), font, 0.5, (255,255,255), 2, cv2.LINE_AA)
    cv2.putText(frame, str_up, (10,40),font, 0.5, (0,0,255), 1, cv2.LINE_AA)
    cv2.putText(frame, str_down, (10,90), font, 0.5, (255,255,255), 2, cv2.LINE_AA)
    cv2.putText(frame, str_down, (10,90), font, 0.5, (255,0,0), 1, cv2.LINE_AA)

    # отображаем в окне работу нашего алгоритма
    #cv2.imshow('Frame',frame)
    cv2.imshow('Panel',frame)

    # Считываем с клавиатуры клавиши
    k = cv2.waitKey(30) & 0xff
    if k == 27: # По нажатию ESC закрываем программу
        break
    elif k == 32: # По нажатию пробела обновляем кадр и сбрасываем счетчики
        ret, mask_frame = cap.read()
        cnt_up = 0
        cnt_down = 0

cap.release() # Заканчиваем работу с видеорядом с камеры
cv2.destroyAllWindows() # Закрываем все окна
