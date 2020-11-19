"""
The following program creates the old game breakout; where the user controls
a paddle at the bottom of the screen, and bounces a ball up and clears individual bricks
until the ball exits the screen.

Future Implementation:
-add side bounce for bricks
-add mode where game ends when all bricks are knocked off the scren
"""

import time
import tkinter
import math
import random

# Constants
BALL_DIAMETER=10
CANVAS_HEIGHT=500
CANVAS_WIDTH=500
BRICK_LAYER=9
N_BRICK_PER_LAYER=10
BRICK_HEIGHT=20
PADDLE_WIDTH=100
PADDLE_HEIGHT=5
SPEED=6 # norm of [dx,dy] should be equal to SPEED
brick_width=CANVAS_WIDTH/N_BRICK_PER_LAYER



def main():
    canvas = make_canvas(CANVAS_WIDTH,CANVAS_HEIGHT,"Breakout")
    canvas.configure(background='black')
    ball,brick_list,paddle,dx,dy,end_flag = initialize_game(canvas)


    while True:
        paddle=draw_paddle(canvas,paddle)
        canvas.move(ball,dx,dy)
        dx,end_flag = Edge_Collision_Check(dx,canvas,ball)
        dx,dy = Paddle_Collision_Check(dx,dy,canvas,paddle,ball)

        if canvas.coords(ball)[1] < CANVAS_HEIGHT/2:
            #start checking brick collision when ball is on top half of screen
            dx,dy=Brick_Collision_Check(canvas,brick_list,dx,dy)

        canvas.update()
        time.sleep(1/60.)



def initialize_game(canvas):
    """
    The following function initializes the game by:
    1.) drawing the paddle and bricks
    2.) selects a random firing trajectory for the ball
    arg:
        canvas
    return:
        ball
        brick_list=list of brick graphic element
        paddle
        dx=x change
        dy=y change
        end_flag= flag indicating state of game. 0 = ongoing, 1 = win, -1 = lose
    """


    ball = draw_ball(canvas)
    brick_list=draw_bricks(canvas)
    paddle = initialize_paddle(canvas)

    dy=random.uniform(SPEED/4.,SPEED/2.)
    dx=math.sqrt(SPEED**2 - dy**2)
    end_flag = 0
    return ball,brick_list,paddle,dx,dy,end_flag



def Brick_Collision_Check(canvas,brick_list,dx,dy):
    """
    This function checks if the ball collided with the array of bricks on the top of the screen.
    arg:
        canvas
        brick_list by reference
        dx
        dy
    return:
        updated dx and dy
    """
    for i in range(len(brick_list)):
        x1,y1,x2,y2=canvas.coords(brick_list[i])
        contact_list=canvas.find_overlapping(x1,y1,x2,y2)
        if len(contact_list)==2:
            dy=dy*-1
            canvas.delete(brick_list[i])
            brick_list.remove(brick_list[i])
            break

    return dx,dy



def draw_bricks(canvas):
    """
    This function draws the array of bricks on the top of the screen. Returns the list of bricks
    """
    brick_list=[]
    for i in range(BRICK_LAYER):
        for j in range(N_BRICK_PER_LAYER):
            x1=j*brick_width+j
            y1=i*BRICK_HEIGHT+i
            x2=(j+1)*brick_width+j
            y2=(i+1)*BRICK_HEIGHT+i
            brick_list.append(canvas.create_rectangle(x1,y1,x2,y2,fill='green',outline='white'))

    return brick_list


def initialize_paddle(canvas):
    """
    This function initializes the paddle based on current mouse location at start of game
    """
    mouse_x=canvas.winfo_pointerx()
    paddle=canvas.create_rectangle(mouse_x-PADDLE_WIDTH/2,CANVAS_HEIGHT-PADDLE_HEIGHT,mouse_x+PADDLE_WIDTH/2,
                            CANVAS_HEIGHT,fill='red',outline='white')
    return paddle

def draw_ball(canvas):
    """
    This function draws the ball at a random location at the center height of the screen
    """
    x1=random.randint(0,CANVAS_WIDTH-BALL_DIAMETER)
    y1=CANVAS_HEIGHT/2
    x2=x1+BALL_DIAMETER
    y2=y1+BALL_DIAMETER
    ball = canvas.create_oval(x1,y1,x2,y2,fill='red',outline='red')
    return ball



