/*
 * @File Name: ecs.d
 * @Author: Copyright (c) 2017-01-07 17:07:54 gilletthernandez
 * @Date:   2017-01-07 17:07:54
 * @Last Modified by:   Gillett Hernandez
 * @Last Modified time: 2017-01-12 13:59:38
 */
import std.stdio;
import std.math;

//class PositionComponent;
//class PhysicsComponent;
//class SpriteComponent;
//class EventComponent;

static immutable int SYSTEM_COUNT       =      2;
static immutable int ENTITY_COUNT       =    100;

static immutable int COMPONENT_NONE     =      0;
static immutable int COMPONENT_POSITION = 1 << 0;
static immutable int COMPONENT_PHYSICS  = 1 << 1;
static immutable int COMPONENT_SPRITE   = 1 << 2;
static immutable int COMPONENT_EVENT    = 1 << 3;

T[n] s(T, size_t n)(auto ref T[n] array) pure nothrow @nogc @safe {
    return array;
}

template components(string name) {
    const char[] components = "world." ~ name;
}


auto get_component(string name)(int id) {
    return &mixin(components!name)[id];
}

alias void function() UpdateType;

struct World {
    UpdateType[SYSTEM_COUNT] systems;
    int[ENTITY_COUNT] mask;

    PositionComponent[ENTITY_COUNT] position;
    PhysicsComponent[ENTITY_COUNT] physics;
    //SpriteComponent[ENTITY_COUNT] sprite;
    //EventComponent[ENTITY_COUNT] event;
    void update() {
        foreach (UpdateType updatemethod; systems) {
            writeln("update in World.update");
            updatemethod();
        }
    }
};

struct Component {
    int id;
    //this(int _id) {
    //    id = _id;
    //}
}

class Entity {
    int id;
    static World* world;
    this(int mask) {
        this.id = makeEntity();
        world.mask[id] = mask;
    }
    static final auto get_component(string name)(int id) {
        return mixin(components!name)[id];
    }

    final auto get_component(string name)() {
        return mixin(components!name)[this.id];
    }

    static void provide(World * world) {
        Entity.world = world;
    }

    final bool set_component(string name, T)(T component) {
        mixin(components!name)[this.id] = component;
        return true;
    }

    static int makeEntity() {
        foreach(int entity; 0..ENTITY_COUNT) {
            if (world.mask[entity] == COMPONENT_NONE) {
                return entity;
            }
        }
        throw new Exception("EntityAllocationError");
    }
}

class System{
    static int mask;
    static World * world;
    static void update(T)() {
        foreach(entity; 0..ENTITY_COUNT) {
            if ((world.mask[entity] & T.mask) == T.mask) {
                T.c_update(entity);
            }
        }
    }

    static void provide(World * world) {
        System.world = world;
    }

    static void c_update(int entity) {};
}

struct PositionComponent{
    int id;
    real x;
    real y;
    this(int _id, real[2] _pos) {
        id = _id;
        pos = _pos;
    }
    @property real[2] pos() { return [x, y]; }
    @property real[2] pos(real[2] val) { x = val[0]; y=val[1]; return val; }
}

struct PhysicsComponent {
    int id;
    real x;
    real y;
    real grav;
    this(int _id, real[2] _v, real _grav){
        id = _id;
        v = _v;
        grav = _grav;
    }
    @property real[2] v() { return [x, y]; }
    @property real[2] v(real[2] val) { x = val[0]; y=val[1]; return val; }
}

class PositionSystem : System{
    static int mask = COMPONENT_POSITION;
    static void c_update(int entity) {
        writeln("in c_update in PositionSystem");
        PositionComponent* p = &world.position[entity];
        writeln("after get in PositionSystem", p.id);
        p.x = round(p.x);
        p.y = round(p.y);
        writeln("after round in PositionSystem");
    }
}

/**
 * PhysicsSystem
 */
class PhysicsSystem : System{
    static int mask = COMPONENT_PHYSICS;
    static void c_update(int entity) {
        writeln("in c_update in PhysicsSystem");
        auto p = &world.position[entity];
        auto v = &world.physics[entity];
        writeln(world.mask[entity], " ", entity, " ", p.id, " ", v.id);
        assert(p.id == entity);
        assert(v.id == entity);
        v.y -= v.grav/2;
        p.y += v.y;
        v.y -= v.grav/2;
        p.x += v.x;
    }
}

class Player : Entity {
    static immutable mask = COMPONENT_EVENT
                           |COMPONENT_SPRITE
                           |COMPONENT_PHYSICS
                           |COMPONENT_POSITION;
    this() {
        super(mask);
        this.set_component!"position"(PositionComponent(this.id, [100.1,100.1]));
        this.set_component!"physics"(PhysicsComponent(this.id, [0,0], 3));
    }
}

void main(){
    World world = World();
    writeln(world.mask[0]);
    Entity.provide(&world);
    System.provide(&world);
    world.systems[0] = &System.update!PositionSystem;
    world.systems[1] = &System.update!PhysicsSystem;
    //world.systems[2] = &System.update!EventSystem;
    //world.systems[0] = &System.update!SpriteSystem;
    auto player = new Player();
    writeln(player.get_component!"position".pos);
    world.update();
    writeln(player.get_component!"position".pos);
    writeln(world.mask[0]);
}
