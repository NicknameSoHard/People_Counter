##Создано Federico Mejia, доработка ведется HydroslidE
import numpy as np
import cv2, time
import Person

#Счетчики входа и выхода
cnt_up   = 0
cnt_down = 0

#Захват видео
cap = cv2.VideoCapture("http://192.168.0.56//video.cgi")
if not cap.isOpened(): #Подключение по айпи, если не удается, то попытка переключения на камеру по умолчанию
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print( "Video Capture error: Can't find camera.")

#cap.set(3,640) #set width
#cap.set(4,480) #set height
LL=40
HH=3
ww = cap.get(3)
hh = cap.get(4)
res=(hh*ww)
min_areaTH = res / LL # Делим высоту и длину кадра на выбранный коэфициент. Его мы подбираем из соображений наилучшего обнаружения
print ('Min area Threshold', min_areaTH) # Размер объекта

max_areaTH = res / HH
print ('Max area Threshold', max_areaTH) #
#Заранее расчитываем все параметры для построения линий на изображении



line_down = int(3*(hh/5)) # Строим линию на уровне 3\5 Экрана
memd=line_down
print ("Red line y:",str(line_down) ) # Выводим в консольно координату по высоте
pt1 =  [0, line_down]; # координаты крайних точек линий" линии
pt2 =  [ww, line_down];
pts_L1 = np.array([pt1,pt2], np.int32) # собираем все в матрицу
pts_L1 = pts_L1.reshape((-1,1,2)) # трансформирует матрицу чисел по виду 1 строка, 2 столбика для дальнейшей работы.
line_down_color = (255,0,0) # Задаем цвет линии

line_up = int(2*(hh/5)) # Аналогичные операции для 2\5 экрана
memt=line_up
print ("Blue line y:", str(line_up) )
pt3 =  [0, line_up];
pt4 =  [ww, line_up];
pts_L2 = np.array([pt3,pt4], np.int32)
pts_L2 = pts_L2.reshape((-1,1,2))
line_up_color = (0,0,255)

up_limit =  int(1*(hh/5)) # для 1\5 экрана
pt5 =  [0, up_limit];
pt6 =  [ww, up_limit];
pts_L3 = np.array([pt5,pt6], np.int32)
pts_L3 = pts_L3.reshape((-1,1,2))

down_limit = int(4*(hh/5)) # для 4\5 экрана
pt7 =  [0, down_limit];
pt8 =  [ww, down_limit];
pts_L4 = np.array([pt7,pt8], np.int32)
pts_L4 = pts_L4.reshape((-1,1,2))

#Создаем объект субстрактора для дальнейшего поиска объектов
#fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows = False)

#Структурируем элементы морфографических фильтров
kernelOp = np.ones((3,3),np.uint8) # Создает новый массив заданного размера и типа(В данном случае восьмибитный unsigned int)
kernelOp2 = np.ones((5,5),np.uint8)
kernelCl = np.ones((11,11),np.uint8)

#Переменные для дальнейшей работы
font = cv2.FONT_HERSHEY_SIMPLEX # Задаем шрифты для корректного отображения текста. Векторные шрифты Херши распространены за счет легкого преобразования в любую плоскость, угол и так далее.
persons = [] # Создаем массив для детектора движения

#Объявление ползунков
Panel = np.zeros([100,500], np.uint8)
cv2.namedWindow("Panel")
def nothing(x):
    pass
cv2.createTrackbar("THRSH_MIN", "Panel", 30, 255, nothing)
cv2.createTrackbar("THRSH_MAX", "Panel", 255, 255, nothing)
cv2.createTrackbar("MAX OBJ", "Panel", 252, 255, nothing)
cv2.createTrackbar("MIN OBJ", "Panel", 215, 255, nothing)
cv2.createTrackbar("DWN_LINE", "Panel", 48, int(hh/2), nothing)
cv2.createTrackbar("TOP_LINE", "Panel", 192, int(hh/2), nothing)

ret, prevframe = cap.read()
while(cap.isOpened()): # Пока камера передает изображения
    ret, frame = cap.read()  #Считываем изображение с камеры
    frameABS =  cv2.absdiff(frame, prevframe) # Производим чистое вычитание из "первого" кажра текущего. Таким образом, имея эталонный кадр без движения мы получим в разнице все движение на кадре.
    cv2.imshow("Panel", Panel)
#    cv2.imshow('ADS',frameABS)
    fgmask = grayABS = cv2.cvtColor(frameABS, cv2.COLOR_BGR2GRAY) # Переводим результат вычитания в оттенки серого

# Работа с ползунками

    TRSHL=cv2.getTrackbarPos("THRSH_MIN", "Panel")
    TRSHH=cv2.getTrackbarPos("THRSH_MAX", "Panel")
    LL=cv2.getTrackbarPos("MIN OBJ", "Panel")
    HH=cv2.getTrackbarPos("MAX OBJ", "Panel")
    DWNL=cv2.getTrackbarPos("DWN_LINE", "Panel")
    TOPL=cv2.getTrackbarPos("TOP_LINE", "Panel")
    min_areaTH = res / (255-LL+1)
    max_areaTH = res / (255-HH+1)
    line_down = int((hh / 2)+DWNL)
    line_up = int(TOPL)
    if (memd != line_down):
        memd=line_down
        print("Red line y:", str(line_down))  # Выводим в консольно координату по высоте
        pt1 = [0, line_down];  # координаты крайних точек линий" линии
        pt2 = [ww, line_down];
        pts_L1 = np.array([pt1, pt2], np.int32)  # собираем все в матрицу
        pts_L1 = pts_L1.reshape((-1, 1, 2))  # трансформирует матрицу чисел по виду 1 строка, 2 столбика для дальнейшей работы.
        line_down_color = (255, 0, 0)  # Задаем цвет линии

    if (memt != line_up):
        memt = line_up
        print("Blue line y:", str(line_up))
        pt3 = [0, line_up];
        pt4 = [ww, line_up];
        pts_L2 = np.array([pt3, pt4], np.int32)
        pts_L2 = pts_L2.reshape((-1, 1, 2))
        line_up_color = (0, 0, 255)

        
