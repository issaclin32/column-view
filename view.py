import numpy as np
import cv2


def handle_mouse_click(event, x, y, flags, param) -> None:
    global mouse_x
    global mouse_y
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x, mouse_y = x, y
        return
    else:
        return


if __name__ == '__main__':
    img = cv2.imread('img\\01.jpg')
    img = cv2.resize(img, (400, 300))
    img_h, img_w = img.shape[0:2]

    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 強制轉成灰階

    # 狀態初始值
    current_x = 0
    current_y = 0
    # 如果為 True, 則以 95th 百分比、5th 百分比為圖表最大最小值
    # 否則用極值作為圖表最大最小值
    FLAG_exclude_outliers: bool = False
    FLAG_exclude_pupil: bool = False

    cursor_hover_pixel_value = -1

    # --- 瞳孔、亮點範圍 ---
    PUPIL_COLOR_RANGE = [80, 84]

    instructions="""<controls>
    
        W: move up
        S: move down
        A: move left
        D: move right
        
        F: exclude outliers (values <5% and >95% percentage)
        G: exclude pupil
        
        ESC: quit
    """

    print(instructions)

    while True:
        # --- img_visualize ---
        img_visualize = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        # --- 目前位置指標 ---
        cv2.line(img_visualize, (current_x, 0), (current_x, img_h-1), (0,255,255), 1)
        cv2.circle(img_visualize, (current_x, current_y), 2, (255,255,0), -1)

        # --- 把瞳孔塗成藍色 ---
        if FLAG_exclude_pupil:
            ignore_list_pupil = np.where(np.logical_and(img >= 80, img <= 84))
            img_visualize[ignore_list_pupil] = (255, 0, 0)
            #include_list_pupil = np.where(np.logical_not(np.logical_and(img >= 80, img <= 84)))

        # --- 目前這一行 (current column) 的統計資料 ---
        pixels_of_current_column = img[:, current_x]
        column_max = np.max(pixels_of_current_column)
        column_min = np.min(pixels_of_current_column)
        column_avg = np.average(pixels_of_current_column)
        column_stdev = np.std(pixels_of_current_column)

        if FLAG_exclude_pupil:
            pass

        tmp_sorted_pixels = sorted(list(pixels_of_current_column))

        column_percentile_5th = tmp_sorted_pixels[int(img_h*0.05-1)]
        column_percentile_95th = tmp_sorted_pixels[int(img_h*0.95-1)]

        # --- panel: 寬 700px, 高 600px ---
        TEXT_WIDTH: int = 1
        GRAPH_TEXT_WIDTH: int = 2

        panel = np.full((600, 700, 3), 255, dtype=np.uint8)
        cv2.putText(panel, f'current column (X): {current_x}', (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), TEXT_WIDTH)
        cv2.putText(panel, f'current row (Y): {current_y}', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), TEXT_WIDTH)
        cv2.putText(panel, f'value(V) of current pixel: {img[current_y, current_x]}', (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), TEXT_WIDTH)

        cv2.putText(panel, '<analysis of current column>', (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), TEXT_WIDTH)
        cv2.putText(panel, f'min:{column_min:.2f}  max:{column_max:.2f}', (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), TEXT_WIDTH)
        cv2.putText(panel, f'avg:{column_avg:.2f}  stdev:{column_stdev:.2f}', (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), TEXT_WIDTH)
        cv2.putText(panel, f'5th percentile:{column_percentile_5th:.2f}', (20, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), TEXT_WIDTH)
        cv2.putText(panel, f'95th percentile:{column_percentile_95th:.2f}', (20, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), TEXT_WIDTH)

        # 滑鼠移過的地方的 pixel value
        if cursor_hover_pixel_value != -1:
            cv2.putText(panel, f'pixel value: {cursor_hover_pixel_value}', (500, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), GRAPH_TEXT_WIDTH)

        # 圖表 (630x260 px)
        graph_w, graph_h = 630, 260
        graph_x, graph_y = 20, 320  # 圖表起始位置

        # 圖表 X, Y 軸
        cv2.line(panel, (graph_x, graph_y+graph_h), (graph_x+graph_w, graph_y+graph_h), (0,0,0), 1)
        cv2.line(panel, (graph_x, graph_y), (graph_x+graph_w, graph_y), (0,0,0), 1)
        cv2.line(panel, (graph_x, graph_y), (graph_x, graph_y+graph_h), (0,0,0), 1)

        # 顯示圖表最大最小值
        if FLAG_exclude_outliers:
            cv2.putText(panel, f'{column_percentile_5th:.2f} (5%)', (10, 580), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), GRAPH_TEXT_WIDTH)
            cv2.putText(panel, f'{column_percentile_95th:.2f} (95%)', (10, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), GRAPH_TEXT_WIDTH)
        else:
            cv2.putText(panel, f'{column_min:.2f} (min)', (10, 580), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), GRAPH_TEXT_WIDTH)
            cv2.putText(panel, f'{column_max:.2f} (max)', (10, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), GRAPH_TEXT_WIDTH)

        DOT_SIZE: int = 1  # 1 -- 邊緣多加 1 個 pixel (= 3 pixel寬)
        prev_dot_x, prev_dot_y, prev_value = 0, 0, 0

        for y in range(img_h):
            dot_x = int(graph_x + graph_w*(y/img_h))

            if FLAG_exclude_outliers:
                dot_y = int(graph_y + graph_h - ((img[y, current_x]-column_percentile_5th)/(column_percentile_95th-column_percentile_5th))*graph_h)
            else:
                dot_y = int(graph_y + graph_h - ((img[y, current_x]-column_min)/(column_max-column_min))*graph_h)

            if y == current_y:
                panel[dot_y-DOT_SIZE-2: dot_y+DOT_SIZE+3, dot_x-DOT_SIZE-2: dot_x+DOT_SIZE+3] = (0, 255, 0)
            elif FLAG_exclude_outliers and (img[y, current_x] > column_percentile_95th or img[y, current_x] < column_percentile_5th):
                panel[dot_y-DOT_SIZE: dot_y+DOT_SIZE+1, dot_x-DOT_SIZE: dot_x+DOT_SIZE+1] = (160,160,160)
            else:
                panel[dot_y-DOT_SIZE: dot_y+DOT_SIZE+1, dot_x-DOT_SIZE: dot_x+DOT_SIZE+1] = (0, 0, 255)

            if 0 < y < img_h-1:
                if FLAG_exclude_outliers:
                    if (column_percentile_5th <= prev_value <= column_percentile_95th) and (column_percentile_5th <= img[y, current_x] <= column_percentile_95th):
                        cv2.line(panel, (prev_dot_x, prev_dot_y), (dot_x, dot_y), (0, 0, 255), 2)
                else:
                    cv2.line(panel, (prev_dot_x, prev_dot_y), (dot_x, dot_y), (0, 0, 255), 2)

            if FLAG_exclude_outliers:
                if column_percentile_5th <= img[y, current_x] <= column_percentile_95th:
                    prev_dot_x, prev_dot_y = dot_x, dot_y
                    prev_value = img[y, current_x]
            else:
                prev_dot_x, prev_dot_y = dot_x, dot_y


        cv2.imshow('Column View', np.hstack((cv2.resize(img_visualize, (800, 600)), panel)))
        cv2.setMouseCallback('Column View', handle_mouse_click)
        uin = cv2.waitKey(33)  # uin: user input

        # handle mouse inputs
        global mouse_x
        if 'mouse_x' in globals() and mouse_x is not None:
            if mouse_x <= 800:
                cursor_hover_pixel_value = img[mouse_y//2-1, mouse_x//2-1]
            mouse_x = None

        # handle keyboard inputs
        if uin == 27: # ESC
            exit(0)
        elif uin == ord('a'):
            if current_x > 0:
                current_x -= 1
        elif uin == ord('d'):
            if current_x < img_w - 1:
                current_x += 1
        elif uin == ord('w'):
            if current_y > 0:
                current_y -= 1
        elif uin == ord('s'):
            if current_y < img_h - 1:
                current_y += 1
        elif uin == ord('f'):
            FLAG_exclude_outliers = not FLAG_exclude_outliers
        elif uin == ord('g'):
            FLAG_exclude_pupil = not FLAG_exclude_pupil
        else:
            pass