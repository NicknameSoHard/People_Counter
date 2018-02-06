## Сreated by HydroslidE
## Source: https://github.com/NicknameSoHard/People-Detect-OpenCV
import numpy as np
import cv2, time
import Person
#Счетчики входа и выхода
cnt_up   = 0
cnt_down = 0

#Захват видео
cap = cv2.VideoCapture("http://192.168.1.35//video.cgi")
if not cap.isOpened(): #Подключение по айпи, если не удается, то попытка переключения на камеру по умолчанию
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print( "Video Capture error: Can't find camera")
    else:
        w = cap.get(3)
        h = cap.get(4)
        areaTH = (h*w)/250 # Делим высоту и длину кадра на выбранный коэфициент. Его мы подбираем из соображений наилучшего обнаружения
        print ('Area Threshold', areaTH) #Область захвата

        #Заранее расчитываем все параметры для построения линий на изображении
        line_down = int(3*(h/5)) # Строим линию на уровне 3\5 Экрана
        print ("Red line y:",str(line_down) ) # Выводим в консольно координату по высоте
        pt1 =  [0, line_down]; # координаты крайних точек линий" линии
        pt2 =  [w, line_down];
        pts_L1 = np.array([pt1,pt2], np.int32) # собираем все в матрицу
        pts_L1 = pts_L1.reshape((-1,1,2)) # трансформирует матрицу чисел по виду 1 строка, 2 столбика для дальнейшей работы.
        line_down_color = (255,0,0) # Задаем цвет линии

        line_up = int(2*(h/5)) # Аналогичные операции для 2\5 экрана
        print ("Blue line y:", str(line_up) )
        pt3 =  [0, line_up];
        pt4 =  [w, line_up];
        pts_L2 = np.array([pt3,pt4], np.int32)
        pts_L2 = pts_L2.reshape((-1,1,2))
        line_up_color = (0,0,255)

        up_limit =  int(1*(h/5)) # для 1\5 экрана
        pt5 =  [0, up_limit];
        pt6 =  [w, up_limit];
        pts_L3 = np.array([pt5,pt6], np.int32)
        pts_L3 = pts_L3.reshape((-1,1,2))

        down_limit = int(4*(h/5)) # для 4\5 экрана
        pt7 =  [0, down_limit];
        pt8 =  [w, down_limit];
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

        ret, frame = cap.read() # Считываем изображение для сравнения
        prvs = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) # Переводим его в серые оттенки

        while(cap.isOpened()): # Пока камера передает изображения
            ret, frame = cap.read() #Считываем изображение с камеры
            next = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) # Перевод в оттенки серого
        #    fgmask = fgbg.apply(frame) #Применяем вычитание фона
            try:
                flow = cv2.calcOpticalFlowFarneback( #Вычисляет оптический поток, используя алгоритм Гуннара Фарнебака
                    prvs, # Предыдущий кадр
                    next, # Следующий кард
                    None, # Вычисление изображения потока
                    0.5, # Масштаб изображения. 0.5 - классическая пирамида
                    3, # Количество уровней пирамиды, включая начальное изображение
                    15, # Средний размер окна. Большие значения увеличивают ошибкоустойчивость алгоритма, но выдают более размытую область движения.
                    3, # Количество итераций алгоритма на каждом уровне пирамиды
                    5, # Размер окрестностей пикселей для нахождения расширенного полиномиала. Большие значения дают сглаженные края.
                    1.2, # Стандартное отклонение Гауссиана, которое используется для сглаживания в polyN.
                    0) # Доп флаги. Нам они не требуются

                horz = flow[..., 0] # Оптический поток возвращает результат в виде двух наборов точек, которые "двигались"
                vert = flow[..., 1] # По горизонтали и вертикали соответствено
                fgmask   = horz.astype('uint8')+ vert.astype('uint8') # Преобразуем типы в unsigned integer 8 и соединим оба потока в один

                ret,imBin= cv2.threshold(fgmask,1,255,cv2.THRESH_BINARY) # Для более четкого восприятия переводим все цвета белый, а фон оставляем черным
                mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernelOp) #"Открытие" морфологической трансформирмации. Позволяет удалить посторонние шумы вокруг объекта.
                mask =  cv2.morphologyEx(mask , cv2.MORPH_CLOSE, kernelCl) #"Закрытие" м.т для закраски областей внутри объекта.
            except:
                # При возникновении любой ошибки завершать выполнение программы
                print('Algorinm error')
                print ('UP:',cnt_up)
                print ('DOWN:',cnt_down )
                break

            img_, contours0, hierarchy_ = cv2.findContours( #Ищем контуры на изображении
                mask, #Бинарное изображение, где ищутся контуры
                cv2.RETR_EXTERNAL, # Извлекает только крайние внешние контуры. Контур ребенка сольется с фоном\родителем
                cv2.CHAIN_APPROX_SIMPLE) # Сжимает все сегменты контура и оставляет только крайние точки.

            for cnt in contours0: # Для каждого контура
                area = cv2.contourArea(cnt) # Вычисляет положение контура
                # При условии что объект больше заданного в начале происходит отслеживание
                if area > areaTH:
                    M = cv2.moments(cnt) # Вычисление Момента изображения, т.е. суммарной характеристики контура(площади или длины).
                    cx = int(M['m10']/M['m00']) # Сохранияем крайние точки
                    cy = int(M['m01']/M['m00'])
                    x,y,w,h = cv2.boundingRect(cnt) # получаем координаты прямоугольников

                    #Проверка всех обнаруженных контуров.
                    new = True
                    if cy in range(up_limit,down_limit): # Для объектов в области отслеживания
                        # Работа с уже обнаруженными ранее объектами
                        for i in persons:
                            # Если объект все еще в поле зрения камеры
                            if abs(cx-i.getX()) <= w and abs(cy-i.getY()) <= h:
                                new = False
                                i.updateCoords(cx,cy) # Обновляем координаты объекта

                                # Если объек прошел через проверочные линии
                                if i.going_UP(line_down,line_up) == True:
                                    cnt_up += 1;
                                    print ('Crossed going up at',time.strftime("%c") )
                                elif i.going_DOWN(line_down,line_up) == True:
                                    cnt_down += 1;
                                    print ('Crossed going down at',time.strftime("%c") )
                                break

                            # Если объект выходит за пределы области отслеживания(т.е. уже пересек линию)
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

            cv2.imshow('Frame',frame) # отображаем работу нашего алгоритма
            prvs = next #Сохраняем кадр как предыдущий

            #Закрыться по нажатию ESC
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break

cap.release() # Заканчиваем работу с видеорядом с камеры
cv2.destroyAllWindows() # Закрываем все окна
