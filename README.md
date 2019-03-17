# Collider #

This is an easy to use swept collision detecition and response Python library for axis-aligned rectangles.
It is ideal to use for platformer or tile-based games where full-featured physics engine such as Box2D or Bullet would be an overkill.

Features:
 
- minimalistic and easy-to-use,
- uses swept collision detection to prevent tunelling,
- optimized to reduce the number of collision tests
- includes some basic responses to collisions
- allows to add own collision responses

Where collider is NOT not suitable:

- realistic simulations
- games requiring shapes other than axis-aligned rectangles

# Basic usage #

In order to use collider, download and import `collider.py` file from the repository.
The module contains a few classes which let you get startes.

## Positions and boxes ##

All positions in the `collider` are represented using `Vector2(x, y)` namedtuple containing coordinates. The fields can be  accessed just as a with regular tuple or throught named fields:

```python
vec = Vector2(3.6, 4.2)
vec[0]  # == 3.6
vec.y  # == 4.2
x, y = vec  # x == 3.6, y == 4.2
```

Note that the `collider` uses floating point numbers to represent positions and dimensions, so the positions in the world is not limited by integer pixel coordinates. Further, it's usually advisable to make object position in the world independent of the rendering system.

The elements taking part in the collisions are `Rectangle` objects. They can be created using the position and dimensions

`Rectangle(x, y, w, h)`

These values can be accessed and changes directly from the object's fields  `x, y, w, h`. Additionally, `pos` and `size` properties are available to get and set position and size using tuples.

## Creating World ##

The `World` is the container for the rectangles.
It acts as a scene for the rectangles resolving all movements and collisions.
To create a new world use a default empty constructor

`world = World()`

You can create as many worlds as you want i.e. to represent different locations in your game.
The objects can only collide with other objects in the same world.

## Adding object ##

A new rectangle can be added to the world using

`world.add(rect)`

The library does not prevent adding the same rectangle to more than one world. However, note that the position is tied to the rectangle and any changes will be reflected in all worlds the rectangle was added to.

## Removing object ##

Similarly, the rectangle can be removed from the world using

`world.remove(rect)`

## Testing collisions ##

Before the object can be moved to a new position the collisions happening on the way need to be resolved.
The movement of the object with collision resolving can be checked using

`position, collisions = world.check_move(rect, target, filter)`

The parameters that the method accepts are following:

| param | type | description |
|---|---|---|
| rect | Rectangle | rectangle to be moved |
| target | Vector2 | a new position for the rectangle |
| filter | function | function used to determine collision response |

The value returned by `check_move` is a tuple `(Vector2, List[Collision])` containing the final position of the rectangle and the list of collisions which occured on the way.
Keep in mind that the final position will not necessarily be the same as the target position provided.
Some of the collisions may change the trajectory of the object.
Also, `check_move` will not attempt to modify any positions of the objects and it's up to the user to change it accordingly.

The `filter` function should accept two arguments, the rectangle currently being moved (`this`) and the one it collided with (`other`), and return the response type.

`filter(this: Rectangle, other: Rectangle) -> str`

If the returned value is `None` or `"ignore"` the calculation of collision between `this` and `other` will be skipped saving computation time.
Other accepted response types are:

 - `"block"` : the object will be blocked by the obstacle stopping at the point of contact. Useful for projectiles/arrows/bullets which does not penetrate throught objects.
 - `"pass"` : the objects should pass through each other without changing the trajectory. The only difference between `"pass"` and `"ignore"` is that the collision is recorded. Useful for collisions with coins or other collectibles.
 - `"slide"` : the object will slide along the side it collided with. Useful for collision betwen a hero and a wall as it allows walking along the wall instead of "sticking" to it.
 - `"bounce"` : the object will bounce off the side it collided with. Useful for bouncing bullets or mirrors reflecting rays.
 - `"return"` : the object will be reflected back in the direction it came from. 

### Collisions ###

The second parameter returned by `check_move` is the list of collisions encountered by the object on its way. The collisions are ordered by their occurence.
Each collision object contains the following fields:

| field | type | description |
|---|---|---|
| rect | Rectangle | The rectangle that the object collided with |
| distance | float | Number between 0 and 1 telling how far the object travelled along the straight line when the collision occurred. Used for internal sorting. |
| normal | Vector2 | The normal to the collision side. Either -1, 0 or 1 along x or y direction. |
| touch | Vector2 | Position of the moved object where the collision occurred. |
| reponse | str | The response type used to resolve the collision |

The most useful fields are `rect`, which tells which rectangles the object collided with, and `normal`, which tells the direction the collision came form.

# Advanced usage #
(coming later)

# Documentation #
(coming later)