#version 330 core

layout(location = 0) in vec3 aPos;
uniform mat4 model;
uniform mat4 light_space_matrix;
out vec3 world_position;

void main() {
    vec4 world = model * vec4(aPos, 1.0);
    world_position = world.xyz;
    gl_Position = light_space_matrix * world;
}