def Paddle_Collision_Check(dx,dy,canvas,paddle,ball):
    """
    This function checks if the ball collided with the paddle and makes necessary adjustment to its speed.
    When collision occurs, dy flips signs. dx will be altered based on location that the ball met the paddle
        1.) ball hit paddle left, go left
        2.) ball hit paddle right, go right
        angle will also change depending how far from the edge contact was made

    Algorithm for collision:
        Bricks and side walls are neutral objects. Meaning angle of bounce will not change when contact is made.
        On the other hand, paddle contact will change angle of bounce. It will do so in the following manner:
            at contact, the distance from center of paddle to ball (dH) is measured. Farther from center => larger dH
            will result in more oblique bounce. Smaller dH will result in more straight up/down bounce. The range of
            of bounce angle will be from 20 degrees to 85 degrees.

    arguments:
        dx=previous change_x
        dy=previous change_y
        canvas
        paddle
    returns:
        dx=new dx
        dy=new dy
    """
    x1,y1,x2,y2 = canvas.coords(paddle)
    paddle_hit = canvas.find_overlapping(x1,y1,x2,y2)

    if len(paddle_hit)==2: #made contact
        paddle_center_x = (x1+x2)/2
        bx1,bx2 = canvas.coords(ball)[0], canvas.coords(ball)[2]
        ball_center_x = (bx1+bx2)/2

        dH = ball_center_x-paddle_center_x
        angle = math.radians(-65/(PADDLE_WIDTH/2)*abs(dH) + 85)
        dy = -SPEED * math.sin(angle)
        if dH<0: #ball to the left of paddle
            dx = -SPEED * math.cos(angle)

        elif dH>0: #ball to the right of paddle
            dx = SPEED * math.cos(angle)

    return dx,dy



def draw_paddle(canvas,paddle):
    """
    This function draws the paddle based on mouse location
    argument:
        canvas
        paddle = current paddle object
    return:
        updated paddle object
    """
    canvas.delete(paddle)
    mouse_x=canvas.winfo_pointerx()
    paddle=canvas.create_rectangle(mouse_x-PADDLE_WIDTH/2,CANVAS_HEIGHT-PADDLE_HEIGHT,mouse_x+PADDLE_WIDTH/2,
                            CANVAS_HEIGHT,fill='red',outline='white')
    canvas.update()
    return paddle




def Edge_Collision_Check(dx,canvas,ball):
    """
    This function determines what occurs when ball hits edge of screen.
    Ball will bounce back for left and right collision. Whereas the game ends if
    ball goes off screen above (winner), or below (loser)
    Arg:
        dx = current x-change
        canvas,ball = objects to be modified (passed by reference)
    Return:
        dx = changes sign if hit a wall
        end_flag = flag indicating state of game. 1 = win, -1 = lose, 0 = ongoing
    """
    if hit_left(canvas,ball) or hit_right(canvas,ball):
        dx=dx*-1

    end_flag = 0
    if hit_bot(canvas,ball):
        end_flag = -1
        canvas.create_text(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, text="You Lose", font="Courier 36", fill='white')
    elif hit_top(canvas,ball):
        end_flag = 1
        canvas.create_text(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, text="You Win!", font="Courier 36", fill='white')

    return dx,end_flag



"""
The following functions are used to determine if ball hit the edge of screen
argument:
    canvas,ball
return:
    boolean for if condition is met
"""
def hit_right(canvas,ball):
    x=canvas.coords(ball)[0]+BALL_DIAMETER
    if x >CANVAS_WIDTH+BALL_DIAMETER:
        return True
    else:
        return False

def hit_left(canvas,ball):
    x = canvas.coords(ball)[0]
    if x < 0-BALL_DIAMETER:
        return True
    else:
        return False

def hit_bot(canvas,ball):
    y = canvas.coords(ball)[1] + BALL_DIAMETER
    if y > CANVAS_HEIGHT+BALL_DIAMETER:
        return True
    else:
        return False

def hit_top(canvas,ball):
    y = canvas.coords(ball)[1]
    if y < 0-BALL_DIAMETER:
        return True
    else:
        return False















def make_canvas(width, height, title=None):
    """
    DO NOT MODIFY
    Creates and returns a drawing canvas
    of the given int size with a blue border,
    ready for drawing.
    """
    objects = {}
    top = tkinter.Tk()
    top.minsize(width=width, height=height)
    if title:
        top.title(title)
    canvas = tkinter.Canvas(top, width=width + 1, height=height + 1)
    canvas.pack()
    canvas.xview_scroll(8, 'units')  # add this so (0, 0) works correctly
    canvas.yview_scroll(8, 'units')  # otherwise it's clipped off

    return canvas




if __name__ == "__main__":
    main()