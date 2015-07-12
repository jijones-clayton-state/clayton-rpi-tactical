#!/usr/bin/python
"""Two-Dimensional Vehicles, using Pygame sprites.

   This is a bare-bones module....finish documenation later.
"""

import os, sys, pygame
from pygame.locals import RLEACCEL, QUIT, MOUSEBUTTONDOWN

INF = float('inf')

# Note: Adjust this depending on where this file ends up.
sys.path.insert(0, '../vpoints')
from point2d import Point2d

# Point2d functions return radians, but pygame wants SCREEN_DEGrees. The negative
# is needed since y coordinates increase downwards on screen. Multiply a
# math radians result by SCREEN_DEG to get pygame screen-appropriate degrees.
SCREEN_DEG = -57.2957795131

# A PointMass has its heading aligned with velocity. However, if the speed is
# almost zero (squared speed is below this threshold), we skip alignment in
# order to avoid jittery behaviour.
SPEED_EPSILON = .000000001


def load_image(name, colorkey=None):
    """Loads image from current working directory for use in pygame.

    Parameters
    ----------
    name: string
        Image file to load (must be pygame-compatible format)
    colorkey: pygame.Color
        Used to set a background color for this image that will be ignored
        during blitting. If set to -1, the upper-left pixel color will be
        used as the background color. See pygame.Surface.set_colorkey() for
        further details.

    Returns
    -------
    (pygame.Surface, pygame.rect):
        For performance reasons, the returned Surface is the same format as
        the pygame display. The alpha channel is removed.

    """
    imagefile = os.path.join(os.getcwd(), name)
    try:
        image_surf = pygame.image.load(imagefile)
    except pygame.error, message:
        print 'Error: Cannot load image:', name
        raise SystemExit(message)

    # This converts the surface for maximum blitting performance,
    # including removal of any alpha channel:
    image_surf = image_surf.convert()

    # This sets the background (ignored during blit) color:
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image_surf.get_at((0,0))
        image_surf.set_colorkey(colorkey, RLEACCEL)
    return image_surf, image_surf.get_rect()

class PointMass2d(pygame.sprite.Sprite):
    """A pygame.Sprite with some basic physics.

    Paramters
    ---------
    img_surf: pygame.Surface
        Contains the image of the sprite; used for blitting.
    img_rect: pygame.rect
        Pygame rectangle with sprite information; used for blitting.
    position: Point2d
        Center of mass, in screen coordinates.
    radius: float
        Bounding radius of the object.
    velocity: Point2d
        Velocity vector, in screen coordinates.

    Notes
    -----
    It is recommended to use the load_image() function above to initialize
    the image surface and rectangle, then pass the values to this function.
    One reason for separating these functions is to allow multiple sprites
    to use the same image file.
    """

    def __init__(self, img_surf, img_rect, position, radius, velocity):
        # Must call pygame's Sprite.__init__ first!
        pygame.sprite.Sprite.__init__(self)

        # Pygame image information for blitting
        self.orig = img_surf
        self.image = img_surf
        self.rect = img_rect

        # Basic object physics
        self.pos = Point2d(position[0], position[1])  # Center of object
        self.radius = radius                          # Bounding radius
        self.vel = Point2d(velocity[0], velocity[1])  # Current Velocity

        # Normalized front/left vector in world coordinates
        try:
            self.front = velocity.unit()
        except ZeroDivisionError:
            # If velocity is <0,0>, set facing to screen upwards
            self.front = Point2d(0,0)

        # Movement constraints
        ## TODO: Put these in the function argument, perhaps as **kwargs
        self.mass = float(1.0)
        self.maxspeed = float(5.0)
        self.maxforce = float(1.5)

    def move(self, delta_t):
        """Update the position of this object, using its current velocity.

        Parameters
        ----------
        delta_t: float
            Time increment since last move.
        """
        self.pos = self.pos + self.vel.scale(delta_t)
        self.rect.center = self.pos[0], self.pos[1]

    def _rotate_for_blit(self):
        """Used to rotate the object's image prior to blitting.

        Note
        ----
        This function does not update any physics, it only rotates the image,
        based on the object's current front vector.
        """
        theta = self.front.angle()*SCREEN_DEG
        center = self.rect.center
        self.image = pygame.transform.rotate(self.orig, theta)
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self, delta_t=1.0):
        """Update the object's position. Update velocity/facing if needed.

        Parameters
        ----------
        dt: float
            Time increment since last update. Default = 1.0.

        Note
        ----
        This is intended to be called by pygame.sprite.RenderPlain()'s update
        method each cycle. This passes the same arguments to each sprite, so
        any object-specific behaviour must be computed within this function.
        Need to think of a clever way around this, otherwise we'd have to
        override this for each subclass, which defeats the point.
        """

# This was the old code, when we could pass in a force to this function.
#        if force_vector:
#            # Don't exceed our maximum force; compute acceleration/velocity
#            sforce.truncate(self.maxforce)
#            accel = sforce.scale(1.0/self.mass)
#            self.vel = self.vel + accel*dt

        # Don't exceed our maximum speed
        self.vel.truncate(self.maxspeed)

        # A PointMass has heading aligned with velocity. However, if the
        # velocity is very small, we skip alignment to avoid jittering.
        if self.vel.sqnorm() > SPEED_EPSILON:
            self.front = self.vel.unit()
            #self.left = Point2d(-self.front[1],self.front[0])

        # Movement and image rotation:
        self.move(delta_t)
        self._rotate_for_blit()



if __name__ == "__main__":
    pygame.init()

    # Display constants
    size = sc_width, sc_height = 640, 480
    screen = pygame.display.set_mode(size)
    bgcolor = 111, 145, 192

    # Sprite images and pygame rectangles
    numobj = 2
    img = list(range(numobj))
    rec = list(range(numobj))
    img[0], rec[0] = load_image('rpig.png', -1)
    for i in range(1, numobj):
        img[i], rec[i] = load_image('ypig.png', -1)

    # Object physics
    pos = [Point2d(10, i*sc_height/(1+numobj)) for i in range(1, 1+numobj)]
    vel = Point2d(20,0)

    # Create any array of objects for pygame
    obj = [PointMass2d(img[i], rec[i], pos[i], 20, vel) for i in range(numobj)]
    obj[0].maxspeed = 2.0

    allsprites = pygame.sprite.RenderPlain(obj)

    while 1:
        for event in pygame.event.get():
            if event.type in [QUIT, MOUSEBUTTONDOWN]:
                pygame.quit()
                sys.exit()

        allsprites.update(0.1)

        #pygame.time.delay(5)

        # Render
        screen.fill(bgcolor)
        allsprites.draw(screen)
        pygame.display.flip()


    pygame.time.delay(2000)
    