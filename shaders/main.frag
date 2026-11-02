#version 330 core

in vec3 vPos;
uniform vec4 color;
out vec4 FragColor;

in vec2 vTexCoord;
uniform sampler2D tex;
uniform bool useTexture;

void main() {
    vec3 n = normalize(cross(dFdx(vPos), dFdy(vPos)));
    vec3 light = normalize(vec3(0.4, 1.0, 0.6));
    float shade = 0.45 + 0.55 * abs(dot(n, light));
    vec4 base = useTexture ? texture(tex, vTexCoord) * color : color;
    FragColor = vec4(base.rgb * shade, base.a);
}