#    fgmask = fgbg.apply(grayABS) #Применяем вычитание фона субстрактором
    cv2.imshow('Fgmask',fgmask)
    try:
        ret,imBin= cv2.threshold(fgmask, TRSHL, TRSHH,cv2.THRESH_BINARY)  # Бинаризация изображения (Перевод изображний в черно-белые оттенки)
#        cv2.imshow('threshold',imBin)
        mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernelOp)   #"Открытие" Морфологической трансформирмации (эрозия -> растяжение). Позволяет удалить посторонние шумы вокруг объекта.
        mask =  cv2.morphologyEx(mask , cv2.MORPH_CLOSE, kernelCl)  #"Закрытие" (растяжение -> эрозия) для соединения областей внутри объекта.
#        fmask = cv2.GaussianBlur(mask, (3,3), -1)
        cv2.imshow('morphologyEx', mask )
    except:
        # При возникновении любой ошибки завершать выполнение программы
        print('EOF')
        print ('UP:',cnt_up)
        print ('DOWN:',cnt_down )
        break

    img_, contours0, hierarchy_ = cv2.findContours( #Ищем контуры на изображении
        mask, #Бинарное изображение, где ищутся контуры
        cv2.RETR_EXTERNAL, # Извлекает только крайние внешние контуры. Контур ребенка сольется с фоном\родителем
        cv2.CHAIN_APPROX_SIMPLE) # Сжимает все сегменты контура и оставляет только крайние точки.

    for cnt in contours0: # Для каждого контура
        area = cv2.contourArea(cnt) # Вычисляет положение контура
        if area > min_areaTH and area < max_areaTH: # При условии что объект больше заданного  начале происходит отслеживание
            # Вычисление Момента изображения, т.е. суммарной характеристики контура(площади или длины).
            M = cv2.moments(cnt)
            cx = int(M['m10']/M['m00']) # Сохранияем крайние точки
            cy = int(M['m01']/M['m00'])
            x,y,w,h = cv2.boundingRect(cnt) # получаем координаты прямоугольника

            #Проверка всех обнаруженных контуров.
            new = True
            if cy in range(up_limit,down_limit): # Для объектов в области отслеживания
                # Работа с уже обнаруженными ранее объектами
                for i in persons:
                    # Если объект близок с предыдущим уже найденым объектом
                    if abs(cx-i.getX()) <= w and abs(cy-i.getY()) <= h:
                        new = False
                        i.updateCoords(cx,cy) # Обновляем координаты объекта

                        # Если объек прошел через проверочные линии
                        if i.going_UP(line_down,line_up) == True:
                            cnt_up += 1;
                            print ("Person crossed going up at",time.strftime("%c") )
                        elif i.going_DOWN(line_down,line_up) == True:
                            cnt_down += 1;
                            print ("Person crossed going down at",time.strftime("%c") )
                        break

                    # Если объект выходит за пределы области отслеживания, то меняем его статус отслеживания
                    if i.getState() == '1':
                        if i.getDir() == 'down' and i.getY() > down_limit:
                            i.setDone()
                        elif i.getDir() == 'up' and i.getY() < up_limit:
                            i.setDone()

                    # Удаляем экземпляр из отслеживания
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
            #cv2.drawContours(frame, cnt, -1, (0,255,0), 3) # Выделяем цветом контур объекта

    # Рисуем на кадре все линии, надписи и так далее
    str_up = 'UP: '+ str(cnt_up)
    str_down = 'DOWN: '+ str(cnt_down)
    frame = cv2.polylines(frame,[pts_L1],False,line_down_color,thickness=2)
    frame = cv2.polylines(frame,[pts_L2],False,line_up_color,thickness=2)
    frame = cv2.polylines(frame,[pts_L3],False,(255,255,255),thickness=1)
    frame = cv2.polylines(frame,[pts_L4],False,(255,255,255),thickness=1)
    cv2.putText(frame, str_up ,(10,40),font,0.5,(255,255,255),2,cv2.LINE_AA)
    cv2.putText(frame, str_up ,(10,40),font,0.5,(0,0,255),1,cv2.LINE_AA)
    cv2.putText(frame, str_down ,(10,90),font,0.5,(255,255,255),2,cv2.LINE_AA)
    cv2.putText(frame, str_down ,(10,90),font,0.5,(255,0,0),1,cv2.LINE_AA)

    # отображаем наглядно работу нашего алгоритма
    cv2.imshow('Frame',frame)

    #Закрыться по нажатию ESC
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release() # Заканчиваем работу с видеорядом с камеры
cv2.destroyAllWindows() # Закрываем все окна
