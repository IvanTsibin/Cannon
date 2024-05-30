import numpy as np
import pygame as pg
import math
from random import randint

pg.init()
pg.font.init()

WHITE = (255, 255, 255)
BLACK = (105, 105, 185)
RED = (225, 0, 0)

START_SCREEN_SIZE = (1000, 900)
SCREEN_SIZE = (1000, 900)

def rand_color():
    return (randint(0, 230), randint(0, 230), randint(0, 230))


class GameObject:
    pass

class Barrier:
    """
    Barrier class. Creates barrie, manages it's rendering and collision with a targets event.
    """
    def __init__(self, coordABCD=None, color =None, center = None):
        if coordABCD == None:
            coordABCD = [(0 ,0),(100, 0),(100, 100),(0, 100)]
        self.coordABCD = coordABCD
        if center == None:
            center = [50, 50]
        self.center = center
        if color == None:
            color = rand_color()
        self.color = color
        self.barrier_massive = []

    def get_lines(self, Barrier):
        self.coordABCD = Barrier.coordABCD
        for i in range(len(self.coordABCD)):
            self.line = (self.coordABCD[i], self.coordABCD[0 if i + 1 == len(self.coordABCD)
            else i + 1])
            self.barrier_massive.append(self.line)
        return self.barrier_massive


    def draw(self, screen):
        """
        Draws the barrie on the screen
        """
        pg.draw.polygon(screen, self.color, self.coordABCD)
        self.steps = 25
        self.coordABCD2 = []
        for i in range(len(self.coordABCD)):
            self.coordABCD2.append([0,0])
        self.color2 = [255, 255, 255]
        self.color_delta = [255, 255, 255]
        for i in range(self.steps):
            for j in range(len(self.coordABCD)):
                for m in range(2):
                    self.coordABCD2[j][m] = self.coordABCD[j][m] + int((self.center[m] - self.coordABCD[j][m]) * (i + 1) / self.steps)

            for j in range(3):
                self.color_delta[j] = 255 - self.color[j]
                self.color2[j] = int(self.color[j] + self.color_delta[j] -\
                                 (self.color_delta[j] ** 2 - ((i + 1) * self.color_delta[j] / self.steps) ** 2) ** 0.5)
            pg.draw.polygon(screen, self.color2, self.coordABCD2)


