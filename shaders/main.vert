#version 330 core

layout(location = 0) in vec3 aPos;
layout(location = 1) in vec2 aTexCoord;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
out vec3 vPos;
out vec2 vTexCoord;

void main() {
    vec4 world = model * vec4(aPos, 1.0);
    vPos = vec3(world);
    vTexCoord = aTexCoord;
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
