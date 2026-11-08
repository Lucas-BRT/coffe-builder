#version 330 core

in vec3 vPos;
uniform vec4 color;
uniform bool grid_enabled;
uniform bool emissive;
uniform bool self_shadow_enabled;
uniform vec3 light_position;
uniform vec3 light_color;
uniform vec3 camera_position;
uniform samplerCube shadow_map;
uniform float shadow_far_plane;
out vec4 FragColor;

in vec2 vTexCoord;
uniform sampler2D tex;
uniform bool useTexture;

void main() {
    if (emissive) {
        FragColor = color;
        return;
    }

    vec3 n = normalize(cross(dFdx(vPos), dFdy(vPos)));
    vec3 to_light = light_position - vPos;
    float distance_to_light = length(to_light);
    vec3 light_direction = to_light / max(distance_to_light, 0.0001);
    float diffuse = max(dot(n, light_direction), 0.0);
    float attenuation =
        1.0 / (1.0 + 0.12 * distance_to_light + 0.035 * distance_to_light * distance_to_light);
    vec4 base = useTexture ? texture(tex, vTexCoord) * color : color;
    vec3 base_color = base.rgb;

    if (grid_enabled && abs(n.y) > 0.95) {
        vec2 distance_to_line = abs(fract(vPos.xz - 0.5) - 0.5);
        vec2 line_width = fwidth(vPos.xz);
        float grid_line = 1.0 - min(
                    smoothstep(0.0, line_width.x, distance_to_line.x),
                    smoothstep(0.0, line_width.y, distance_to_line.y)
                );
        base_color = mix(base_color, vec3(0.25, 0.18, 0.12), grid_line);
    }

    vec3 view_direction = normalize(camera_position - vPos);
    vec3 reflected_light = reflect(-light_direction, n);
    float specular = diffuse > 0.0
        ? pow(max(dot(view_direction, reflected_light), 0.0), 32.0)
        : 0.0;
    float shadow = 0.0;
    if (self_shadow_enabled && diffuse > 0.0) {
        float closest_depth = texture(shadow_map, -to_light).r * shadow_far_plane;
        shadow = distance_to_light - 0.05 > closest_depth ? 1.0 : 0.0;
    }
    vec3 ambient = base_color * 0.2;
    vec3 direct = (base_color * diffuse + vec3(specular * 0.4))
        * light_color * attenuation * 3.0 * (1.0 - shadow);
    FragColor = vec4(ambient + direct, base.a);
}
