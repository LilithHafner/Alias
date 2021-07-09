import numpy as np
from time import time
from pynput.mouse import Button, Controller, Listener
import cv2 as cv
from threading import Thread
from skimage.draw import line
#from skimage import morphology

shape = (1300, 2000, 3)
sz = 50
blocks = [[sz*3,sz*3,sz,sz,220,0,0],
          [sz*3,shape[1]/2,sz,sz,128,128,128],
          [sz*3,shape[1]-sz*3,sz,sz,0,200,200]]

static = len(blocks)
above = [[50,50,1,10,255,255,255], [70,70,10,1,255,255,255]]
def pint(x):
    return max(0, int(x))
def render():
    global display_queued
    global display
    if not display_queued:
        buffer = np.zeros(shape, dtype=np.uint8)
        for b in blocks + above:
            for b2 in b[7:]:
                d = np.hypot(b[0]-b2[0], b[1]-b2[1])
                dy, dx = (b[1]-b2[1])/d, (b2[0]-b[0])/d
                for k in [-2, -1, 0, 1, 2]:
                    y,x = line(pint(b[0]+k*dy), pint(b[1]+k*dx), pint(b2[0]+k*dy), pint(b2[1]+k*dx))
                    mask = (y >= 0) & (x >= 0) & (y < shape[0]) & (x < shape[1])
                    buffer[y[mask],x[mask]] = 255
##                    if yxvs:
##                        ys,xs,vals = zip(*yxvs)
##                        vals = np.array(vals).reshape(len(vals),1)
##                        if abs(k) != 2.53:
##                            vals[:] = 1
##                        buffer[ys,xs] = vals*255
        for b in blocks + above:
            for c in range(3):
                buffer[pint(b[0]-b[2]):pint(b[0]+b[2]),pint(b[1]-b[3]):pint(b[1]+b[3]),c] = b[4+c]
        #for i in range(3):
        #    buffer[:,:,i] = morphology.dilation(buffer[:,:,i], morphology.disk(radius=3))
        display = buffer
        #print(len(blocks))
        display_queued = True

def to_coords(x,y):
    return ((y-54.3)*2,x*2)
last_time = time()

def remove_edges_to(block):
    for b in blocks:
        b[7:] = [i for i in b[7:] if i != block]

def on_move(x, y):
    y,x = to_coords(x,y)
    #print('Pointer moved to {0}'.format(
    #    (y, x)))
    for i in range(2):#Cross hairs
        above[i][0:2] = y,x
    global last_time, line_accumulation
    dt = time()-last_time
    last_time += dt
    if offset:
        blocks[-1][0:2] = y+offset[0], x+offset[1]
        if blocks[-1][0] < 0 or blocks[-1][1] < 0 or blocks[-1][0] > shape[0] or blocks[-1][1] > shape[1]:
            remove_edges_to(blocks[-1])
            while len(blocks[-1]) > 7:
                blocks[-1].pop()
        distance, b = min([(np.inf,None)]+[(max(abs(blocks[-1][0]-b[0])/blocks[-1][2], abs(blocks[-1][1]-b[1])/blocks[-1][3]), b) for b in blocks[static:-1]])
        max_dist = 1.7
        min_time = .1
        max_time = .3
        if distance < max_dist:
            value = dt/max_time/(min_time/max_time+(1-min_time/max_time)*(distance/max_dist)**2)
            if not line_accumulation or line_accumulation[0] != b:
                line_accumulation = [b,value]
            else:
                line_accumulation[1] += value
                
            if line_accumulation[1] >= 1 and b not in blocks[-1]:
                blocks[-1].append(b)
                print('\a',end='',flush=True)
        else:
            line_accumulation = None
                
                
        
    #print(blocks)
    render()

offset = None
line_accumulation = None
def on_click(x, y, button, pressed):
    y,x = to_coords(x,y)
    global offset
    if pressed:
        for i,b in list(enumerate(blocks))[::-1]:
            if abs(y-b[0])<b[2] and abs(x-b[1]) < b[3]:
                offset = b[0]-y, b[1]-x
                if i >= static:
                    blocks.append(blocks.pop(i))
                else:
                    blocks.append(list(b))
                
                break
    else:
        offset = None
        line_accumulation = None
        if blocks[-1][0] < 0 or blocks[-1][1] < 0 or blocks[-1][0] > shape[0] or blocks[-1][1] > shape[1]:
            remove_edges_to(blocks.pop())
            
        
    #print('{0} at {1}'.format(
    #    'Pressed' if pressed else 'Released',
    #    (x, y)))
    render()
    #if not pressed:
    #    pass
        # Stop listener
        #return False

def on_scroll(x, y, dx, dy):#Unused
    #print('Scrolled {0}'.format(
    #    (x, y)))
    pass

listener = Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll)
listener.start()
Thread(target=listener.join).start()

##Display
stop = False##Access point
display_queued = True##Access point
display = np.zeros(shape, dtype=np.uint8)##Access point
def show():
    print("Show started!")
    global stop
    global display_queued
    try:
        while not stop:
            if display_queued:
                display_queued = False
                cv.imshow("GUI", display)
                #print("Shown")
            cv.waitKey(5)
            #if cv.waitKey(5) != -1:
            #    break
    finally:
        cv.destroyAllWindows()
        listener.stop()
        stop = True
    print("Show stopped!")

show()
##Input
# Collect events until released








##Old drafts
'''
        for i in range(1000):
            frame[np.random.randint(0,200),np.random.randint(0,200),np.random.randint(0,2)] = np.random.randint(0,255)




#try:
while True:
    frame = np.zeros(shape, dtype=np.uint8)
    for b in blocks:
        for c in range(3):
            frame[b[0]-b[2]:b[0]+b[2],b[1]-b[2]:b[1]+b[2],c] = b[3+c]
                
#        cv.imshow("GUI", frame)
#        if cv.waitKey(1) != -1:
#            break
        

#finally:
#    cv.destroyAllWindows()




'''
