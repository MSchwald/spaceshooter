from __future__ import annotations
from dataclasses import dataclass
from math import sqrt, sin, cos, pi
from random import uniform

class Vector:
    """Simple class for 2d vector calculus,
    could also be replaced by pygames Vector2 class."""

    def __init__(self, x: int | float, y: int | float):
        self.x = x
        self.y = y

    def __add__(self, other: Vector) -> Vector:
        return Vector(self.x + other.x, self.y + other.y)

    def __neg__(self) -> Vector:
        return Vector(-self.x, -self.y)

    def __sub__(self, other: Vector) -> Vector:
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other: Vector | int | float) -> int | float | Vector:
        """scalar product or multiplication with scalars"""
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        elif isinstance(other, (int, float)):
            return Vector(other * self.x, other * self.y)
        return NotImplemented

    def __rmul__(self, other: Vector | int | float) -> int | float | Vector:
        """allows also for multiplication with scalars from the right"""
        return self * other

    def __truediv__(self, s: int | float) -> Vector:
        if isinstance(s, (int, float)):
            if s == 0:
                raise ValueError("Division by zero")
            return self * (1 / s)
        return NotImplemented

    def __iter__(self) -> tuple:
        yield self.x
        yield self.y

    def change_direction(self, other: Vector) -> Vector:
        """Changes direction of a vector while preserving its norm"""
        self = norm(self) * normalize(other)

    def change_norm(self, n: int | float) -> Vector:
        """Changes norm of a vector while preserving its direction"""
        self = n * normalize(self)

    def clamp(self, min_v: Vector, max_v: Vector) -> Vector:
        """Clamps x and y coordinates of vector to minimal or maximal possible value
        when outside the given ranges of x and y values"""
        return Vector(
            max(min_v.x, min(self.x, max_v.x)),
            max(min_v.y, min(self.y, max_v.y))
        )

    def randomize_direction(self, phi_min: float = 0,
                                phi_max: float = 2 * pi) -> Vector:
        """Changes direction of a vector randomly while preserving its norm"""
        phi = uniform(phi_min, phi_max)
        self = norm(self) * Vector(cos(phi), sin(phi))

def norm(v: Vector) -> int | float:
    """Euclidean norm of a vector"""
    return sqrt(v * v)

def norm2(v: Vector) -> int | float:
    """Square of Euclidean norm; avoids computing sqrt function for faster computations"""
    return v * v

def normalize(v: Vector) -> Vector:
    """Changes norm of a vector to 1 while preserving its direction"""
    n = norm(v)
    return v if n == 0 else v / n

def random_direction(phi_min: float = 0,
                    phi_max: float = 2 * pi) -> Vector:
    """Returns a random unit vector"""
    phi = uniform(phi_min, phi_max)
    return Vector(cos(phi), sin(phi))

def turn_by_angle(v: Vector, phi: float) -> Vector:
    """Turns a vector by a given angle (in radians), counterclockwise"""
    return Vector(v.x*cos(phi)-v.y*sin(phi), v.x*sin(phi)+v.y*cos(phi))

class Ball:
    """Simple class for computations of moving 3d balls"""
    def __init__(self, pos: Vector, vel: Vector, r: float):
        self.pos, self.vel, self.r = pos, vel, r

def elastic_collision(v1: Vector, v2: Vector, m1: float, m2: float, n: Vector) -> tuple(Vector, Vector):
    """Calculate new velocity vectors of two masses m1, m2
    after they collide elastically in a given normal direction n"""
    factor = 2 * (v1 - v2) * n / (m1 + m2)
    return v1 + (-m2 * factor) * n, v2 + (m1 * factor) * n

def inelastic_collision(p1: Vector, p2: Vector, v1: Vector, v2: Vector, m1: float, m2: float) -> tuple(Vector, Vector):
    """return center of gravity of two masses m1, m2
    and their velocity after they merge by a completely inelastic collision"""
    m = m1 + m2
    return (m1 * p1 + m2 * p2) / m, (m1 * v1 + m2 * v2) / m

def ball_collision_data(ball1: Ball, ball2: Ball, m1: float, m2: float) -> tuple(float | None, Vector, Vector):
    """if two balls collided elastically in the past,
    return the (negative) time of their collision and their new velocity vectors afterwards"""
    dp, dv = ball1.pos - ball2.pos, ball1.vel - ball2.vel
    n2dv, n2dp, dpdv,  = norm2(dv), norm2(dp), dp * dv
    d2 = (ball1.r + ball2.r) ** 2
    if (n2dv > 1e-8     # avoids division problems
        and n2dp < d2   # balls intersect
        and dpdv < 0    # balls move towards each other (makes collision rendering more stable)
    ):
        collision_time = (-dpdv - sqrt(dpdv ** 2 - n2dv * (n2dp - d2))) / n2dv
        new_v1, new_v2 = elastic_collision(ball1.vel, ball2.vel, m1, m2, normalize(dp))
        return collision_time, new_v1, new_v2
    return None, ball1.vel, ball2.vel