class Target(GameObject):
    """
    Target class. Creates target, manages it's rendering and collision with a ball event.
    """
    def __init__(self, coord=None, vel=None, rad=None, color=None, refl_ort=1, refl_par=1):
        """
        Constructor method. Sets coordinate, color and radius of the target.
        """
        if coord == None:
            coord = [rad * randint(1, (SCREEN_SIZE[0] - rad) // rad), rad * randint(1, (150 - rad) // rad)]
        self.coord = coord
        # self.rad = rad
        self.rad = rad
        if rad == None:
            self.rad = randint(16, 60)
        self.vel = vel
        self.old_vel = [0, 0]
        self.target_vel_new = [0, 0]
        self.new_coord1 = [0, 0]
        self.new_coord2 = [0, 0]
        self.refl_ort = refl_ort
        self.refl_par = refl_par
        self.bump_trigger = False
        self.bump_trigger_counter = 0
        self.bump_barrier_trigger = False
        self.bump_barrier_trigger_counter = 5
        self.grav_counter = 0
        self.total_bump_counter = 0
        self.tick_counter = 0
        self.power = self.rad * (self.vel[0] **2 + self.vel[1] **2) **0.5 / 2

        if color == None:
            color = rand_color()
        self.color = color

        self.color_flip_counter = 30
        self.color_triger = True

    def color_flip(self):
        if self.color_flip_counter > 0 and self.color_triger:
            self.color = (0 + self.color_flip_counter * 8, 0, 0)
            self.color_flip_counter -= 1
        elif self.color_flip_counter ==0:
            self.color_flip_counter += 1
            self.color_triger = False
        elif self.color_flip_counter <= 30:
            self.color = (0 + self.color_flip_counter * 8, 0, 0)
            self.color_flip_counter += 1
        else:
            self.color_triger = True
        # return self.color


    def check_collision(self, ball):
        """
        Checks whether the ball bumps into target.
        """
        dist = sum([(self.coord[i] - ball.coord[i])**2 for i in range(2)])**0.5
        min_dist = self.rad + ball.rad + 2
        if dist <= min_dist:
            if self.rad < 20:
                return True
            else:
                self.rad -= 2
                return False
        return False

    def chek_collision_barrier(self, coordABCD):
        """
        :param coordABCD:
        :return: nothing
        :checks the collision of Target with line AB with coordABCD(A(), B()) and changes Target's velocity if
        collision has happened
        """
        self.coordABCD = coordABCD
        self.circleCenter = self.coord
        self.crossDot = (0, 0)

        def right_angle_dot(line1dot1, line1dot2, line2dot1):
            """
            Gets points A and B of line AB and coordinates of a circle C. Returns coordinates of point D (CrossDot)
             of line AB and line CD which is normal to line AB
             """
            normal_dot = [0, 0]
            line2dot2 = [0, 0]
            if line1dot1[0] == line1dot2[0]:
                line2dot2[1] = line2dot1[1]
                line2dot2[0] = line1dot1[0]
            else:
                line2dot2[1] = 0
                line2dot2[0] = line2dot1[0] - line2dot1[1] * (line1dot2[1] - line1dot1[1]) / (line1dot1[0] - line1dot2[0])
            a1 = line1dot2[0] - line1dot1[0]
            b1 = line1dot2[1] - line1dot1[1]
            c1 = line1dot1[0] * (line1dot2[1] - line1dot1[1]) - line1dot1[1] * (line1dot2[0] - line1dot1[0])
            a2 = line2dot2[0] - line2dot1[0]
            b2 = line2dot2[1] - line2dot1[1]
            c2 = line2dot1[0] * (line2dot2[1] - line2dot1[1]) - line2dot1[1] * (line2dot2[0] - line2dot1[0])
            if b1 == 0:
                normal_dot[1] = line1dot2[1]
                normal_dot[0] = line2dot1[0]
            else:
                normal_dot[1] = (c1 * b2 / b1 - c2) / (a2 - a1 * b2 / b1)
                normal_dot[0] = (normal_dot[1] * a1 + c1) / b1
            ND = (int(normal_dot[0]), int(normal_dot[1]))
            return ND

        if self.bump_barrier_trigger and self.bump_barrier_trigger_counter == 0:
            self.bump_barrier_trigger = False
            self.bump_barrier_trigger_counter = 4
        elif self.bump_barrier_trigger and self.bump_barrier_trigger_counter > 0:
            self.bump_barrier_trigger_counter -= 1
        else:
            self.crossDot = right_angle_dot(self.coordABCD[0], self.coordABCD[1], self.circleCenter)
            self.dot_A = self.coordABCD[0]
            self.dot_B = self.coordABCD[1]
            self.dot_C = self.circleCenter
            self.dot_D = self.crossDot
            self.lenth_AB = ((self.dot_A[0] - self.dot_B[0])**2+(self.dot_A[1] - self.dot_B[1])**2) ** 0.5
            self.lenth_AD = ((self.dot_A[0] - self.dot_D[0])**2+(self.dot_A[1] - self.dot_D[1])**2) ** 0.5
            self.lenth_BD = ((self.dot_D[0] - self.dot_B[0])**2+(self.dot_D[1] - self.dot_B[1])**2) ** 0.5
            self.lenth_CD = ((self.dot_D[0] - self.dot_C[0])**2+(self.dot_D[1] - self.dot_C[1])**2) ** 0.5
            self.lenth_CA = ((self.dot_C[0] - self.dot_A[0]) ** 2 + (self.dot_C[1] - self.dot_A[1]) ** 2) ** 0.5
            self.lenth_CB = ((self.dot_C[0] - self.dot_B[0]) ** 2 + (self.dot_C[1] - self.dot_B[1]) ** 2) ** 0.5
            if self.lenth_CD > self.rad:
                self.bump_barrier_trigger_counter = 4
            elif self.lenth_AD < self.lenth_AB and self.lenth_BD < self.lenth_AB:
                # print(" Barrier Collision Happened between", self.dot_A, "and", self.dot_B)
                self.bump_barrier_target_vel_change(self.dot_D)
            elif self.lenth_CA < self.rad:
                # print(" Barrier Collision Happened with A side", self.dot_A)
                self.bump_barrier_target_vel_change(self.dot_A)
            elif self.lenth_CB < self.rad:
                # print(" Barrier Collision Happened with B side", self.dot_B)
                self.bump_barrier_target_vel_change(self.dot_B)

    def bump_barrier_target_vel_change(self, bump_dot):
        self.dist = (sum([(self.coord[i] - bump_dot[i]) ** 2 for i in range(2)])) ** 0.5

        if self.bump_barrier_trigger and  self.bump_barrier_trigger_counter > 0:
            self.bump_barrier_trigger_counter -= 1
            # print("No Vel_Change Ball with rad = ", self.rad, "bump_barrier_trigger_counter = ",
            #       self.bump_barrier_trigger_counter,"bump_barrier_trigger = ", self.bump_barrier_trigger)
            pass
        elif self.bump_barrier_trigger and self.dist >= self.rad and self.bump_barrier_trigger_counter == 0:
            self.bump_barrier_trigger = False
            # print("No Vel_Change Ball with rad = ", self.rad, "bump_barrier_trigger_counter = ",
            #       self.bump_barrier_trigger_counter,"bump_barrier_trigger = ", self.bump_barrier_trigger)
        elif self.bump_barrier_trigger == False and self.dist < self.rad and self.bump_barrier_trigger_counter > 0:

            self.vel_vec = (sum([self.vel[i] ** 2 for i in range(2)])) ** 0.5
            if self.dist > 0:
                self.coord[0] -= self.vel[0] * abs(self.vel_vec / self.dist)
                self.coord[1] -= self.vel[1] * abs(self.vel_vec / self.dist)
            self.dist = (sum([(self.coord[i] - bump_dot[i]) ** 2 for i in range(2)])) ** 0.5

            # print("Circle center:%.1f" %self.coord[0],"%.1f" %self.coord[1],"Collision dot", bump_dot)
            self.vel_vec = (sum([self.vel[i] ** 2 for i in range(2)])) ** 0.5
            # print("Starting Target velocity: X %.2f" % self.vel[0], "Y %.2f" % self.vel[1], "Full Velocity = %.2f" % self.vel_vec )
            self.B_dot = [0, 0]
            self.V_dot = [0, 0]
            self.V_dot[0], self.V_dot[1] = self.vel[0], self.vel[1]
            self.B_dot[0], self.B_dot[1] = bump_dot[0] - self.coord[0], bump_dot[1] - self.coord[1]
            self.dist2 = (sum([(self.B_dot[i]) ** 2 for i in range(2)])) ** 0.5
            # print("self.B_dot X %.1f" % self.B_dot[0], "self.B_dot Y %.1f" % self.B_dot[1], "self.dist2 %.1f" % self.dist2)
            self.turn1 = 1
            if self.B_dot[0] > 0 and self.B_dot[1] <= 0:
                self.turn1 = 2
                self.B_dot[1] = - self.B_dot[1]
                self.V_dot[1] = - self.V_dot[1]
            elif self.B_dot[0] <= 0 and self.B_dot[1] <= 0:
                self.turn1 = 3
                self.B_dot[0] = - self.B_dot[0]
                self.B_dot[1] = - self.B_dot[1]
                self.V_dot[0] = - self.V_dot[0]
                self.V_dot[1] = - self.V_dot[1]
            elif self.B_dot[0] <= 0 and self.B_dot[1] > 0:
                self.turn1 = 4
                self.B_dot[0] = - self.B_dot[0]
                self.V_dot[0] = - self.V_dot[0]
            self.betta = math.acos(self.B_dot[0] / self.dist2)
            self.betta2 = math.degrees(self.betta)
            if self.vel_vec == 0:
                self.alfa_0 = 0
            else:
                self.alfa_0 = math.degrees(math.acos(self.V_dot[0] / self.vel_vec))
            # print("self.B_dot X %.1f" % self.B_dot[0], "self.B_dot Y %.1f" % self.B_dot[1], "self.betta  %.1f" % self.betta2)
            # print("Starting 2 Target velocity: X %.1f" % self.V_dot[0], "Y %.1f" % self.V_dot[1], "self.alfa_0 %.1f" % self.alfa_0)
            if self.V_dot[0] >= 0 and self.V_dot[1] <= 0:
                if self.vel_vec == 0:
                    self.alfa = 0
                else:
                    self.alfa = math.asin(self.V_dot[1] / self.vel_vec)
                self.alfa = self.alfa + math.radians(90) - self.betta
                self.turn2 = 2
            elif self.V_dot[0] <= 0 and self.V_dot[1] > 0:
                if self.vel_vec == 0:
                    self.alfa = 0
                else:
                    self.alfa = + math.pi / 2 + math.acos(self.V_dot[1] / self.vel_vec) + math.pi / 2 - self.betta
                self.turn2 = 3
            else:
                self.alfa = math.acos(self.V_dot[0] / self.vel_vec) + math.pi / 2 - self.betta
                self.turn2 = 1

            # print("real alfa = %.2f" % math.degrees(self.alfa))
            self.alfa *= - 1
            # print(" - real alfa = %.2f" % math.degrees(self.alfa))
            self.alfa = self.alfa + self.betta - math.pi / 2
            # print(" Recalculated alfa = %.2f" % math.degrees(self.alfa))
            self.V_dot[0] = self.vel_vec * math.cos(self.alfa)
            self.V_dot[1] = self.vel_vec * math.sin(self.alfa)
            self.vel_vec = (sum([self.vel[i] ** 2 for i in range(2)])) ** 0.5
            # print("Recalculated Target velocity: X %.2f" % self.vel[0], "Y %.2f" % self.vel[1], "Full Velocity = %.2f" % self.vel_vec )
            if self.turn1 == 2:
                self.V_dot[1] = - self.V_dot[1]
            elif self.turn1 == 3:
                self.V_dot[0] = - self.V_dot[0]
                self.V_dot[1] = - self.V_dot[1]
            elif self.turn1 == 4:
                self.V_dot[0] = - self.V_dot[0]

            self.coord[0] -= self.vel[0]
            self.coord[1] -= self.vel[1]

            self.vel[0], self.vel[1] = self.V_dot[0], self.V_dot[1]

            self.vel_vec = (sum([self.vel[i] ** 2 for i in range(2)])) ** 0.5
            # print("Changed Target velocity: X %.2f" % self.vel[0], "Y %.2f" % self.vel[1], "Full Velocity = %.2f" % self.vel_vec)
            self.bump_barrier_trigger = True
            if self.vel_vec == 0:
                self.bump_barrier_trigger_counter = 10
            else:
                self.bump_barrier_trigger_counter = int((abs(self.rad - self.dist))/self.vel_vec) + 4
            # print("Радиус шара", self.rad, "bump_barrier_trigger_counter = ", self.bump_barrier_trigger_counter,
            #       "bump_barrier_trigger = ", self.bump_barrier_trigger,"Radius = ", self.rad, "self.dist %.1f" % self.dist)


            self.dist = (sum([(self.coord[i] - bump_dot[i]) ** 2 for i in range(2)])) ** 0.5
            self.coord[0] += self.vel[0] * abs(self.vel_vec / self.dist)
            self.coord[1] += self.vel[1] * abs(self.vel_vec / self.dist)

    def check_collision_target(self, target):
        """
        Checks whether the target bumps into target.
        """
        # self.tick_counter+= 1
        # print("Tick counter = ", self.tick_counter)
        self.dist = sum([(self.coord[i] - target.coord[i])**2 for i in range(2)])**0.5
        # print("Radius = ", self.rad, "Distance = %.1f" %self.dist)
        if self.dist == 0:
            self.dist = 1
        self.min_dist = self.rad + target.rad + 2
        self.new_coord1[0] = self.coord[0] + self.vel[0]
        self.new_coord1[1] = self.coord[1] + self.vel[1]
        self.new_coord2[0] = target.coord[0] + target.vel[0]
        self.new_coord2[1] = target.coord[1] + target.vel[1]
        dist_delta = self.min_dist - self.dist
        self.dist2 = sum([(self.new_coord1[i] - self.new_coord2[i])**2 for i in range(2)])**0.5

        if self.bump_trigger and self.dist <= self.min_dist and self.bump_trigger_counter > 0:
        # if  self.dist2 <= self.min_dist and self.bump_trigger_counter > 0:
            self.bump_trigger_counter -= 1
            return False
        else:
            self.bump_trigger_counter = 0

        if (self.dist - 3) < self.min_dist and self.vel[0] == target.vel[0] and self.vel[1] == target.vel[1]:
            if self.coord[0] < target.coord[0]:
                self.vel[0] += 2
            else:
                self.vel[0] -= 2
            if self.coord[1] < target.coord[1]:
                self.vel[1] += 2
            else:
                self.vel[1] -= 2

        if self.bump_trigger and self.dist2 > self.min_dist:
            self.bump_trigger = False

        if self.dist <= self.min_dist and self.dist2 < self.dist:
            self.bump_trigger = True
            # print('Target bumps, coords and velocity will be changed.')
            return True
        else:
            return False


    def bump_target_vel_change(self, target):
        self.bump_dot = [0, 0]
        self.bump_dot[0], self.bump_dot[1] = target.coord[0], target.coord[1]
        self.dist = (sum([(self.coord[i] - target.coord[i]) ** 2 for i in range(2)])) ** 0.5
        # print("Target with color = ", self.color, "bump_trigger_counter = ",
        #       self.bump_trigger_counter, "bump_trigger = ", self.bump_trigger, "    dist = %.1f" %self.dist)
        self.vel_vec = (sum([self.vel[i] ** 2 for i in range(2)])) ** 0.5
        if self.dist == 0:
            self.coord[0] -= self.vel[0]
            self.coord[1] -= self.vel[1]
        else:
            self.coord[0] -= self.vel[0] * 0.99 * abs(self.vel_vec / self.dist)
            self.coord[1] -= self.vel[1] * 0.99 * abs(self.vel_vec / self.dist)

        if self.bump_trigger and self.bump_trigger_counter > 0:

            self.bump_trigger_counter -= 1
            # print("No Vel_Change Target with color = ", self.color, "bump_trigger_counter = ",
            #       self.bump_trigger_counter,"bump_trigger = ", self.bump_trigger)
            pass
        elif self.bump_trigger and self.dist > (self.rad + target.rad + 2) and self.bump_trigger_counter == 0:
            self.bump_trigger = False
            # print("Still is being bumped Target with color ", self.color, "bump_trigger_counter = ",
            #       self.bump_trigger_counter, "bump_trigger = ", self.bump_trigger, "  dist = %.1f" %self.dist)
        elif self.bump_trigger and self.dist <= (self.rad + target.rad + 2) and self.bump_trigger_counter == 0:
            self.old_vel = list(self.vel)
            # print("Target's center X %.1f" %self.coord[0]," Y %.1f" %self.coord[1],"Bumped ball's center",
            #       "X %.1f" %self.bump_dot[0], "   Y %.1f" %self.bump_dot[1])
            self.vel_vec = (sum([self.vel[i] ** 2 for i in range(2)])) ** 0.5
            # print("Starting Target with color ",self.color ," velocity: X %.2f" % self.vel[0],
            #       "Y %.2f" % self.vel[1], "Full Velocity = %.2f" % self.vel_vec)
            self.B_dot = [0, 0]
            self.V_dot = [0, 0]
            self.VT_dot = [0, 0]
            self.V_dot[0], self.V_dot[1] = self.vel[0], self.vel[1]
            self.VT_dot[0], self.VT_dot[1] = target.old_vel[0], target.old_vel[1]
            self.B_dot[0], self.B_dot[1] = self.bump_dot[0] - self.coord[0], self.bump_dot[1] - self.coord[1]
            # print("Bumped ball   with color ", target.color, " velocity: X %.2f" % target.old_vel[0],
            #       " Y %.2f" % target.old_vel[1], "before recalculating")
            self.dist2 = (sum([(self.B_dot[i]) ** 2 for i in range(2)])) ** 0.5
            # print("self.B_dot X %.1f" % self.B_dot[0], "self.B_dot Y %.1f" % self.B_dot[1], "self.dist2 %.1f" % self.dist2)

            if self.B_dot[0] >= 0 and self.B_dot[1] <= 0:
                self.turn1 = 2
                self.B_dot[1] = - self.B_dot[1]
                self.V_dot[1] = - self.V_dot[1]
                self.VT_dot[1] = - self.VT_dot[1]
                # print("turn1 = 2")
            elif self.B_dot[0] < 0 and self.B_dot[1] < 0:
                self.turn1 = 3
                self.B_dot[0] = - self.B_dot[0]
                self.B_dot[1] = - self.B_dot[1]
                self.V_dot[0] = - self.V_dot[0]
                self.V_dot[1] = - self.V_dot[1]
                self.VT_dot[0] = - self.VT_dot[0]
                self.VT_dot[1] = - self.VT_dot[1]
                # print("turn1 = 3")
            elif self.B_dot[0] <= 0 and self.B_dot[1] >= 0:
                self.turn1 = 4
                self.B_dot[0] = - self.B_dot[0]
                self.V_dot[0] = - self.V_dot[0]
                self.VT_dot[0] = - self.VT_dot[0]
                # print("turn1 = 4")
            else:
                self.turn1 = 1
                # print("turn1 = 1")
            self.betta = math.acos(self.B_dot[0] / self.dist2)
            self.betta2 = math.degrees(self.betta)
            self.alfa = 0
            if self.vel_vec == 0:
                self.alfa_0 = 0
            else:
                if self.V_dot[1]>=0:
                    self.alfa = math.acos(self.V_dot[0] / self.vel_vec)
                else:
                    self.alfa = - math.acos(self.V_dot[0] / self.vel_vec)

            self.vel_vec_target = (sum([self.VT_dot[i] ** 2 for i in range(2)])) ** 0.5

            if self.vel_vec_target == 0:
                self.gamma = 0
            else:
                if self.VT_dot[1]>=0:
                    self.gamma = math.acos(- self.VT_dot[0] / self.vel_vec_target)
                else:
                    self.gamma = - math.acos(- self.VT_dot[0] / self.vel_vec_target)


            if self.vel_vec_target == 0:
                self.vel_vec_target = 0.001
            # print("Starting 2 Bumped ball velocity: %.2f" % self.vel_vec, " X vel = %.2f" % self.VT_dot[0]," Y vel = %.2f" % self.VT_dot[1],"self.gamma %.1f" % math.degrees(self.gamma))
            # print("self.B_dot X %.1f" % self.B_dot[0], "self.B_dot Y %.1f" % self.B_dot[1], "self.betta  %.1f" % self.betta2)
            # print("Starting 2      Target velocity: %.2f" % self.vel_vec_target," X vel = %.2f" % self.V_dot[0], "Y vel = %.2f" % self.V_dot[1], "self.alfa %.1f" % math.degrees(self.alfa))

            self.alfa = self.alfa - self.betta
            self.gamma = self.gamma + self.betta

            # print("Starting 3 Target velocity before angle change: X %.2f" % self.V_dot[0], "Y %.2f" % self.V_dot[1], "alfa = %.1f" % math.degrees(self.alfa))
            # print("Starting 3 Ball   velocity before angle change: X %.2f" % self.VT_dot[0], "Y %.2f" % self.VT_dot[1], "gamma = %.1f" % math.degrees(self.gamma))

            self.V_dot[0] = self.vel_vec * math.cos(self.alfa) # this is Target's normal velocity - will be changed
            self.V_dot[1] = self.vel_vec * math.sin(self.alfa) # this is Target's tangens - will not be changed before Starting 5

            # print("Starting 4 Target velocity: X %.2f" % self.V_dot[0], "Y %.2f" % self.V_dot[1], "alfa = %.1f" % math.degrees(self.alfa))
            self.VT_dot[1] = self.vel_vec_target * math.sin(self.gamma) # this is Ball's tangens - will no be used
            self.VT_dot[0] = - self.vel_vec_target * math.cos(self.gamma) # this is Ball's normal velocity - wiil be used to change Target's velocity
            # print("Starting 4 Ball   velocity: X %.2f" % self.VT_dot[0], "Y %.2f" % self.VT_dot[1], "gamma = %.1f" % math.degrees(self.gamma))
            self.normal_velocity_shift = self.VT_dot[0] - self.V_dot[0]
            self.V_dot[0] = self.normal_velocity_shift * 0.8 * target.rad / self.rad + self.V_dot[0]
            self.vel_vec_new = (self.V_dot[0] ** 2 + self.V_dot[1] ** 2) ** 0.5

            if self.V_dot[1] >= 0:
                self.alfa = math.acos(self.V_dot[0] / self.vel_vec_new)
            else:
                self.alfa = - math.acos(self.V_dot[0] / self.vel_vec_new)

            # print("Starting 5 Target velocity after angle change: X %.2f" % self.V_dot[0], "Y %.2f" % self.V_dot[1], "alfa = %.1f" % math.degrees(self.alfa))
            self.alfa = self.alfa + self.betta
            # print(" Recalculated alfa = %.2f" % math.degrees(self.alfa))
            self.V_dot[0] = self.vel_vec_new * math.cos(self.alfa)
            self.V_dot[1] = self.vel_vec_new * math.sin(self.alfa)
            self.vel_vec = (sum([self.V_dot[i] ** 2 for i in range(2)])) ** 0.5
            # print("Recalculated Target velocity before final turn1: X %.2f" % self.V_dot[0], "Y %.2f" % self.V_dot[1], "Full Velocity = %.2f" % self.vel_vec)
            if self.turn1 == 2:
                self.V_dot[1] = - self.V_dot[1]
            elif self.turn1 == 3:
                self.V_dot[0] = - self.V_dot[0]
                self.V_dot[1] = - self.V_dot[1]
            elif self.turn1 == 4:
                self.V_dot[0] = - self.V_dot[0]

            self.vel[0], self.vel[1] = self.V_dot[0], self.V_dot[1]
            self.vel_vec = (sum([self.vel[i] ** 2 for i in range(2)])) ** 0.5
            # print("Target with color ", self.color, "Changed Target velocity: X %.2f" % self.vel[0],
            #       "Y %.2f" % self.vel[1], "Full Velocity = %.2f" % self.vel_vec)
            self.bump_trigger = True
            if self.vel_vec == 0:
                self.bump_trigger_counter = 1
            else:
                self.bump_trigger_counter = int((abs(self.rad + target.rad - self.dist))/self.vel_vec) + 2
            self.dist = (sum([(self.coord[i] - target.coord[i]) ** 2 for i in range(2)])) ** 0.5
            self.energy = self.vel_vec * self.rad + self.vel_vec_target * target.rad
            # print("Turn finished Target with color", self.color, "bump_trigger_counter = ", self.bump_trigger_counter,
            #       "bump_trigger = ", self.bump_trigger, "self.dist %.1f" % self.dist, "Energy of system = R1 * V1 + R2 * V2  = %.1f" % self.energy)
            self.total_bump_counter += 1
            # print("Terget with color", self.color, " Target old velocity: X %.2f" % self.old_vel[0],
            #       "Y %.2f" % self.old_vel[1], " Total_bump_counter = ", self.total_bump_counter)


    def draw_shadow(self, screen):
        """
        Draws the target's shadow on the screen
        """

        if self.__class__.__name__ == "Shell":
            self.color_flip()

        self.rad_shift = 0.4
        self.steps = int(self.rad / 2)
        self.color_delta2 = [2, 2, 2]
        self.color3 = [2, 2, 2]
        self.color4 = BLACK
        self.coord2 = [0, 0]
        for i in range(self.steps):
            for j in range(3):
                if self.color4[j] > 25:
                    self.shadow_shift = self.color4[j] - 15
                else:
                    self.shadow_shift = 10
                self.color3[j] = int(self.shadow_shift * (self.steps**2 - (i + 1) ** 2)**0.5/self.steps)
            self.coord2[0] = int(self.coord[0] + self.rad * self.rad_shift * (1 - (i + 1) * 1.4 / self.steps))
            self.coord2[1] = int(self.coord[1] + self.rad * self.rad_shift * (1 - (i + 1) * 1.4 / self.steps))
            self.rad2 = 0.9 * (self.rad ** 2 - ((i + 1) * self.rad / self.steps) ** 2) ** 0.5
            pg.draw.circle(screen, self.color3, self.coord2, int(self.rad2))



    def draw(self, screen):
        """
        Draws the target on the screen
        """
        if self.__class__.__name__ == "Shell":
            self.color_flip()

        pg.draw.circle(screen, self.color, self.coord, self.rad)

        self.rad_shift = 0.4
        self.steps = int(self.rad / 1)
        self.color_delta = [253, 253, 253]
        self.color2 = [253, 253, 253]
        self.coord2 = [0, 0]
        for i in range(self.steps):
            for j in range(3):
                self.color_delta[j] = 255 - self.color[j]
                self.color2[j] = int(self.color[j] + self.color_delta[j] -\
                                 (self.color_delta[j] ** 2 - ((i + 1) * self.color_delta[j] / self.steps) ** 2) ** 0.5)
            self.coord2[0] = int(self.coord[0] - self.rad * self.rad_shift * (i + 1) * 0.8 / self.steps)
            self.coord2[1] = int(self.coord[1] - self.rad * self.rad_shift * (i + 1) * 0.8 / self.steps)
            self.rad2 = 0.9 * (self.rad ** 2 - ((i + 1) * self.rad / self.steps) ** 2) ** 0.5
            pg.draw.circle(screen, self.color2, self.coord2, int(self.rad2))


    def move(self, time = 1, grav = 0):
        """
        Moves the target according to it's velocity and time step.
        Changes the ball's velocity due to gravitational force.
        """

        # print("Target with Rad = ", self.rad, "has bump barrier trigger counter =", self.bump_barrier_trigger_counter)
        if self.bump_barrier_trigger_counter != 0:
            self.vel[1] += grav


        for i in range(2):
            self.coord[i] += time * self.vel[i]
        self.check_corners(self.refl_ort, self.refl_par)
        if self.vel[0]**2 + self.vel[1]**2 < 1 and self.coord[1] > SCREEN_SIZE[1] - 2*self.rad:
            self.is_alive = False

    def power_counter(self):
        self.power = self.rad * (self.vel[0] ** 2 + self.vel[1] ** 2) ** 0.5 / 2
        return self.power

    def check_corners(self, refl_ort = 1, refl_par = 1):
        """
        Reflects targetl's velocity when target bumps into the screen corners. Implemetns inelastic rebounce.
        """
        self.refl_ort = refl_ort
        self.refl_par = refl_par
        for i in range(2):
            if self.coord[i] < self.rad:
                self.coord[i] = self.rad
                self.vel[i] = -self.vel[i] * self.refl_ort
                self.vel[1-i] = self.vel[1-i] * self.refl_par
            elif self.coord[i] > SCREEN_SIZE[i] - self.rad:
                self.coord[i] = SCREEN_SIZE[i] - self.rad
                self.vel[i] = -self.vel[i] * self.refl_ort
                self.vel[1-i] = self.vel[1-i] * self.refl_par


class MovingTarget(Target):
    def __init__(self, coord=None, vel=[0.00, 0.00], rad=30, color=None, refl_ort=1, refl_par=1):
        super().__init__(coord, vel, rad, color, refl_ort, refl_par)
        self.refl_ort = refl_ort
        self.refl_par = refl_par
        vel = [randint(-60, +60)/10, randint(-60, +60)/10]
        self.vel = vel
        self.rad = rad



class StableTarget(Target):
    def __init__(self, coord=None, vel = [0, 0], rad=30, color=None, refl_ort=1, refl_par=1):
        super().__init__(coord, vel, rad, color, refl_ort, refl_par)
        self.refl_ort = refl_ort
        self.refl_par = refl_par
        vel = [0, 0]
        self.vel = vel



class Shell(Target):
    """
    The ball class. Creates a ball, controls it's movement and implement it's rendering.
    """
    def __init__(self, coord, vel, rad=24, color=None):
        super().__init__(coord, vel, rad, color)
        """
        Constructor method. Initializes ball's parameters and initial values.
        """
        self.coord = coord
        self.vel = vel
        if color == None:
            color = rand_color()
            # color = (10, 140, 60)
        self.color = color
        self.rad = rad
        self.is_alive = True
        self.old_vel = [0, 0]
        self.target_vel_new = [0, 0]
        self.new_coord1 = [0, 0]
        self.new_coord2 = [0, 0]
        self.bump_trigger = False
        refl_ort = 0.99
        refl_par = 0.99
        self.refl_ort = refl_ort
        self.refl_par = refl_par
        self.grav = 0.5



class Cannon(GameObject):
    """
    Cannon class. Manages it's renderring, movement and striking.
    """
    def __init__(self, coord=[30, SCREEN_SIZE[1]//2], angle=0, max_pow=40, min_pow=2, color=RED):
        """
        Constructor method. Sets coordinate, direction, minimum and maximum power and color of the gun.
        """
        self.coord = coord
        self.angle = angle
        self.max_pow = max_pow
        self.min_pow = min_pow
        self.color = color
        self.active = False
        self.pow = min_pow

    def activate(self):
        """
        Activates gun's charge.
        """
        self.active = True

    def gain(self, inc=10):
        """
        Increases current gun charge power according to mouse position multiplied by increment

        """

        self.mouse_pos = [0, 0]
        if pg.mouse.get_focused():
            self.mouse_pos = pg.mouse.get_pos()
        self.dist = ((self.mouse_pos[1] - self.coord[1])**2 + (self.mouse_pos[0] - self.coord[0])**2)**0.5

        if self.dist == 0:
            self.pow = self.min_pow
        elif self.dist / inc < self.max_pow:
            self.pow = self.dist / inc
        else:
            self.pow = self.max_pow

    def strike(self):
        """
        Creates ball, according to gun's direction and current charge power.
        """
        vel = self.pow
        angle = self.angle
        ball = Shell(list(self.coord), [int(vel * np.cos(angle)), int(vel * np.sin(angle))])
        self.pow = self.min_pow
        self.active = False
        return ball

    def set_angle(self, target_pos):
        """
        Sets gun's direction to target position.
        """
        self.angle = np.arctan2(target_pos[1] - self.coord[1], target_pos[0] - self.coord[0])
        # print("Cannon's angle %2.f" %math.degrees(self.angle))

    def move(self, inc):
        """
        Changes vertical position of the gun.
        """
        if (self.coord[1] > 30 or inc > 0) and (self.coord[1] < SCREEN_SIZE[1] - 30 or inc < 0):
            self.coord[1] += inc

    def draw(self, screen):
        """
        Draws the gun on the screen.
        """
        self.buttons = pg.mouse.get_pressed(3)

        if sum([(self.coord[i] - self.mouse_pos[i]) ** 2 for i in range(2)]) ** 0.5 < 30 and self.buttons[0]:
            self.gun_trigger = True
        elif self.buttons[0] == False:
            self.gun_trigger = False

        if self.buttons[0] and self.gun_trigger:
            gun_shape = []
            vec_1 = np.array([int(10*np.cos(self.angle - np.pi/2)), int(10*np.sin(self.angle - np.pi/2))])
            vec_2 = np.array([int(self.pow*5*np.cos(self.angle)), int(self.pow*5*np.sin(self.angle))])
            gun_pos = np.array(self.coord)
            gun_shape.append((gun_pos + vec_1 * 3).tolist())
            gun_shape.append((gun_pos + vec_1 + vec_2).tolist())
            gun_shape.append((gun_pos + vec_2 - vec_1).tolist())
            gun_shape.append((gun_pos - vec_1 * 3).tolist())
            self.color = (int(53 + self.pow * 2), 0, 0)
            self.draw_polygon(screen, self.color, gun_shape)
            self.draw_circle(screen, self.color, self.coord, radius=30)

            if self.gun_trigger and self.buttons[0] == False:
                self.gun_trigger = False
        else:
            gun_shape = []
            vec_1 = np.array([int(10*np.cos(self.angle - np.pi/2)), int(10*np.sin(self.angle - np.pi/2))])
            vec_2 = np.array([int(10*np.cos(self.angle)), int(10*np.sin(self.angle))])
            gun_pos = np.array(self.coord)
            gun_shape.append((gun_pos + vec_1 * 3).tolist())
            gun_shape.append((gun_pos + vec_1 + vec_2).tolist())
            gun_shape.append((gun_pos + vec_2 - vec_1).tolist())
            gun_shape.append((gun_pos - vec_1 * 3).tolist())
            self.color = (int(53 + self.pow * 2), 0, 0)
            self.draw_polygon(screen, self.color, gun_shape)
            self.draw_circle(screen, self.color, self.coord, radius=30)


    def draw_circle(self, screen, color, coord, radius):
        """
        Draws the target on the screen
        """
        self.color = color
        self.coord = coord
        self.rad = radius
        pg.draw.circle(screen, self.color, self.coord, self.rad)

        self.rad_shift = 0.4
        self.steps = int(self.rad / 1)
        self.color_delta = [253, 253, 253]
        self.color2 = [253, 253, 253]
        self.coord2 = [0, 0]
        for i in range(self.steps):
            for j in range(3):
                self.color_delta[j] = 255 - self.color[j]
                # print("Cannon shadow:", (self.color_delta[j] ** 2 - ((i + 1) * self.color_delta[j] / self.steps) ** 2)**0.5)
                self.color2[j] = int(self.color[j] + self.color_delta[j] - (self.color_delta[j] ** 2 - ((i + 1) * self.color_delta[j] / self.steps) ** 2) ** 0.5)
            self.coord2[0] = int(self.coord[0] - self.rad * self.rad_shift * (i + 1) * 0.8 / self.steps)
            self.coord2[1] = int(self.coord[1] - self.rad * self.rad_shift * (i + 1) * 0.8 / self.steps)
            self.rad2 = 0.9 * (self.rad ** 2 - ((i + 1) * self.rad / self.steps) ** 2) ** 0.5
            pg.draw.circle(screen, self.color2, self.coord2, int(self.rad2))


    def draw_polygon(self, screen, color, coord):

        self.color = color
        self.barrel_coord = coord


        pg.draw.polygon(screen, self.color, self.barrel_coord)
        self.steps = 25
        self.coordABCD2 = [[0, 0], [100, 0], [100, 100], [0, 100]]
        self.color2 = [255, 255, 255]
        self.color_delta = [255, 255, 255]


        for i in range(self.steps):
            for m in range(2):
                self.coordABCD2[0][m] = self.barrel_coord[0][m] + int((self.barrel_coord[3][m] - self.barrel_coord[0][m]) * (i + 1) *0.5 / self.steps)
                self.coordABCD2[3][m] = self.barrel_coord[3][m] + int((self.barrel_coord[0][m] - self.barrel_coord[3][m]) * (i + 1) *0.5 / self.steps)
                self.coordABCD2[1][m] = self.barrel_coord[1][m] + int((self.barrel_coord[2][m] - self.barrel_coord[1][m]) * (i + 1) *0.5 / self.steps)
                self.coordABCD2[2][m] = self.barrel_coord[2][m] + int((self.barrel_coord[1][m] - self.barrel_coord[2][m]) * (i + 1) *0.5 / self.steps)
            for j in range(3):
                self.color_delta[j] = 255 - self.color[j]
                self.color2[j] = int(self.color[j] + self.color_delta[j] -\
                                 (self.color_delta[j] ** 2 - ((i + 1) * self.color_delta[j] / self.steps) ** 2) ** 0.5)
            pg.draw.polygon(screen, self.color2, self.coordABCD2)


        pass


class ScoreTable:
    """
    Score table class.
    """
    def __init__(self, t_destr=0, b_used=0, level_number=1, total_power=100):
        self.t_destr = t_destr
        self.b_used = b_used
        self.font = pg.font.SysFont("timesnewroman", 25)
        self.level_number = level_number
        self.total_power = total_power

    def score(self):
        """
        Score calculation method.
        """
        return self.t_destr - self.b_used

    def draw(self, screen):
        score_surf = []
        score_surf.append(self.font.render("Total Power: {}".format(int(self.total_power)), True, WHITE))
        score_surf.append(self.font.render("Level: {}".format(self.level_number), True, WHITE))
        score_surf.append(self.font.render("Destroyed: {}".format(self.t_destr), True, WHITE))
        score_surf.append(self.font.render("Balls used: {}".format(self.b_used), True, WHITE))
        score_surf.append(self.font.render("Total: {}".format(self.score()), True, RED))
        for i in range(5):
            screen.blit(score_surf[i], [10, 50 + 30*i])


class Button:
    def __init__(self, button_name="None", button_coord=None, button_radius=22, button_color=None):
        if button_color is None:
            button_color = [100, 100, 100]
        if button_coord is None:
            button_coord = [100, 100]
        self.levels = []
        self.button_color = button_color
        self.button_radius = button_radius
        self.button_coord = button_coord
        self.font = pg.font.SysFont("timesnewroman", 15)
        self.button_font_coord = [button_coord[0] - len(button_name)*4, button_coord[1] - 10]
        self.button_name = button_name
        self.button_marked = False
        self.button_pressed = False

    def draw_button(self):
        pg.draw.circle(screen, self.button_color, self.button_coord, self.button_radius)
        screen.blit(self.font.render(self.button_name, True, WHITE), self.button_font_coord)
        pass

    def draw_marked_button(self):
        self.marked_button_color = [int(self.button_color[j] * 1.2) for j in range(3)]
        pg.draw.circle(screen, self.marked_button_color, self.button_coord, self.button_radius)
        screen.blit(self.font.render(self.button_name, True, WHITE), self.button_font_coord)


    def draw_pressed_button(self):
        self.pressed_button_color = [int(self.button_color[j] * 0.5) for j in range(3)]
        pg.draw.circle(screen, self.pressed_button_color, self.button_coord, self.button_radius)
        screen.blit(self.font.render(self.button_name, True, WHITE), self.button_font_coord)


    def check_button_marked(self):
        self.mouse_pos = pg.mouse.get_pos()

        if sum([(self.button_coord[i] - self.mouse_pos[i]) ** 2 for i in range(2)]) ** 0.5 < self.button_radius:
            self.button_marked = True
        else:
            self.button_marked = False
        return self.button_marked

    def check_button_pressed(self):
        self.mouse_pos = pg.mouse.get_pos()
        self.buttons = pg.mouse.get_pressed(3)
        # print(self.buttons,sum([(self.button_coord[i] - self.mouse_pos[i]) ** 2 for i in range(2)]) ** 0.5)

        if sum([(self.button_coord[i] - self.mouse_pos[i]) ** 2 for i in range(2)]) ** 0.5 < self.button_radius\
                and self.buttons[0]:
            self.button_pressed = True
            return True
        else:
            self.button_pressed = False
            return False



class Menu:
    """
    Class that menages level choosing and quit game ability
    """
    def __init__(self):
        self.levels_buttons = []
        self.menu_sight_color = [100, 100, 100]
        self.menu_sight_radius = 22
        self.menu_sight_coord = [22, 22]
        self.font = pg.font.SysFont("timesnewroman", 15)
        self.menu_sight_font_coord = [5, 12]
        self.levels_amount = 15
        self.level_menu_base_color = [90, 90, 90]
        self.level_menu_base_coord = [[10, 50], [750, 50], [750, 120], [10, 120]]


    def creat_on_top_menu_button(self):
        """
        Creates On TOP menu button
        """
        self.on_top_menu_button = Button("Menu", [22, 22], 22,[150, 150, 150])


    def draw_on_top_menu_button(self):
        """
        Draws the On TOP Menu button to came into menu

        """
        self.on_top_menu_button.draw_button()

    def check_on_top_menu_button_marked(self):
        if self.on_top_menu_button.check_button_marked():
            return True
        else:
            return False

    def check_on_top_menu_button_pressed(self):
        if self.on_top_menu_button.check_button_pressed():
            print("On Top Menu button pressed")
            return True
        else:
            return False


    def draw_on_top_menu_button_mareked(self):
        """
        Draws the On TOP Menu marked button to came into menu

        """
        self.on_top_menu_button.draw_marked_button()

    def draw_on_top_menu_button_pressed(self):
        """
        Draws the On TOP Menu pressed button to came into menu

        """
        self.on_top_menu_button.draw_pressed_button()

    def creat_levels_menu(self):
        self.level_menu_back_button = Button("Back", [45, 85], 22,[150, 150, 150])
        for level in range(self.levels_amount):
            self.levels_buttons.append(Button(str(level + 1),[90 + level*45, 85],22, [150, 150, 150]))
            # print(str(level + 1))


    def draw_levels_menu(self):
        pg.draw.polygon(screen, self.level_menu_base_color, self.level_menu_base_coord)

        if self.level_menu_back_button.check_button_marked():
            self.level_menu_back_button.draw_marked_button()
        elif self.level_menu_back_button.check_button_pressed():
            self.level_menu_back_button.draw_pressed_button()
        else:
            self.level_menu_back_button.draw_button()
        
        for level in range(self.levels_amount):
            self.level_button = self.levels_buttons[level]
            if self.level_button.check_button_marked():
                self.level_button.draw_marked_button()
            elif self.level_button.check_button_pressed():
                self.level_button.draw_pressed_button()
            else:
                self.level_button.draw_button()
        pass

    def check_pressed_button_in_levels_menu(self, events):
        """
        Checks the number of chosen level
        :return: number of chosen level or 0 if None was chosen
        """
        # print(self.levels_buttons)
        for event in events:
            if self.level_menu_back_button.check_button_pressed() and event.type == pg.MOUSEBUTTONDOWN:
                print("Menu Back Button has been pressed")
                return -1

            for level in range(self.levels_amount):
                self.level_button = self.levels_buttons[level]
                # print(self.level_button)
                if self.level_button.check_button_pressed() and event.type == pg.MOUSEBUTTONDOWN:
                    # print(self.level_button)
                    return level + 1
            else:
                return 0



class Manager:
    """
    Class that manages events' handling, ball's motion and collision, target creation, etc.
    """
    def __init__(self, n_targets=1):
        self.balls = []
        self.gun = Cannon()
        self.gun_trigger = False
        self.levels_menu_visibility = False
        self.system_power_counter = 0
        self.total_power = 0
        self.level = 9
        self.targets = []
        self.score_t = ScoreTable()
        self.menu = Menu()
        self.levels_menu = Menu()
        self.n_targets = n_targets
        self.barrier_massive = []
        self.barriers = []
        self.new_mission()


    def new_mission(self):
        """
        Creats a new mission according to
        """
        self.barriers.clear()
        self.targets.clear()
        self.barrier_massive.clear()
        self.balls.clear()

        self.score_t.level_number = self.level
        self.new_levels(self.level)
        self.menu.creat_on_top_menu_button()


    def new_levels(self, level=1):
        """
        Adds new targets and barrires according to level number.
        """

        self.level = level

        if self.level == 1:
            self.barriers1 = Barrier(coordABCD=[(130, 200), (260, 350), (320, 700), (120, 400)], color=(210, 15, 15),
                                     center=[180, 335])
            self.barriers2 = Barrier(coordABCD=[(870, 200), (740, 350), (680, 700), (880, 400)], color=(15, 210, 15),
                                     center=[820, 335])

            for i in range(self.n_targets):
                self.targets.append(StableTarget(rad=randint(20, 40)))

            for i in range(self.n_targets):
                self.targets.append(MovingTarget(rad=randint(20, 40)))

            self.barriers.append(self.barriers1)
            self.barriers.append(self.barriers2)
            for i, barrier in enumerate(self.barriers):
                self.barrier_massive.extend(barrier.get_lines(barrier))


        elif self.level == 2:
            self.targets.append(Target(coord=[175, 132], vel=[-0.65,1.89], rad=60, color=[50, 50, 50]))
            self.targets.append(Target(coord=[226, 272], vel=[0.65,-1.89], rad=40, color=[100, 100, 100]))

        elif self.level == 3:
            self.barriers1 = Barrier(coordABCD=[(130, 200), (260, 350), (320, 700), (120, 400)],
                                         color=(15, 15, 210),
                                         center=[200, 365])
            self.barriers2 = Barrier(coordABCD=[(870, 200), (740, 350), (680, 700), (880, 400)],
                                         color=(210, 15, 15),
                                         center=[840, 345])

            for i in range(self.n_targets):
                    self.targets.append(StableTarget(rad=randint(20, 40)))

            for i in range(self.n_targets):
                    self.targets.append(MovingTarget(rad=randint(20, 40)))

            self.barriers.append(self.barriers1)
            self.barriers.append(self.barriers2)
            # print(self.barriers)
            for i, barrier in enumerate(self.barriers):
                self.barrier_massive.extend(barrier.get_lines(barrier))

        elif self.level == 4:
            self.barriers1 = Barrier(coordABCD=[(187, 292), (370, 292), (445, 100), (505, 292), (703, 292),
                                                (529, 409), (604, 595), (445, 478), (292, 595), (349, 409)],
                                         color=(15, 15, 210),
                                         center=[445, 379])

            for i in range(self.n_targets):
                    self.targets.append(StableTarget(rad=randint(20, 40)))
            for i in range(self.n_targets):
                    self.targets.append(MovingTarget(rad=randint(20, 40)))

            self.barriers.append(self.barriers1)

            # print(self.barriers)
            for i, barrier in enumerate(self.barriers):
                self.barrier_massive.extend(barrier.get_lines(barrier))

        elif self.level == 5:
            self.barriers1 = Barrier(coordABCD=[(300, 300), (700, 300), (700, 600), (300, 600)],
                                         color=(140, 10, 250),
                                         center=[500, 450])

            for i in range(self.n_targets):
                    self.targets.append(StableTarget(rad=randint(20, 40)))
            for i in range(self.n_targets):
                    self.targets.append(MovingTarget(rad=randint(20, 40)))

            self.barriers.append(self.barriers1)

            # print(self.barriers)
            for i, barrier in enumerate(self.barriers):
                self.barrier_massive.extend(barrier.get_lines(barrier))

        elif self.level == 6:
            self.barriers1 = Barrier(coordABCD=[(0, 700), (200, 900), (0, 900)],
                                         color=(140, 10, 250),
                                         center=[0, 900])
            self.barriers2 = Barrier(coordABCD=[(1000, 700), (1000, 900), (800, 900)],
                                         color=(140, 10, 250),
                                         center=[1000, 900])
            self.barriers3 = Barrier(coordABCD=[(400, 0), (600, 0), (500, 100)],
                                         color=(210, 10, 250),
                                         center=[500, 0])

            for i in range(self.n_targets):
                    self.targets.append(StableTarget(rad=randint(20, 40)))
            for i in range(self.n_targets):
                    self.targets.append(MovingTarget(rad=randint(20, 40)))

            self.barriers.append(self.barriers1)
            self.barriers.append(self.barriers2)
            self.barriers.append(self.barriers3)
            # print(self.barriers)
            for i, barrier in enumerate(self.barriers):
                self.barrier_massive.extend(barrier.get_lines(barrier))

        elif self.level == 7:
            self.barriers1 = Barrier(coordABCD=[(0, 0), (200, 0), (0, 200)],
                                         color=(140, 40, 150),
                                         center=[0, 0])
            self.barriers2 = Barrier(coordABCD=[(800, 0), (1000, 0), (1000, 200)],
                                         color=(140, 40, 150),
                                         center=[1000, 0])
            self.barriers3 = Barrier(coordABCD=[(300, 900), (700, 900), (500, 700)],
                                         color=(110, 10, 150),
                                         center=[500, 900])

            for i in range(self.n_targets):
                    self.targets.append(StableTarget(rad=randint(20, 40)))
            for i in range(self.n_targets):
                    self.targets.append(MovingTarget(rad=randint(20, 40)))

            self.barriers.append(self.barriers1)
            self.barriers.append(self.barriers2)
            self.barriers.append(self.barriers3)
            # print(self.barriers)
            for i, barrier in enumerate(self.barriers):
                self.barrier_massive.extend(barrier.get_lines(barrier))

        elif self.level == 8:
            self.boders = []
            for i in range(51):
                self.boders.append((i*20, int(600 + 150*math.sin(i*0.2/math.pi))))
            self.boders.append((1000, 900))
            self.boders.append((0, 900))
            self.barriers1 = Barrier(coordABCD=self.boders,
                                         color=(140, 140, 50),
                                         center=[500, 900])


            for i in range(self.n_targets):
                    self.targets.append(StableTarget(rad=randint(20, 40)))
            for i in range(self.n_targets):
                    self.targets.append(MovingTarget(rad=randint(20, 40)))

            self.barriers.append(self.barriers1)

            # print(self.barriers)
            for i, barrier in enumerate(self.barriers):
                self.barrier_massive.extend(barrier.get_lines(barrier))

        elif self.level == 9:
            self.boders = []
            for i in range(51):
                self.boders.append((i*20, int(600 + 150*math.sin(i*0.2/math.pi))))
            self.boders.append((1000, 900))
            self.boders.append((0, 900))
            self.barriers1 = Barrier(coordABCD=self.boders,
                                         color=(40, 40, 50),
                                         center=[500, 900])

            print("You choosed level 9, Barrier repairing level")
            self.targets.append(Target(coord=[175, 132], vel=[-0.65,1.89], rad=60, color=[10, 10, 100]))
            self.targets.append(Target(coord=[226, 272], vel=[0.65,-1.89], rad=40, color=[200, 200, 200]))
            # self.targets.append(Target(coord=[226, 572], vel=[0.65,0], rad=40, color=[120, 120, 200]))

            self.barriers.append(self.barriers1)

            # print(self.barriers)
            for i, barrier in enumerate(self.barriers):
                self.barrier_massive.extend(barrier.get_lines(barrier))

        elif self.level == 10:

            self.barriers1 = Barrier(coordABCD=[(300, 250), (1000, 150), (1000, 200), (300, 300)], color=(210, 15, 15),
                                     center=[650, 200])
            self.barriers2 = Barrier(coordABCD=[(0, 500), (700, 700), (700, 750), (0, 550)], color=(15, 210, 15),
                                     center=[350, 625])

            for i in range(self.n_targets):
                self.targets.append(StableTarget(rad=randint(20, 40)))

            for i in range(self.n_targets):
                self.targets.append(MovingTarget(rad=randint(20, 40)))

            self.barriers.append(self.barriers1)
            self.barriers.append(self.barriers2)
            for i, barrier in enumerate(self.barriers):
                self.barrier_massive.extend(barrier.get_lines(barrier))


        elif self.level == 11:

            self.barriers1 = Barrier(coordABCD=[(0, 150), (700, 250), (700, 300), (0, 200)], color=(210, 115, 15),
                                     center=[350, 200])
            self.barriers2 = Barrier(coordABCD=[(300, 700), (1000, 500), (1000, 550), (300, 750)], color=(115, 210, 15),
                                     center=[650, 625])

            for i in range(self.n_targets):
                self.targets.append(StableTarget(rad=randint(20, 40)))

            for i in range(self.n_targets):
                self.targets.append(MovingTarget(rad=randint(20, 40)))

            self.barriers.append(self.barriers1)
            self.barriers.append(self.barriers2)
            for i, barrier in enumerate(self.barriers):
                self.barrier_massive.extend(barrier.get_lines(barrier))

        elif self.level == 12:
            self.boders = []
            for i in range(51):
                self.boders.append((i*20, int(800 + 100*math.sin(math.pi/2 + i*0.4/math.pi))))
            self.boders.append((1000, 900))
            self.boders.append((0, 900))
            self.barriers1 = Barrier(coordABCD=self.boders,
                                         color=(40, 140, 150),
                                         center=[500, 900])

            # print("You choosed level 12, Barrier repairing level")
            # self.targets.append(Target(coord=[175, 132], vel=[-0.65,1.89], rad=60, color=[10, 10, 100]))
            # self.targets.append(Target(coord=[226, 272], vel=[0.65,-1.89], rad=40, color=[200, 200, 200]))
            # self.targets.append(Target(coord=[226, 572], vel=[0.65,0], rad=40, color=[120, 120, 200]))

            for i in range(self.n_targets):
                    self.targets.append(StableTarget(rad=randint(20, 40)))
            for i in range(self.n_targets):
                    self.targets.append(MovingTarget(rad=randint(20, 40)))

            self.barriers.append(self.barriers1)

            # print(self.barriers)
            for i, barrier in enumerate(self.barriers):
                self.barrier_massive.extend(barrier.get_lines(barrier))

        else:
            print("You choosed None existing level, Ha Ha Ha")
            self.targets.append(Target(coord=[175, 132], vel=[-0.65,1.89], rad=60, color=[10, 10, 100]))
            self.targets.append(Target(coord=[226, 272], vel=[0.65,-1.89], rad=40, color=[200, 200, 200]))



    def process(self, events, screen):
        """
        Runs all necessary method for each iteration. Adds new targets, if previous are destroyed.
        """
        done = self.handle_events(events)

        if pg.mouse.get_focused():
            mouse_pos = pg.mouse.get_pos()
            self.gun.set_angle(mouse_pos)


        self.collide()
        self.bump_target()
        self.bump_balls()
        self.barrier_collision()
        self.power_counter()
        self.move()
        self.menu_manage(events)
        self.draw(screen)


        # if len(self.targets) == 0 and len(self.balls) == 0:
        if len(self.targets) == 0:
            if self.level == 15:
                self.level =1
            else:
                self.level += 1
            self.new_mission()

        return done

    def menu_manage(self, events):

        for event in events:
            if self.menu.check_on_top_menu_button_pressed() and event.type == pg.MOUSEBUTTONDOWN:
                self.levels_menu_visibility = True
                self.levels_menu.creat_levels_menu()
            if self.levels_menu_visibility:
                if self.levels_menu.check_pressed_button_in_levels_menu(events) == -1:
                    print("The Back menu button pressed in menu manager")
                    self.levels_menu_visibility = False
                    # self.levels_menu_visibility = False
                elif self.levels_menu.check_pressed_button_in_levels_menu(events) != 0:
                    self.level = self.levels_menu.check_pressed_button_in_levels_menu(events)
                    print('You have chosen level:', self.level)
                    self.new_mission()
                    self.levels_menu_visibility = False


    def handle_events(self, events):
        """
        Handles events from keyboard, mouse, etc.
        """

        self.mouse_pos = pg.mouse.get_pos()
        self.buttons = pg.mouse.get_pressed(3)
        self.key_buttons = pg.key.get_pressed()
        done = False
        for event in events:
            self.key = pg.key.get_pressed()
            # print(self.key)
            if self.key[pg.K_UP]:
                print(self.key)
            #     self.gun.move(-1)
            # elif self.key[pg.K_DOWN]:
            #     self.gun.move(-1)
            # print(event)
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.KEYDOWN:
                print(event.key)
                if event.key == pg.K_UP:
                    self.gun.move(-5)
                elif event.key == pg.K_DOWN:
                    self.gun.move(5)
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1 and sum([(self.gun.coord[i] - self.mouse_pos[i]) ** 2 for i in range(2)]) ** 0.5 < 15:
                    self.gun.activate()
                    self.gun_trigger = True
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1 and self.gun_trigger:
                    self.balls.append(self.gun.strike())
                    self.score_t.b_used += 1
                    self.gun_trigger = False

        return done

    def power_counter(self):
        self.total_power = 0
        for ball in self.balls:
            self.total_power += ball.power_counter()
        for target in self.targets:
            self.total_power += target.power_counter()
        self.score_t.total_power = self.total_power
        # print("                                                                                     "
        #       "                                         Total Power of all balls and Targets = %1.f" %self.total_power)



    def draw(self, screen):
        """
        Runs balls', gun's, targets' and score table's drawing method.
        """

        # self.draw_sun_on_the_screen()
        for ball in self.balls:
            ball.draw_shadow(screen)
        for target in self.targets:
            target.draw_shadow(screen)
        self.gun.draw(screen)
        for barrier in self.barriers:
            barrier.draw(screen)
        for ball in self.balls:
            ball.draw(screen)
        for target in self.targets:
            target.draw(screen)
        self.score_t.draw(screen)
        # self.menu.draw_on_top_menu_button()

        if self.menu.check_on_top_menu_button_marked():
            self.menu.draw_on_top_menu_button_mareked()
        elif self.menu.check_on_top_menu_button_pressed():
            self.menu.draw_on_top_menu_button_pressed()
        else:
            self.menu.draw_on_top_menu_button()

        if self.levels_menu_visibility:
            self.levels_menu.draw_levels_menu()




    def draw_sun_on_the_screen(self, sun_pos=None):

        if sun_pos == None:
            self.sun_pos = [SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2]
        else:
            self.sun_pos = sun_pos
        self.color = BLACK
        self.coord = self.sun_pos
        self.rad = int((sum((SCREEN_SIZE[i]//2)**2 for i in range (2)))**0.5)
        self.rad_shift = 0.8
        self.steps = int(self.rad / 2)
        self.color_delta = [253, 253, 253]
        self.color2 = [253, 253, 253]
        self.coord2 = [0, 0]
        for i in range(self.steps):
            for j in range(3):
                self.color_delta[j] = 255 - self.color[j]
                self.color2[j] = int(self.color[j] + self.color_delta[j] -\
                                 (self.color_delta[j] ** 2 - ((i + 1) * self.color_delta[j] / self.steps) ** 2) ** 0.5)
            self.coord2[0] = int(self.coord[0] - self.rad * self.rad_shift * (i + 1) * 0.8 / self.steps)
            self.coord2[1] = int(self.coord[1] - self.rad * self.rad_shift * (i + 1) * 0.8 / self.steps)
            self.rad2 = 1.4 * (self.rad ** 2 - ((i + 1) * self.rad / self.steps) ** 2) ** 0.5
            pg.draw.circle(screen, self.color2, self.coord2, int(self.rad2))

    def move(self):
        """
        Runs balls' and gun's movement method, removes dead balls.
        """
        dead_balls = []
        for i, ball in enumerate(self.balls):
            ball.move(grav=0.05)
            if not ball.is_alive:
                dead_balls.append(i)
        for i in reversed(dead_balls):
            self.balls.pop(i)
        for i, target in enumerate(self.targets):
            target.move(grav=0.02)
        self.gun.gain()

    def collide(self):
        """
        Checks whether balls bump into targets, sets balls' alive trigger.
        """
        collisions = []
        targets_c = []
        for i, ball in enumerate(self.balls):
            for j, target in enumerate(self.targets):
                if target.check_collision(ball):
                    collisions.append([i, j])
                    targets_c.append(j)
                else:
                    if target.check_collision_target(ball):
                        target.bump_target_vel_change(ball)
                    if ball.check_collision_target(target):
                        ball.bump_target_vel_change(target)
        targets_c.sort()
        for j in reversed(targets_c):
            self.score_t.t_destr += 1
            self.targets.pop(j)

    def bump_target(self):
        """
        Checks whether target bump into targets, sets balls' alive trigger.
        """
        for i, target in enumerate(self.targets):
            for j, target in enumerate(self.targets):
                if i != j:
                    self.target1 = self.targets[i]
                    self.target2 = self.targets[j]
                    if self.target1.check_collision_target(self.target2):
                        self.target1.bump_target_vel_change(self.target2)


    def bump_balls(self):
        """
        Checks whether ball bump into ball, sets balls' alive trigger.
        """
        for i, balls in enumerate(self.balls):
            for j, balls in enumerate(self.balls):
                if i != j:
                    self.ball1 = self.balls[i]
                    self.ball2 = self.balls[j]
                    if self.ball1.check_collision_target(self.ball2):
                        self.ball1.bump_target_vel_change(self.ball2)

    def barrier_collision(self):
        for i, target in enumerate(self.targets):
            self.target1 = self.targets[i]
            for j in range(len(self.barrier_massive)):
                self.target1.chek_collision_barrier(self.barrier_massive[j])

        for i, balls in enumerate(self.balls):
            self.ball1 = self.balls[i]
            for j in range(len(self.barrier_massive)):
                self.ball1.chek_collision_barrier(self.barrier_massive[j])



flags = pg.RESIZABLE
screen = pg.display.set_mode(SCREEN_SIZE, flags)
# print(pg.display.get_window_size())
pg.display.set_caption("Balls by Ivan Tsibin 2021 based on Khirianov's GUN")


done = False
clock = pg.time.Clock()

mgr = Manager(n_targets=10)

while not done:
    clock.tick(60)
    screen.fill(BLACK)
    done = mgr.process(pg.event.get(), screen)
    pg.display.flip()
    window_size = pg.display.get_window_size()
    # print(window_size[0])
    if window_size != SCREEN_SIZE:
        print("y", window_size[1])
        if window_size[0] > START_SCREEN_SIZE[0] and window_size[1] > START_SCREEN_SIZE[1]:
            print("Let's change window_size ", window_size[0])
            SCREEN_SIZE = window_size
            screen = pg.display.set_mode(SCREEN_SIZE, flags)


pg.quit()