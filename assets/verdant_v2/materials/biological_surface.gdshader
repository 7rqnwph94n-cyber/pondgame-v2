shader_type spatial;
render_mode cull_disabled;

uniform vec4 base_colour : source_color = vec4(0.09, 0.29, 0.31, 1.0);
uniform float family = 0.0; // 0 shell, 1 chalk/ceramic, 2 silica, 3 soft tissue, 4 amber/resin
uniform float base_roughness = 0.48;
varying vec3 local_point;

float hash(vec3 p) {
	p = fract(p * 0.1031);
	p += dot(p, p.yzx + 33.33);
	return fract((p.x + p.y) * p.z);
}
float noise(vec3 p) {
	vec3 i = floor(p);
	vec3 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(mix(hash(i), hash(i + vec3(1,0,0)), f.x), mix(hash(i + vec3(0,1,0)), hash(i + vec3(1,1,0)), f.x), f.y),
		mix(mix(hash(i + vec3(0,0,1)), hash(i + vec3(1,0,1)), f.x), mix(hash(i + vec3(0,1,1)), hash(i + vec3(1,1,1)), f.x), f.y), f.z);
}
void vertex() {
	local_point = VERTEX;
}
void fragment() {
	float broad = noise(local_point * 2.4);
	float grain = noise(local_point * 32.0);
	float bands = sin(local_point.y * 24.0 + broad * 5.0) * 0.5 + 0.5;
	float pores = smoothstep(0.70, 0.91, noise(local_point * 18.0));
	vec3 tone = base_colour.rgb;
	float variation = 0.84 + broad * 0.26;
	float roughness = base_roughness;
	if (family < 0.5) {
		// Low-contrast accretion, waxy body and pale rim, not painted stripes.
		variation *= 0.90 + bands * 0.14;
		tone = mix(tone, tone * vec3(0.80, 1.11, 1.07), broad * 0.35);
		roughness += (grain - 0.5) * 0.14;
	} else if (family < 1.5) {
		variation *= 1.0 - pores * 0.32;
		tone = mix(tone, tone * vec3(0.80, 0.82, 0.77), (1.0-broad) * 0.35);
		roughness = 0.80 + grain * 0.13;
	} else if (family < 2.5) {
		variation = 0.85 + broad * 0.20;
		roughness = 0.19 + grain * 0.09;
		METALLIC = 0.03;
	} else if (family < 3.5) {
		variation *= 0.91 + bands * 0.11;
		roughness = 0.55 + broad * 0.18;
	} else {
		variation *= 0.90 + broad * 0.12;
		roughness = 0.29 + grain * 0.12;
	}
	// Tiny view-space surface relief keeps pores and wax grain from reading as paint.
	float relief = family > 0.5 && family < 1.5 ? -pores * 0.012 : (grain - 0.5) * 0.003;
	vec3 dx = dFdx(VERTEX);
	vec3 dy = dFdy(VERTEX);
	vec3 r1 = cross(dy, NORMAL);
	vec3 r2 = cross(NORMAL, dx);
	float determinant = dot(dx, r1);
	if (abs(determinant) > 0.00000001) {
		vec3 gradient = r1 * dFdx(relief) + r2 * dFdy(relief);
		NORMAL = normalize(abs(determinant) * NORMAL - sign(determinant) * gradient);
	}
	ALBEDO = tone * variation;
	ROUGHNESS = clamp(roughness, 0.12, 0.98);
	SPECULAR = family > 1.5 && family < 2.5 ? 0.65 : 0.35;
	// Opaque on purpose: sorting, emission and work-state animation are separate concerns.
}
