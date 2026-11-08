#version 330 core

in vec3 world_position;
uniform vec3 light_position;
uniform float shadow_far_plane;

void main() {
    gl_FragDepth = length(world_position - light_position) / shadow_far_plane;
}
