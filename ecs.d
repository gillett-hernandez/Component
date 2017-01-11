/*
 * @File Name: ecs.d
 * @Author: Copyright (c) 2017-01-07 17:07:54 gilletthernandez
 * @Date:   2017-01-07 17:07:54
 * @Last Modified by:   gilletthernandez
 * @Last Modified time: 2017-01-11 13:53:13
 */
import std.stdio;
import std.math;

//class PositionComponent;
//class PhysicsComponent;
//class SpriteComponent;
//class EventComponent;

static immutable int SYSTEM_COUNT       =      1;
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
    //PhysicsComponent[ENTITY_COUNT] physics;
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
    real[2] pos;
    this(int _id, real[2] _pos) {
        id = _id;
        pos = _pos;
    }
}

class PositionSystem : System{
    static void c_update(int entity) {
        writeln("in c_update in PositionSystem", "");
        PositionComponent* p = &world.position[entity];
        writeln("after get in PositionSystem", (*p).id);
        p.pos[0] = round(p.pos[0]);
        p.pos[1] = round(p.pos[1]);
        writeln("after round in PositionSystem");
    }
}

class Player : Entity {
    this() {
        auto mask = COMPONENT_EVENT
                   |COMPONENT_SPRITE
                   |COMPONENT_PHYSICS
                   |COMPONENT_POSITION;
        super(mask);
        this.set_component!"position"(PositionComponent(this.id, [100.1,100.1]));
    }
}

void main(){
    World world = World();
    writeln(world.mask[0]);
    Entity.provide(&world);
    System.provide(&world);
    world.systems[0] = &System.update!PositionSystem;
    auto player = new Player();
    writeln(player.get_component!"position".pos);
    world.update();
    writeln(player.get_component!"position".pos);
    writeln(world.mask[0]);
}
