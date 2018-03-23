#!/usr/bin/env python
# like the testsprite.c that comes with sdl, this pygame version shows
#   lots of sprites moving around.


import pygame, sys, os
from pygame.locals import *
from random import randint
from time import time
import gc
import pygame.joystick
from pygame.compat import xrange_

##import FastRenderGroup as FRG
import pygame.sprite as FRG

if "-psyco" in sys.argv:
    try:
        import psyco
        psyco.full()
    except Exception:
        print ("No psyco for you!  psyco failed to import and run.")

jit_on = True
try:
    import pypyjit
except:
    pass
    jit_on = False

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')






# use this to use update rects or not.
#  If the screen is mostly full, then update rects are not useful.
update_rects = True
if "-update_rects" in sys.argv:
    update_rects = True
if "-noupdate_rects" in sys.argv:
    update_rects = False

use_static = False
if "-static" in sys.argv:
    use_static = True


use_FastRenderGroup = False
if "-FastRenderGroup" in sys.argv:
    update_rects = True
    use_FastRenderGroup = True


flags = 0
if "-flip" in sys.argv:
    flags ^= DOUBLEBUF

if "-fullscreen" in sys.argv:
    flags ^= FULLSCREEN

if "-sw" in sys.argv:
    flags ^= SWSURFACE

use_rle = True

if "-hw" in sys.argv:
    flags ^= HWSURFACE
    use_rle = False


screen_dims = [640, 480]

if "-height" in sys.argv:
    i = sys.argv.index("-height")
    screen_dims[1] = int(sys.argv[i+1])

if "-width" in sys.argv:
    i = sys.argv.index("-width")
    screen_dims[0] = int(sys.argv[i+1])

if "-alpha" in sys.argv:
    use_alpha = True
else:
    use_alpha = False

plot = '-plot' in sys.argv


print (screen_dims)


##class Thingy(pygame.sprite.Sprite):
##    images = None
##    def __init__(self):
##        pygame.sprite.Sprite.__init__(self)
##        self.image = Thingy.images[0]
##        self.rect = self.image.get_rect()
##        self.rect.x = randint(0, screen_dims[0])
##        self.rect.y = randint(0, screen_dims[1])
##        #self.vel = [randint(-10, 10), randint(-10, 10)]
##        self.vel = [randint(-1, 1), randint(-1, 1)]
##
##    def move(self):
##        for i in [0, 1]:
##            nv = self.rect[i] + self.vel[i]
##            if nv >= screen_dims[i] or nv < 0:
##                self.vel[i] = -self.vel[i]
##                nv = self.rect[i] + self.vel[i]
##            self.rect[i] = nv

class Thingy(FRG.DirtySprite):
    images = None
    def __init__(self):
##        pygame.sprite.Sprite.__init__(self)
        FRG.DirtySprite.__init__(self)
        self.image = Thingy.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = randint(0, screen_dims[0])
        self.rect.y = randint(0, screen_dims[1])
        #self.vel = [randint(-10, 10), randint(-10, 10)]
        self.vel = [randint(-1, 1), randint(-1, 1)]
        self.dirty = 2

    def update(self):
        for i in [0, 1]:
            nv = self.rect[i] + self.vel[i]
            if nv >= screen_dims[i] or nv < 0:
                self.vel[i] = -self.vel[i]
                nv = self.rect[i] + self.vel[i]
            self.rect[i] = nv

class Static(FRG.DirtySprite):
    images = None
    def __init__(self):
        FRG.DirtySprite.__init__(self)
        self.image = Static.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = randint(0, 3*screen_dims[0]/4)
        self.rect.y = randint(0, 3*screen_dims[1]/4)



