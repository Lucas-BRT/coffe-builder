#version 330 core

in vec3 vPos;
uniform vec4 color;
out vec4 FragColor;

void main() {
    vec3 n = normalize(cross(dFdx(vPos), dFdy(vPos)));
    vec3 light = normalize(vec3(0.4, 1.0, 0.6));
    float shade = 0.45 + 0.55 * abs(dot(n, light));
    FragColor = vec4(color * shade);
}
