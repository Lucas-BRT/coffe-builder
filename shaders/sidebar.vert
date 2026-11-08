#version 330 core

layout(location = 0) in vec2 aPos;
layout(location = 1) in vec3 aColor;
uniform vec2 viewport_size;
out vec3 color;

void main() {
    vec2 ndc = vec2(2.0 * aPos.x / viewport_size.x - 1.0,
                   1.0 - 2.0 * aPos.y / viewport_size.y);
    gl_Position = vec4(ndc, 0.0, 1.0);
    color = aColor;
}