def main(update_rects = True,
        use_static = False,
        use_FastRenderGroup = False,
        screen_dims = [640, 480],
        use_alpha = False,
        flags = 0,
        plot = False):
    """Show lots of sprites moving around

    Optional keyword arguments:
    update_rects - use the RenderUpdate sprite group class (default True)
    use_static - include non-moving images (default False)
    use_FastRenderGroup - Use the FastRenderGroup sprite group (default False)
    screen_dims - Pygame window dimensions (default [640, 480])
    use_alpha - use alpha blending (default False)
    flags - additional display mode flags (default no addiontal flags)

    """
    global jit_on
    if use_FastRenderGroup:
        update_rects = True


    #pygame.init()
    pygame.display.init()



    #if "-fast" in sys.argv:

    screen = pygame.display.set_mode(screen_dims, flags)


    # this is mainly for GP2X, so it can quit.
    pygame.joystick.init()
    num_joysticks = pygame.joystick.get_count()
    if num_joysticks > 0:
        stick = pygame.joystick.Joystick(0)
        stick.init() # now we will receive events for the joystick


    screen.fill([0,0,0])
    pygame.display.flip()
    sprite_surface = pygame.image.load(os.path.join(data_dir, "asprite.bmp"))
    sprite_surface2 = pygame.image.load(os.path.join(data_dir, "static.png"))

    if use_rle:
        sprite_surface.set_colorkey([0xFF, 0xFF, 0xFF], SRCCOLORKEY|RLEACCEL)
        sprite_surface2.set_colorkey([0xFF, 0xFF, 0xFF], SRCCOLORKEY|RLEACCEL)
    else:
        sprite_surface.set_colorkey([0xFF, 0xFF, 0xFF], SRCCOLORKEY)
        sprite_surface2.set_colorkey([0xFF, 0xFF, 0xFF], SRCCOLORKEY)

    if use_alpha:
        sprite_surface = sprite_surface.convert_alpha()
        sprite_surface2 = sprite_surface2.convert_alpha()
    else:
        sprite_surface = sprite_surface.convert()
        sprite_surface2 = sprite_surface2.convert()

    Thingy.images = [sprite_surface]
    if use_static:
        Static.images = [sprite_surface2]

    if len(sys.argv) > 1:
        try:
            numsprites = int(sys.argv[-1])
        except Exception:
            numsprites = 100
    else:
        numsprites = 100
    sprites = None
    if use_FastRenderGroup:
##        sprites = FRG.FastRenderGroup()
        sprites = FRG.LayeredDirty()
    else:
        if update_rects:
            sprites = pygame.sprite.RenderUpdates()
        else:
            sprites = pygame.sprite.Group()

    for i in xrange_(0, numsprites):
        if use_static and i%2==0:
            sprites.add(Static())
        sprites.add(Thingy())

    done = False
    frames = 0
    start = time()

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill([0,0,0])

    frame_times = []
    gc.disable()
    frames_since_last_gc = 0
    while not done:
        t0 = time()
        for event in pygame.event.get():
            if event.type in [KEYDOWN, QUIT, JOYBUTTONDOWN]:
                done = True

        if not update_rects:
            screen.fill([0,0,0])

##        for sprite in sprites:
##            sprite.move()

        if update_rects:
            sprites.clear(screen, background)
        sprites.update()

        rects = sprites.draw(screen)

        t1 = time()
        # print (t1-t0)
        # gc.collect(0)

        if t1 - t0 > 0.011:
            print('slow')
        # print('frame')
        if (t1-t0 < 0.0011 and frames_since_last_gc > 30):
            # print('collecting')
            frames_since_last_gc = 0
            # gc.collect(0)
        else:
            frames_since_last_gc += 1
        if update_rects:
            pygame.display.update(rects)
        else:
            pygame.display.flip()

        # frame_times.append(time() - t0)
        frame_times.append(t1 - t0)
        if jit_on and time() - start > 10:
            # print('turning off pypyjit')
            # pypyjit.set_param("off")
            jit_on = 0
        frames += 1
    end = time()
    print ("FPS: %f" % (frames / ((end - start))))
    pygame.quit()

    if plot:

        msg = '\n'.join(('update_rects:%s,',
            'use_static:%s,',
            'use_FastRenderGroup:%s',
            'screen_dims:%s,',
            'use_alpha:%s,',
            'flags: %s')) % (
            update_rects,
            use_static,
            use_FastRenderGroup,
            screen_dims,
            use_alpha,
            flags
        )
        print(msg)
        import pickle
        with open('spriteplot.pickle', 'wb') as picklef:
            pickle.dump({'msg': msg, 'frame_times': frame_times}, picklef)




if __name__ == "__main__":


    if '-plotpickle' in sys.argv:
        import pickle
        with open('spriteplot.pickle', 'rb') as picklef:
            data = pickle.load(picklef)
            print(data['msg'])

        import matplotlib.pyplot as plt
        print(len(data['frame_times']))
        plt.plot(data['frame_times'][:1200])
        plt.plot(data['frame_times'][-1200:])

        # n, bins, patches = plt.hist(data['frame_times'], 50, normed=1, facecolor='g', alpha=0.75)

        # plt.ylabel('per frame time. pypy gc.disable(), pypyjit.set_param("off") after 10s')
        # plt.ylabel('30fps. pypy, 1000 sprites')
        # plt.ylabel('30fps. python36, 1000 sprites, gc.disable()')
        # plt.ylabel('30fps. pypy, 1000 sprites, gc.disable()')
        plt.ylabel('python3.6, 100 sprites. gc.disable()')
        # plt.ylabel('Time per frame, python3.6, gc.disable()')
        # plt.ylabel('Time per frame, python3.6, gc.disable()')
        plt.show()
    else:
        main(update_rects,
            use_static,
            use_FastRenderGroup,
            screen_dims,
            use_alpha,
            flags,
            plot)
